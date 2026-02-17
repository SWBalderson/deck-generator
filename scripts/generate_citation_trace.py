#!/usr/bin/env python3
"""Generate citation trace mapping bullets to source excerpts."""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")


def normalise_words(text: str) -> List[str]:
    words = [w.lower() for w in WORD_RE.findall(text or '')]
    stop = {
        'the', 'and', 'for', 'with', 'from', 'that', 'this', 'will', 'have', 'has', 'are', 'was', 'were',
        'into', 'their', 'about', 'where', 'which', 'using', 'through', 'more', 'than', 'into'
    }
    return [w for w in words if w not in stop]


def split_fragments(text: str) -> List[str]:
    parts = re.split(r'(?<=[.!?])\s+|\n+', text or '')
    return [p.strip() for p in parts if p and p.strip()]


def source_lookup(contents: Dict[str, dict]) -> Dict[str, dict]:
    idx = {}
    for path, doc in contents.items():
        idx[path] = doc
        idx[Path(path).name] = doc
        filename = doc.get('filename')
        if isinstance(filename, str):
            idx[filename] = doc
    return idx


def extract_source_text(doc: dict) -> str:
    if not doc:
        return ''
    for key in ['content', 'text', 'markdown']:
        value = doc.get(key)
        if isinstance(value, str) and value.strip():
            return value
    data = doc.get('data')
    if data is not None:
        return json.dumps(data, ensure_ascii=False)
    return ''


def best_excerpt(query: str, fragments: List[str]) -> Tuple[str, int]:
    q_words = set(normalise_words(query))
    if not q_words or not fragments:
        return '', 0

    best = ('', 0)
    for frag in fragments:
        score = 0
        low = frag.lower()
        for token in q_words:
            if token in low:
                score += 1
        if score > best[1]:
            best = (frag, score)
    return best


def main():
    parser = argparse.ArgumentParser(description='Generate citation trace for analysis bullets')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--content', required=True, help='Path to content.json from ingestion')
    parser.add_argument('--output', required=True, help='Output citation trace JSON path')
    parser.add_argument('--min-score', type=int, default=2, help='Minimum keyword overlap score')
    args = parser.parse_args()

    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    with open(args.content, 'r', encoding='utf-8') as f:
        content = json.load(f)

    idx = source_lookup(content.get('contents', {}))
    trace = {
        'title': analysis.get('title', 'Presentation'),
        'analysis_file': args.analysis,
        'content_file': args.content,
        'slides': [],
    }

    for s_idx, slide in enumerate(analysis.get('slides', []), start=1):
        slide_source = slide.get('source')
        visual = slide.get('visual', {}) if isinstance(slide.get('visual'), dict) else {}
        source_file = visual.get('source_file') or slide_source
        doc = idx.get(source_file, {})
        source_text = extract_source_text(doc)
        fragments = split_fragments(source_text)

        bullet_traces = []
        for b_idx, bullet in enumerate(slide.get('bullets', []) or [], start=1):
            main = str(bullet.get('main', '')).strip()
            detail = str(bullet.get('detail', '')).strip()
            query = f'{main} {detail}'.strip()
            excerpt, score = best_excerpt(query, fragments)
            bullet_traces.append({
                'bullet_index': b_idx,
                'bullet_main': main,
                'query': query,
                'source_file': source_file,
                'match_score': score,
                'excerpt': excerpt if score >= args.min_score else '',
                'matched': bool(excerpt and score >= args.min_score),
            })

        trace['slides'].append({
            'slide_index': s_idx,
            'title': slide.get('title', ''),
            'source_file': source_file,
            'citations': bullet_traces,
        })

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    matched = sum(
        1
        for slide in trace['slides']
        for c in slide.get('citations', [])
        if c.get('matched')
    )
    total = sum(len(slide.get('citations', [])) for slide in trace['slides'])
    print(f'✓ Citation trace generated: {output_path}')
    print(f'  Matched citations: {matched}/{total}')


if __name__ == '__main__':
    main()
