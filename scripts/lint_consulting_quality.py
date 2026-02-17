#!/usr/bin/env python3
"""Consulting quality linter with scoring and ranked remediation."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


ACTION_VERB_RE = re.compile(
    r"\b(is|are|can|should|must|will|improves?|reduces?|enables?|drives?|shows?|demonstrates?|increases?|decreases?|delivers?|supports?|creates?|limits?)\b",
    re.IGNORECASE,
)
OUTCOME_RE = re.compile(
    r"\b(therefore|so|result|impact|outcome|drives|enables|reduces|increases|improves|supports)\b",
    re.IGNORECASE,
)
RECOMMEND_RE = re.compile(r"\b(should|recommend|next step|must|priority|action)\b", re.IGNORECASE)
NUMERIC_RE = re.compile(r"\d|%|£|\$|€")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")


def normalise_words(text: str) -> List[str]:
    stop = {
        'the', 'and', 'for', 'with', 'from', 'that', 'this', 'will', 'have', 'has', 'are', 'was', 'were',
        'into', 'their', 'about', 'where', 'which', 'using', 'through', 'more', 'than', 'into', 'over',
        'each', 'across', 'while', 'when', 'under', 'between', 'after', 'before'
    }
    return [w.lower() for w in WORD_RE.findall(text or '') if w.lower() not in stop]


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def parse_content_index(content_payload: dict) -> Dict[str, dict]:
    idx = {}
    for path, item in content_payload.get('contents', {}).items():
        idx[path] = item
        idx[Path(path).name] = item
        filename = item.get('filename')
        if isinstance(filename, str):
            idx[filename] = item
    return idx


def issue(issues: List[dict], category: str, severity: str, message: str, suggestion: str, impact: int, slide_index=None):
    issues.append({
        'category': category,
        'severity': severity,
        'message': message,
        'suggestion': suggestion,
        'impact': impact,
        'slide_index': slide_index,
    })


def score_from_issues(issues: List[dict]) -> Tuple[int, Dict[str, int], Dict[str, int]]:
    category_weights = {
        'action_titles': 25,
        'pyramid': 20,
        'mece': 20,
        'minimalist': 15,
        'data_evidence': 20,
    }
    penalties = defaultdict(int)
    for item in issues:
        if item['severity'] == 'info':
            continue
        penalties[item['category']] += max(0, int(item.get('impact', 0)))

    category_scores = {}
    for key, weight in category_weights.items():
        category_scores[key] = max(0, weight - min(weight, penalties.get(key, 0)))

    overall = sum(category_scores.values())
    return overall, category_scores, dict(penalties)


def rank_fixes(issues: List[dict]) -> List[dict]:
    grouped = {}
    for item in issues:
        suggestion = item.get('suggestion') or 'Address reported issue.'
        grouped.setdefault(suggestion, {'suggestion': suggestion, 'impact': 0, 'occurrences': 0})
        grouped[suggestion]['impact'] += int(item.get('impact', 0))
        grouped[suggestion]['occurrences'] += 1
    ranked = sorted(grouped.values(), key=lambda x: (-x['impact'], -x['occurrences'], x['suggestion']))
    return ranked[:5]


def lint_analysis(analysis: dict, content_index: Dict[str, dict], citation_trace: dict, min_citation_match: float) -> dict:
    slides = analysis.get('slides', [])
    issues = []

    substantive = [
        (idx + 1, s)
        for idx, s in enumerate(slides)
        if s.get('layout') not in {'title', 'end'}
    ]

    # Action title + minimalist checks + data checks (per slide)
    slide_scores = []
    slide_keywords = {}
    section_groups = []
    current_section = {'section_slide': None, 'slides': []}

    for idx, slide in enumerate(slides, start=1):
        layout = slide.get('layout', 'content')
        title = (slide.get('title') or '').strip()
        bullets = slide.get('bullets', []) or []
        source = (slide.get('source') or '').strip()
        visual = slide.get('visual', {}) if isinstance(slide.get('visual'), dict) else {}
        vtype = visual.get('type', 'none')

        if layout == 'section':
            if current_section['section_slide'] or current_section['slides']:
                section_groups.append(current_section)
            current_section = {'section_slide': idx, 'slides': []}
        elif layout not in {'title', 'end'}:
            current_section['slides'].append(idx)

        if layout not in {'title', 'end'}:
            if title and not title.endswith('.'):
                issue(
                    issues,
                    'action_titles',
                    'warn',
                    f'slides[{idx}] title should end with a period to read as a claim.',
                    'Rewrite the title as a complete conclusion sentence ending with a period.',
                    3,
                    idx,
                )
            if title and not ACTION_VERB_RE.search(title):
                issue(
                    issues,
                    'action_titles',
                    'warn',
                    f'slides[{idx}] title lacks a decisive action verb.',
                    'Use a verb-led action title (for example: improves, reduces, enables, demonstrates).',
                    5,
                    idx,
                )
            if title and len(title.split()) <= 4 and not ACTION_VERB_RE.search(title):
                issue(
                    issues,
                    'action_titles',
                    'warn',
                    f'slides[{idx}] title appears topic-like rather than insight-led.',
                    'Replace short topic labels with an explicit takeaway statement.',
                    4,
                    idx,
                )
            if title and not (OUTCOME_RE.search(title) or NUMERIC_RE.search(title)):
                issue(
                    issues,
                    'action_titles',
                    'info',
                    f'slides[{idx}] title could include a clearer implication signal.',
                    'Add implication language (impact/result) or a quantified outcome where possible.',
                    1,
                    idx,
                )

        if layout in {'content', 'two-col'}:
            if not (3 <= len(bullets) <= 5):
                issue(
                    issues,
                    'minimalist',
                    'warn',
                    f'slides[{idx}] has {len(bullets)} bullets; consulting norm is 3-5.',
                    'Reduce or expand bullet count to 3-5 high-signal points.',
                    4,
                    idx,
                )

            total_words = len(title.split()) + sum(
                len((b.get('main', '') + ' ' + b.get('detail', '')).split())
                for b in bullets if isinstance(b, dict)
            )
            if total_words > 120:
                issue(
                    issues,
                    'minimalist',
                    'warn',
                    f'slides[{idx}] appears text-dense ({total_words} words).',
                    'Trim bullet text and move detail into speaker notes.',
                    5,
                    idx,
                )

            for b_i, bullet in enumerate(bullets, start=1):
                words = len((bullet.get('main', '') + ' ' + bullet.get('detail', '')).split())
                if words > 24:
                    issue(
                        issues,
                        'minimalist',
                        'warn',
                        f'slides[{idx}] bullet {b_i} is long ({words} words).',
                        'Keep bullets concise (approximately <=24 words) and move detail to notes.',
                        2,
                        idx,
                    )

        if title and len(title) > 110:
            issue(
                issues,
                'minimalist',
                'warn',
                f'slides[{idx}] title is long ({len(title)} chars).',
                'Shorten the title to improve readability and whitespace.',
                3,
                idx,
            )

        if layout in {'content', 'two-col', 'chart-full'} and not source:
            issue(
                issues,
                'data_evidence',
                'blocking',
                f'slides[{idx}] is missing a source citation.',
                'Add a clear source reference for each evidence-led slide.',
                6,
                idx,
            )

        if layout == 'chart-full':
            required = ['data_file', 'source_file', 'x_key', 'y_key']
            for field in required:
                value = visual.get(field) or slide.get(field)
                if not value:
                    issue(
                        issues,
                        'data_evidence',
                        'blocking',
                        f'slides[{idx}] chart is missing `{field}` mapping metadata.',
                        'Provide complete chart mapping fields (`data_file`, `source_file`, `x_key`, `y_key`).',
                        7,
                        idx,
                    )
            if not slide.get('insight'):
                issue(
                    issues,
                    'data_evidence',
                    'warn',
                    f'slides[{idx}] chart slide has no explicit insight callout.',
                    'Add an `insight` field summarising the key takeaway from the chart.',
                    4,
                    idx,
                )

        if NUMERIC_RE.search(title):
            evidence_text = ' '.join(
                (str(b.get('main', '')) + ' ' + str(b.get('detail', '')))
                for b in bullets if isinstance(b, dict)
            )
            has_numeric_support = bool(NUMERIC_RE.search(evidence_text)) or layout == 'chart-full'
            if not has_numeric_support:
                issue(
                    issues,
                    'data_evidence',
                    'warn',
                    f'slides[{idx}] title contains a numeric claim without numeric support in body evidence.',
                    'Include supporting numeric evidence in bullets or chart data.',
                    4,
                    idx,
                )

        # keyword set for MECE overlap
        text_blob = title + ' ' + ' '.join(
            (str(b.get('main', '')) + ' ' + str(b.get('detail', '')))
            for b in bullets if isinstance(b, dict)
        )
        slide_keywords[idx] = set(normalise_words(text_blob))

    if current_section['section_slide'] or current_section['slides']:
        section_groups.append(current_section)

    # Pyramid checks
    if substantive:
        first_sub_idx = substantive[0][0]
        if first_sub_idx > 3:
            issue(
                issues,
                'pyramid',
                'warn',
                'Deck introduces substantive conclusions too late.',
                'Move an executive conclusion slide to position 2 or 3.',
                6,
                first_sub_idx,
            )

        last_idx, last_slide = substantive[-1]
        last_text = (last_slide.get('title', '') + ' ' + ' '.join(
            (str(b.get('main', '')) + ' ' + str(b.get('detail', '')))
            for b in (last_slide.get('bullets', []) or []) if isinstance(b, dict)
        ))
        if not RECOMMEND_RE.search(last_text):
            issue(
                issues,
                'pyramid',
                'warn',
                f'slides[{last_idx}] does not clearly state recommendation/next steps.',
                'Close with explicit recommendations, priorities, or next-step actions.',
                5,
                last_idx,
            )

    for idx, slide in substantive:
        layout = slide.get('layout', 'content')
        if layout not in {'content', 'two-col'}:
            continue
        bullets = slide.get('bullets', []) or []
        if not bullets:
            continue

        first = bullets[0] if isinstance(bullets[0], dict) else {}
        first_text = str(first.get('main', '')) + ' ' + str(first.get('detail', ''))
        if not first.get('detail'):
            issue(
                issues,
                'pyramid',
                'warn',
                f'slides[{idx}] first bullet lacks explicit supporting evidence detail.',
                'Make the first bullet an evidence-backed reason for the headline claim.',
                3,
                idx,
            )
        if not (NUMERIC_RE.search(first_text) or ACTION_VERB_RE.search(first_text)):
            issue(
                issues,
                'pyramid',
                'info',
                f'slides[{idx}] first bullet could more directly prove the headline.',
                'Use a stronger evidence statement or quantified proof in the first bullet.',
                1,
                idx,
            )

    # MECE checks
    for group in section_groups:
        if group['section_slide'] and len(group['slides']) < 2:
            issue(
                issues,
                'mece',
                'warn',
                f'Section at slide {group["section_slide"]} has only one supporting slide.',
                'Use at least two supporting slides per section or remove the divider.',
                4,
                group['section_slide'],
            )

    substantive_ids = [idx for idx, _ in substantive]
    for i in range(len(substantive_ids)):
        for j in range(i + 1, len(substantive_ids)):
            a = substantive_ids[i]
            b = substantive_ids[j]
            overlap = jaccard(slide_keywords.get(a, set()), slide_keywords.get(b, set()))
            if overlap >= 0.55:
                issue(
                    issues,
                    'mece',
                    'warn',
                    f'Slides {a} and {b} appear topically overlapping (MECE risk).',
                    'Differentiate slide scopes to avoid duplication and improve clean decomposition.',
                    6,
                    a,
                )

    for idx, slide in substantive:
        bullets = slide.get('bullets', []) or []
        stems = []
        for bullet in bullets:
            if not isinstance(bullet, dict):
                continue
            main = str(bullet.get('main', '')).strip().lower()
            if not main:
                continue
            stems.append(' '.join(main.split()[:2]))
        if len(stems) != len(set(stems)) and stems:
            issue(
                issues,
                'mece',
                'warn',
                f'slides[{idx}] bullets appear overlapping or repetitive.',
                'Rewrite bullets to be mutually exclusive and collectively complete.',
                4,
                idx,
            )

    # Citation trace consistency (optional)
    if citation_trace and isinstance(citation_trace, dict):
        slide_traces = citation_trace.get('slides', [])
        if slide_traces:
            matched = 0
            total = 0
            for slide_entry in slide_traces:
                for c in slide_entry.get('citations', []) or []:
                    total += 1
                    if c.get('matched'):
                        matched += 1
            if total > 0:
                ratio = matched / total
                if ratio < min_citation_match:
                    issue(
                        issues,
                        'data_evidence',
                        'warn',
                        f'Citation match ratio is low ({ratio:.0%}).',
                        'Improve source alignment for bullets or refine citation trace thresholds.',
                        5,
                    )

    # slide scores
    by_slide = defaultdict(int)
    for item in issues:
        idx = item.get('slide_index')
        if idx:
            by_slide[idx] += int(item.get('impact', 0))
    for idx, slide in enumerate(slides, start=1):
        slide_scores.append({
            'slide_index': idx,
            'title': slide.get('title', ''),
            'score': max(0, 100 - min(100, by_slide.get(idx, 0))),
            'issues': [
                x for x in issues if x.get('slide_index') == idx
            ],
        })

    overall, category_scores, category_penalties = score_from_issues(issues)
    blocking = [x for x in issues if x.get('severity') == 'blocking']

    if overall >= 90:
        band = 'Excellent'
    elif overall >= 75:
        band = 'Good'
    elif overall >= 60:
        band = 'Needs refinement'
    else:
        band = 'Rework recommended'

    return {
        'overall_score': overall,
        'overall_band': band,
        'category_scores': category_scores,
        'category_penalties': category_penalties,
        'blocking_issues': blocking,
        'warnings': [x for x in issues if x.get('severity') != 'blocking'],
        'slide_findings': slide_scores,
        'recommended_fixes': rank_fixes(issues),
    }


def print_report(report: dict):
    print(f"Consulting quality score: {report['overall_score']}/100 ({report['overall_band']})")
    print('Category scores:')
    for key, value in report['category_scores'].items():
        print(f'  - {key}: {value}')

    blocking = report.get('blocking_issues', [])
    warnings = report.get('warnings', [])
    print(f"Blocking issues: {len(blocking)}")
    print(f"Warnings/info: {len(warnings)}")

    if report.get('recommended_fixes'):
        print('Top fixes:')
        for fix in report['recommended_fixes']:
            print(f"  - {fix['suggestion']} (impact {fix['impact']}, occurrences {fix['occurrences']})")


def main():
    parser = argparse.ArgumentParser(description='Lint consulting-quality principles in analysis output')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--content', help='Optional path to content.json for evidence checks')
    parser.add_argument('--citation-trace', help='Optional citation-trace.json path')
    parser.add_argument('--report-out', help='Optional output path for JSON report')
    parser.add_argument('--strict', action='store_true', help='Fail when blocking issues exist or score < threshold')
    parser.add_argument('--threshold', type=int, default=70, help='Strict mode score threshold (default: 70)')
    parser.add_argument('--min-citation-match', type=float, default=0.6, help='Citation ratio threshold when trace is provided')
    args = parser.parse_args()

    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    content_index = {}
    if args.content:
        with open(args.content, 'r', encoding='utf-8') as f:
            content_payload = json.load(f)
        content_index = parse_content_index(content_payload)

    citation_trace = {}
    if args.citation_trace:
        path = Path(args.citation_trace)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                citation_trace = json.load(f)

    report = lint_analysis(analysis, content_index, citation_trace, args.min_citation_match)

    if args.report_out:
        out_path = Path(args.report_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    print_report(report)

    if args.strict:
        if report['blocking_issues']:
            print('✗ Consulting lint failed: blocking issues detected.', file=sys.stderr)
            return 1
        if report['overall_score'] < args.threshold:
            print(
                f"✗ Consulting lint failed: score {report['overall_score']} below threshold {args.threshold}.",
                file=sys.stderr,
            )
            return 1

    print('✓ Consulting lint completed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
