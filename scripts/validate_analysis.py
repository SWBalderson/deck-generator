#!/usr/bin/env python3
"""Validate analysis.json before deck build/export steps."""

import argparse
import json
import sys
from typing import List


VALID_LAYOUTS = {'title', 'section', 'content', 'two-col', 'chart-full', 'end'}
VALID_VISUAL_TYPES = {'chart', 'image', 'none'}


def validate_analysis_payload(payload: dict) -> List[str]:
    """Return validation errors for analysis payload."""
    errors = []

    if not isinstance(payload, dict):
        return ['Analysis must be a JSON object.']

    title = payload.get('title')
    if not isinstance(title, str) or not title.strip():
        errors.append('Top-level "title" is required and must be a non-empty string.')

    slides = payload.get('slides')
    if not isinstance(slides, list) or not slides:
        errors.append('Top-level "slides" is required and must be a non-empty array.')
        return errors

    for idx, slide in enumerate(slides, start=1):
        path = f'slides[{idx}]'
        if not isinstance(slide, dict):
            errors.append(f'{path} must be an object.')
            continue

        layout = slide.get('layout')
        if layout not in VALID_LAYOUTS:
            errors.append(f'{path}.layout must be one of: {", ".join(sorted(VALID_LAYOUTS))}.')

        title_val = slide.get('title')
        if not isinstance(title_val, str) or not title_val.strip():
            errors.append(f'{path}.title must be a non-empty string.')

        visual = slide.get('visual', {})
        if visual and not isinstance(visual, dict):
            errors.append(f'{path}.visual must be an object when present.')
            continue

        vtype = visual.get('type') if isinstance(visual, dict) else None
        if vtype and vtype not in VALID_VISUAL_TYPES:
            errors.append(f'{path}.visual.type must be one of: chart, image, none.')

        if vtype == 'chart':
            data_file = visual.get('data_file') or slide.get('data_file')
            if not isinstance(data_file, str) or not data_file.strip():
                errors.append(f'{path} chart visual requires visual.data_file or slide.data_file.')
            chart_type = visual.get('chart_type')
            if not isinstance(chart_type, str) or not chart_type.strip():
                errors.append(f'{path} chart visual requires visual.chart_type.')

        if vtype == 'image':
            filename = visual.get('filename')
            if not isinstance(filename, str) or not filename.strip():
                errors.append(f'{path} image visual requires visual.filename.')

    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate analysis.json structure')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    args = parser.parse_args()

    with open(args.analysis, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    errors = validate_analysis_payload(payload)
    if errors:
        print('✗ Analysis validation failed:', file=sys.stderr)
        for err in errors:
            print(f'  - {err}', file=sys.stderr)
        return 1

    print(f'✓ Analysis validation passed: {args.analysis}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
