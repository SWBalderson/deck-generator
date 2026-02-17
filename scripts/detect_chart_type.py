#!/usr/bin/env python3
"""
Auto-detect optimal chart type based on data structure.
"""

import argparse
import json
from typing import Dict, List, Any
from pathlib import Path


def is_time_series(data: List[Dict]) -> bool:
    """Check if data represents time series."""
    if not data or len(data) < 2:
        return False
    
    # Check for date/time columns
    first_row = data[0]
    for key, value in first_row.items():
        if isinstance(value, str):
            # Check for common date patterns
            value_lower = value.lower()
            if any(month in value_lower for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                                        'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                return True
            if 'q1' in value_lower or 'q2' in value_lower or 'q3' in value_lower or 'q4' in value_lower:
                return True
            if '20' in value and len(value) == 4:  # Year
                return True
    
    return False


def is_categorical_comparison(data: List[Dict]) -> bool:
    """Check if data is suitable for bar chart comparison."""
    return len(data) >= 2 and len(data) <= 15


def is_composition(data: List[Dict]) -> bool:
    """Check if data represents parts of a whole."""
    return len(data) >= 2 and len(data) <= 6


def is_waterfall_data(data: List[Dict]) -> bool:
    """Check if data shows incremental changes."""
    if len(data) < 3:
        return False
    
    # Look for columns with positive/negative changes
    numeric_cols = []
    for key in data[0].keys():
        try:
            float(data[0][key])
            numeric_cols.append(key)
        except:
            pass
    
    if len(numeric_cols) >= 1:
        values = [float(row[numeric_cols[0]]) for row in data]
        has_positive = any(v > 0 for v in values)
        has_negative = any(v < 0 for v in values)
        return has_positive and has_negative
    
    return False


def detect_chart_type(data: List[Dict], context: str = "") -> str:
    """
    Auto-detect best chart type based on data structure.
    
    Returns one of: line, bar, horizontal_bar, pie, donut, waterfall, bubble, gantt, none
    """
    if not data or len(data) == 0:
        return 'none'
    
    # Check for time series
    if is_time_series(data):
        return 'line'
    
    # Check for waterfall (changes/decomposition)
    if is_waterfall_data(data):
        return 'waterfall'
    
    # Check for composition
    if is_composition(data):
        return 'donut' if len(data) > 4 else 'pie'
    
    # Check for comparison
    if is_categorical_comparison(data):
        return 'horizontal_bar' if len(data) > 6 else 'bar'
    
    # Default to bar
    return 'bar'


def fallback_from_context(context: str) -> str:
    """Fallback chart-type heuristic when structured data is unavailable."""
    context = context.lower()
    if any(word in context for word in ['growth', 'trend', 'over time', 'quarter', 'year']):
        return 'line'
    if any(word in context for word in ['composition', 'share', 'breakdown', 'distribution']):
        return 'donut'
    if any(word in context for word in ['change', 'increase', 'decrease', 'delta', 'bridge']):
        return 'waterfall'
    if any(word in context for word in ['comparison', 'vs', 'versus', 'ranking']):
        return 'bar'
    return 'bar'


def build_content_index(content: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index ingested documents by basename for lookup from source_file."""
    indexed = {}
    for path, item in content.get('contents', {}).items():
        basename = Path(path).name
        indexed[basename] = item
        indexed[path] = item
    return indexed


def extract_records(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tabular records from ingested document payload."""
    if not document:
        return []

    if isinstance(document.get('data'), list):
        return [r for r in document['data'] if isinstance(r, dict)]

    if isinstance(document.get('data'), dict):
        for value in document['data'].values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return value

    return []


def main():
    parser = argparse.ArgumentParser(description='Auto-detect chart types')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--content', help='Optional path to content.json from ingestion')
    parser.add_argument('--overrides', help='Optional path to chart-overrides.json')
    parser.add_argument('--output', required=True, help='Output chart-types.json')
    args = parser.parse_args()
    
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    content_index = {}
    if args.content:
        with open(args.content, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content_index = build_content_index(content)

    overrides = {}
    if args.overrides:
        override_path = Path(args.overrides)
        if override_path.exists():
            with open(override_path, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
        else:
            print(f"⚠ Overrides file not found: {args.overrides} (continuing without overrides)")
    
    chart_types = {}
    
    # Detect chart type for each slide with data
    slides = analysis.get('slides', [])
    for i, slide in enumerate(slides):
        slide_id = f"slide_{i+1}"

        slide_override = overrides.get(slide_id, {}) if isinstance(overrides, dict) else {}
        if isinstance(slide_override, dict) and slide_override.get('chart_type'):
            chart_types[slide_id] = slide_override['chart_type']
            continue

        if slide.get('data_file') and slide.get('visual', {}).get('type') == 'chart':
            visual = slide.get('visual', {})
            source_file = visual.get('source_file')
            records = extract_records(content_index.get(source_file, {})) if source_file else []
            context = slide.get('title', '') + ' ' + slide.get('content', '')

            if records:
                chart_types[slide_id] = detect_chart_type(records, context)
            else:
                chart_types[slide_id] = fallback_from_context(context)
        else:
            chart_types[slide_id] = 'none'
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(chart_types, f, indent=2)
    
    print(f"✓ Chart types saved to: {args.output}")


if __name__ == '__main__':
    main()
