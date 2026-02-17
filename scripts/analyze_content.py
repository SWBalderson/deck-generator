#!/usr/bin/env python3
"""
Prepare content for LLM analysis.
"""

import argparse
import json


def main():
    parser = argparse.ArgumentParser(description='Prepare content analysis')
    parser.add_argument('--content', required=True, help='Path to content.json')
    parser.add_argument('--output', required=True, help='Path to output analysis_request.json')
    args = parser.parse_args()
    
    with open(args.content, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Prepare request for LLM
    analysis_request = {
        'documents': content,
        'instruction': """
        Analyze these documents and create a presentation structure.
        
        Create 6-10 slides covering:
        1. Title slide
        2. Executive Summary (key message upfront)
        3-7. Main content slides (one message per slide)
        8. Conclusions/Next Steps
        9. Thank You (optional)
        
        For each slide, provide this structure:
        {
            "layout": "title|section|content|two-col|chart-full|end",
            "title": "Action title - complete sentence stating the main message",
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
            "source": "Source citation"
        }
        
        Guidelines:
        - Use action titles (complete sentences with conclusions)
        - One main message per slide
        - 3-5 bullet points per content slide
        - Bold the key phrase in each bullet
        - Include data visualizations where data exists
        - When proposing a chart, map it to concrete source fields (`source_file`, `x_key`, `y_key`)
        - Follow MECE structure for problem decomposition
        - Cite sources from the documents
        """
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(analysis_request, f, indent=2)
    
    print(f"✓ Analysis request saved: {args.output}")
    print("Pass this JSON to LLM for slide structure generation")


if __name__ == '__main__':
    main()
