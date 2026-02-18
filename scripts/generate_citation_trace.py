#!/usr/bin/env python3
"""Generate citation trace mapping bullets to source excerpts."""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from utils import (
    build_content_index,
    extract_source_text,
    normalise_words,
    split_fragments,
)


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

    idx = build_content_index(content)
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
