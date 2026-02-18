#!/usr/bin/env python3
"""Apply slide locks and selective regeneration controls to analysis JSON."""

import argparse
import json
from pathlib import Path
from typing import List, Set

from utils import load_json, save_json


def parse_indexes(values: List[int]) -> Set[int]:
    return {int(v) for v in values if int(v) > 0}


def main():
    parser = argparse.ArgumentParser(description='Apply iterative slide controls')
    parser.add_argument('--base-analysis', required=True, help='Current baseline analysis JSON')
    parser.add_argument('--new-analysis', required=True, help='Newly regenerated analysis JSON')
    parser.add_argument('--output', required=True, help='Merged analysis output path')
    parser.add_argument('--locks-file', default='.temp/slide-locks.json', help='Lock state JSON path')
    parser.add_argument('--lock-slides', nargs='*', type=int, default=[], help='Slide indexes to lock')
    parser.add_argument('--unlock-slides', nargs='*', type=int, default=[], help='Slide indexes to unlock')
    parser.add_argument(
        '--regenerate-only',
        nargs='*',
        type=int,
        default=[],
        help='Only these slide indexes are allowed to change from new analysis',
    )
    args = parser.parse_args()

    base = load_json(Path(args.base_analysis))
    new = load_json(Path(args.new_analysis))

    base_slides = base.get('slides', [])
    new_slides = new.get('slides', [])
    max_len = max(len(base_slides), len(new_slides))

    locks_path = Path(args.locks_file)
    locks_payload = {'locked_slide_indexes': []}
    if locks_path.exists():
        locks_payload = load_json(locks_path)

    locked = set(int(i) for i in locks_payload.get('locked_slide_indexes', []) if int(i) > 0)
    locked |= parse_indexes(args.lock_slides)
    locked -= parse_indexes(args.unlock_slides)

    regenerate_only = parse_indexes(args.regenerate_only)
    merged_slides = []

    for idx in range(1, max_len + 1):
        base_slide = base_slides[idx - 1] if idx <= len(base_slides) else None
        new_slide = new_slides[idx - 1] if idx <= len(new_slides) else None

        if idx in locked and base_slide is not None:
            merged_slides.append(base_slide)
            continue

        if regenerate_only and idx not in regenerate_only and base_slide is not None:
            merged_slides.append(base_slide)
            continue

        if new_slide is not None:
            merged_slides.append(new_slide)
        elif base_slide is not None:
            merged_slides.append(base_slide)

    merged = dict(base)
    for key in ['title', 'subtitle', 'author', 'theme']:
        if key in new:
            merged[key] = new[key]
    merged['slides'] = merged_slides

    save_json(Path(args.output), merged)
    save_json(locks_path, {'locked_slide_indexes': sorted(locked)})

    print(f'✓ Iterative controls applied: {args.output}')
    print(f'  Locked slides: {sorted(locked)}')
    if regenerate_only:
        print(f'  Regenerate only: {sorted(regenerate_only)}')


if __name__ == '__main__':
    main()
