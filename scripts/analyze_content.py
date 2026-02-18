#!/usr/bin/env python3
"""
Prepare content for LLM analysis.
"""

import argparse
import json


AUDIENCE_GUIDANCE = {
    'board': (
        'Audience mode: board. Prioritise strategic implications, risk, governance decisions, and concise evidence for trustees/governors.'
    ),
    'staff': (
        'Audience mode: staff. Prioritise implementation detail, practical classroom/operational implications, and clear ownership of actions.'
    ),
    'parents': (
        'Audience mode: parents. Prioritise learner outcomes, wellbeing, transparency, and plain-language explanation of decisions and impact.'
    ),
    'mixed': (
        'Audience mode: mixed. Balance strategic clarity with practical implications, avoiding jargon while retaining evidence-led recommendations.'
    ),
}


ANALYSIS_INSTRUCTION = """
Analyse these documents and create a presentation structure.

Create 6-10 slides covering:
1. Title slide
2. Executive Summary (key message upfront — the pyramid principle: lead with the answer)
3-7. Main content slides (one message per slide)
8. Conclusions/Next Steps (explicit recommendations or actions)
9. Thank You (optional)

For each slide, provide this JSON structure:
{
    "layout": "title|section|content|two-col|chart-full|end",
    "title": "Action title — a complete sentence stating the slide's conclusion, ending with a period.",
    "subtitle": "Optional subtitle",
    "bullets": [
        {"main": "Bold key phrase", "detail": "Supporting explanation"},
        ...
    ],
    "visual": {
        "type": "chart|image|none",
        "chart_type": "bar|line|pie|waterfall|none",
        "data_file": "chart_N.json (if chart; output config filename)",
        "source_file": "source filename containing chart data (if chart)",
        "x_key": "column/key name for x-axis (if chart)",
        "y_key": "column/key name for y-axis (if chart)",
        "series_key": "optional group/series column (if chart)",
        "filename": "slide-NN.png (if image)"
    },
    "insight": "One-sentence takeaway from the chart (chart slides only)",
    "source": "Source citation (required for every content, two-col, and chart-full slide)"
}

## Presentation Principles (must follow)

1. ACTION TITLES: Every content slide title must be a complete sentence containing a
   decisive verb (improves, reduces, enables, drives, demonstrates, etc.) and ending
   with a period. The title IS the slide's conclusion — not a topic label.
   Bad:  "Revenue Overview"
   Good: "Revenue grew 18% year-on-year, driven by new product lines."

2. PYRAMID PRINCIPLE: Lead with the answer. Place the executive summary at position 2.
   Within each slide, make the first bullet the strongest evidence for the headline claim.
   Close the deck with explicit recommendations or next steps.

3. MECE: Slides must be Mutually Exclusive and Collectively Exhaustive. Each slide
   covers a distinct aspect of the argument. No two slides should substantially overlap.
   Within a slide, bullets should not repeat each other.

4. MINIMALIST DESIGN: 3-5 bullet points per content slide. Keep each bullet concise
   (roughly 24 words or fewer). Total slide word count should stay below 120 words.
   Move supporting detail into the "detail" field of the bullet or into speaker notes.

5. DATA EVIDENCE: Every content, two-col, and chart-full slide must cite its source.
   Chart slides must map to real data with complete metadata (source_file, x_key, y_key,
   data_file). If the title contains a number, the body must contain supporting numerics.

## Additional Guidelines

- Include data visualisations where tabular data exists in the source documents
- When proposing a chart, map it to concrete source fields (`source_file`, `x_key`, `y_key`)
- Bold the key phrase in each bullet's "main" field
- Quantify claims wherever the source data permits
"""


def prepare_analysis_request(content_path: str, output_path: str, audience: str = 'board') -> None:
    """Build analysis_request.json from content. Callable from pipeline or CLI."""
    with open(content_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    analysis_request = {
        'documents': content,
        'audience_mode': audience,
        'instruction': ANALYSIS_INSTRUCTION + "\n\n" + AUDIENCE_GUIDANCE.get(audience, AUDIENCE_GUIDANCE['mixed']),
    }

    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_request, f, indent=2)

    print(f"✓ Analysis request saved: {output_path}")
    print("Pass this JSON to LLM for slide structure generation")


def main():
    parser = argparse.ArgumentParser(description='Prepare content analysis')
    parser.add_argument('--content', required=True, help='Path to content.json')
    parser.add_argument('--output', required=True, help='Path to output analysis_request.json')
    parser.add_argument(
        '--audience',
        default='board',
        choices=sorted(AUDIENCE_GUIDANCE.keys()),
        help='Audience mode to tune tone and detail (default: board)',
    )
    args = parser.parse_args()
    prepare_analysis_request(args.content, args.output, args.audience)


if __name__ == '__main__':
    main()
