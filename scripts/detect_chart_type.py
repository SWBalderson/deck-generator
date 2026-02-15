#!/usr/bin/env python3
"""
Auto-detect optimal chart type based on data structure.
"""

import argparse
import json
from typing import Dict, List, Any


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


def main():
    parser = argparse.ArgumentParser(description='Auto-detect chart types')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--output', required=True, help='Output chart-types.json')
    args = parser.parse_args()
    
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    chart_types = {}
    
    # Detect chart type for each slide with data
    slides = analysis.get('slides', [])
    for i, slide in enumerate(slides):
        slide_id = f"slide_{i+1}"
        
        if slide.get('data_file') and slide.get('visual', {}).get('type') == 'chart':
            data_file = slide['data_file']
            # In real implementation, would load and analyze the data file
            # For now, use context clues
            context = slide.get('title', '') + ' ' + slide.get('content', '')
            
            # Simple heuristic based on slide content
            if any(word in context.lower() for word in ['growth', 'trend', 'over time', 'quarter', 'year']):
                chart_types[slide_id] = 'line'
            elif any(word in context.lower() for word in ['composition', 'share', 'breakdown', 'distribution']):
                chart_types[slide_id] = 'donut'
            elif any(word in context.lower() for word in ['change', 'increase', 'decrease', 'delta', 'bridge']):
                chart_types[slide_id] = 'waterfall'
            elif any(word in context.lower() for word in ['comparison', 'vs', 'versus', 'ranking']):
                chart_types[slide_id] = 'bar'
            else:
                chart_types[slide_id] = 'bar'  # default
        else:
            chart_types[slide_id] = 'none'
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(chart_types, f, indent=2)
    
    print(f"✓ Chart types saved to: {args.output}")


if __name__ == '__main__':
    main()
