#!/usr/bin/env python3
"""
Build slides.md from template and analysis.
Auto-detects existing images and enables them automatically.
"""

import argparse
import json
import sys
from pathlib import Path
from jinja2 import Template

from validate_analysis import validate_analysis_payload
from lint_slides import lint_analysis as lint_slides_analysis


def check_existing_images(slides: list, output_dir: Path) -> list:
    """Check which images exist and mark them for inclusion."""
    images_dir = output_dir / 'public' / 'images'

    updated_slides = []
    for slide in slides:
        visual = slide.get('visual', {})

        if visual.get('type') == 'image' and visual.get('filename'):
            image_path = images_dir / visual['filename']

            if image_path.exists():
                print(f"  ✓ Found image: {visual['filename']}")
            else:
                print(f"  ⚠ Missing image: {visual['filename']} (will be hidden)")
                visual = visual.copy()
                visual['type'] = 'none'
                slide = slide.copy()
                slide['visual'] = visual

        updated_slides.append(slide)

    return updated_slides


def build(
    analysis_path: str,
    template_path: str,
    output_path: str,
    deck_dir: str = None,
    lint: bool = False,
    lint_strict: bool = False,
    consulting_lint: bool = False,
    consulting_lint_strict: bool = False,
    consulting_lint_threshold: int = 70,
    content_path: str = None,
    citation_trace_path: str = None,
) -> None:
    """Build slides.md from analysis + template. Callable from pipeline or CLI."""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())

    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    errors = validate_analysis_payload(analysis)
    if errors:
        msg = '✗ Analysis validation failed:\n' + '\n'.join(f'  - {e}' for e in errors)
        print(msg, file=sys.stderr)
        raise ValueError(msg)

    if lint:
        warnings = lint_slides_analysis(analysis)
        if warnings:
            print('⚠ Slide lint warnings:')
            for item in warnings:
                print(f'  - {item}')
            if lint_strict:
                raise ValueError('Slide lint failed in strict mode.')

    if consulting_lint:
        from lint_consulting_quality import lint_analysis as lint_cq, print_report
        content_index = {}
        if content_path:
            with open(content_path, 'r', encoding='utf-8') as f:
                from lint_consulting_quality import parse_content_index
                content_index = parse_content_index(json.load(f))

        citation_trace = {}
        if citation_trace_path:
            ct = Path(citation_trace_path)
            if ct.exists():
                with open(ct, 'r', encoding='utf-8') as f:
                    citation_trace = json.load(f)

        report = lint_cq(analysis, content_index, citation_trace, 0.6)
        report_out = Path(output_path).parent / 'consulting-quality-report.json'
        report_out.parent.mkdir(parents=True, exist_ok=True)
        with open(report_out, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_report(report)

        if consulting_lint_strict:
            if report['blocking_issues']:
                raise ValueError('Consulting lint failed: blocking issues detected.')
            if report['overall_score'] < consulting_lint_threshold:
                raise ValueError(
                    f"Consulting lint failed: score {report['overall_score']} below threshold {consulting_lint_threshold}."
                )

    slides = analysis.get('slides', [])

    if deck_dir:
        output_dir = Path(deck_dir)
        print(f"Checking for existing images in {output_dir}/public/images/...")
        slides = check_existing_images(slides, output_dir)
        print()

    rendered = template.render(
        title=analysis.get('title', 'Presentation'),
        subtitle=analysis.get('subtitle', ''),
        author=analysis.get('author', ''),
        slides=slides,
        theme=analysis.get('theme', 'consulting'),
        primary_color='#003366',
        secondary_color='#6699CC',
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, 'w', encoding='utf-8') as f:
        f.write(rendered)

    print(f"✓ Slides built: {output_path}")

    image_count = sum(1 for s in slides if s.get('visual', {}).get('type') == 'image')
    if image_count > 0:
        print(f"✓ {image_count} image(s) enabled in presentation")


def main():
    parser = argparse.ArgumentParser(description='Build slides')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--template', required=True, help='Path to slides.md.jinja2')
    parser.add_argument('--output', required=True, help='Output slides.md path')
    parser.add_argument('--deck-dir', help='Deck directory for image detection (optional)')
    parser.add_argument('--lint', action='store_true', help='Run slide quality lint before rendering')
    parser.add_argument('--lint-strict', action='store_true', help='Fail build on lint warnings (requires --lint)')
    parser.add_argument('--consulting-lint', action='store_true', help='Run consulting quality linter')
    parser.add_argument('--consulting-lint-strict', action='store_true', help='Fail build on consulting-lint score/blocks')
    parser.add_argument('--consulting-lint-threshold', type=int, default=70, help='Consulting lint strict score threshold')
    parser.add_argument('--content', help='Optional content.json path for consulting-lint evidence checks')
    parser.add_argument('--citation-trace', help='Optional citation-trace.json for consulting-lint trace checks')
    args = parser.parse_args()

    try:
        build(
            analysis_path=args.analysis,
            template_path=args.template,
            output_path=args.output,
            deck_dir=args.deck_dir,
            lint=args.lint,
            lint_strict=args.lint_strict,
            consulting_lint=args.consulting_lint,
            consulting_lint_strict=args.consulting_lint_strict,
            consulting_lint_threshold=args.consulting_lint_threshold,
            content_path=args.content,
            citation_trace_path=args.citation_trace,
        )
    except ValueError:
        sys.exit(1)


if __name__ == '__main__':
    main()
