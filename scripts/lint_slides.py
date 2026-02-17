#!/usr/bin/env python3
"""Lint analysis slide quality before deck rendering."""

import argparse
import json
import re
import sys


VERB_RE = re.compile(
    r"\b(is|are|can|should|must|will|improves?|reduces?|enables?|drives?|shows?|demonstrates?|increases?)\b",
    re.IGNORECASE,
)


def lint_analysis(payload: dict):
    warnings = []

    slides = payload.get('slides', [])
    for idx, slide in enumerate(slides, start=1):
        layout = slide.get('layout', 'content')
        title = (slide.get('title') or '').strip()
        source = (slide.get('source') or '').strip()
        bullets = slide.get('bullets', []) or []

        if layout in {'content', 'two-col', 'chart-full'} and not source:
            warnings.append(f'slides[{idx}] missing source citation.')

        if layout in {'content', 'two-col'}:
            if not (3 <= len(bullets) <= 5):
                warnings.append(
                    f'slides[{idx}] has {len(bullets)} bullets; recommended range is 3-5.'
                )

        if title and not title.endswith('.'):
            warnings.append(f'slides[{idx}] title should usually be an action sentence ending in a period.')

        if title and not VERB_RE.search(title):
            warnings.append(f'slides[{idx}] title may be weak; consider a clearer action verb.')

    return warnings


def main():
    parser = argparse.ArgumentParser(description='Lint slide quality in analysis.json')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--strict', action='store_true', help='Return non-zero when warnings exist')
    args = parser.parse_args()

    with open(args.analysis, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    warnings = lint_analysis(payload)
    if not warnings:
        print(f'✓ Slide lint passed: {args.analysis}')
        return 0

    print('⚠ Slide lint warnings:')
    for item in warnings:
        print(f'  - {item}')

    if args.strict:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
