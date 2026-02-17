#!/usr/bin/env python3
"""Generate speaker notes from analysis slides."""

import argparse
import json
from pathlib import Path


def sentence(text: str) -> str:
    text = (text or '').strip()
    if not text:
        return ''
    return text if text.endswith('.') else f'{text}.'


def main():
    parser = argparse.ArgumentParser(description='Generate speaker notes markdown from analysis.json')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--output', required=True, help='Output path for speaker-notes.md')
    parser.add_argument('--style', choices=['concise', 'detailed'], default='concise', help='Note verbosity')
    parser.add_argument('--max-points', type=int, default=3, help='Max bullet points per slide in concise mode')
    args = parser.parse_args()

    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    lines = [
        f"# Speaker Notes - {analysis.get('title', 'Presentation')}",
        '',
        f"Generated from: {args.analysis}",
        '',
    ]

    slides = analysis.get('slides', [])
    for idx, slide in enumerate(slides, start=1):
        title = slide.get('title', f'Slide {idx}')
        lines.append(f'## Slide {idx}: {title}')
        lines.append('')

        custom_notes = slide.get('speaker_notes')
        if isinstance(custom_notes, list) and custom_notes:
            for note in custom_notes:
                lines.append(f'- {sentence(str(note))}')
            lines.append('')
            continue
        if isinstance(custom_notes, str) and custom_notes.strip():
            lines.append(f'- {sentence(custom_notes)}')
            lines.append('')
            continue

        lines.append(f'- Core message: {sentence(title)}')

        bullets = slide.get('bullets', []) or []
        if args.style == 'concise':
            selected = bullets[: max(0, args.max_points)]
        else:
            selected = bullets

        for bullet in selected:
            main = sentence(str(bullet.get('main', '')).strip())
            detail = sentence(str(bullet.get('detail', '')).strip())
            if main and detail:
                lines.append(f'- Evidence: {main} {detail}')
            elif main:
                lines.append(f'- Evidence: {main}')

        if slide.get('source'):
            lines.append(f'- Source cue: Reference {slide["source"]} when challenged on evidence.')

        lines.append('')

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')

    print(f'✓ Speaker notes generated: {output_path}')


if __name__ == '__main__':
    main()
