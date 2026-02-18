#!/usr/bin/env python3
"""
Generate Chart.js configurations from data.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from utils import build_content_index, extract_records, to_float


def generate_bar_chart(data, labels, dataset_label, colors):
    """Generate bar chart configuration."""
    return {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': data,
                'backgroundColor': colors['primary'],
                'borderColor': colors['primary'],
                'borderWidth': 0
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {'display': False}
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': colors['grid']}
                },
                'x': {
                    'grid': {'display': False}
                }
            }
        }
    }


def generate_line_chart(data, labels, dataset_label, colors):
    """Generate line chart configuration."""
    return {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': data,
                'borderColor': colors['primary'],
                'backgroundColor': colors['primary'] + '20',  # 20% opacity
                'borderWidth': 3,
                'fill': True,
                'tension': 0.3
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {'display': False}
            },
            'scales': {
                'y': {
                    'beginAtZero': False,
                    'grid': {'color': colors['grid']}
                },
                'x': {
                    'grid': {'display': False}
                }
            }
        }
    }


def generate_waterfall_chart(data, labels, colors):
    """Generate waterfall chart configuration."""
    return {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Value',
                'data': data,
                'backgroundColor': [
                    colors['primary'] if v >= 0 else colors['accent'] 
                    for v in data
                ],
                'borderWidth': 0
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'indexAxis': 'y',
            'plugins': {
                'legend': {'display': False}
            },
            'scales': {
                'x': {
                    'grid': {'color': colors['grid']},
                    'ticks': {
                        'callback': "function(val) { return val >= 0 ? '+' + val : val; }"
                    }
                },
                'y': {
                    'grid': {'display': False}
                }
            }
        }
    }


def generate_pie_chart(data, labels, colors):
    """Generate pie chart configuration."""
    color_palette = [
        colors['primary'],
        colors['secondary'],
        colors['accent'],
        '#666666',
        '#999999',
        '#CCCCCC'
    ]
    
    return {
        'type': 'pie',
        'data': {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': color_palette[:len(data)],
                'borderWidth': 2,
                'borderColor': '#FFFFFF'
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'position': 'right'
                }
            }
        }
    }


def infer_keys(records: List[Dict[str, Any]], x_key=None, y_key=None):
    """Infer x and y keys when not explicitly provided."""
    if not records:
        return x_key, y_key
    sample = records[0]
    keys = list(sample.keys())
    if not x_key:
        for key in keys:
            if to_float(sample.get(key)) is None:
                x_key = key
                break
    if not y_key:
        for key in keys:
            if key == x_key:
                continue
            if to_float(sample.get(key)) is not None:
                y_key = key
                break
    return x_key, y_key


def extract_xy(records: List[Dict[str, Any]], x_key: str, y_key: str):
    """Extract x labels and numeric y values from records."""
    labels = []
    values = []
    for row in records:
        if x_key not in row or y_key not in row:
            continue
        numeric = to_float(row.get(y_key))
        if numeric is None:
            continue
        labels.append(str(row.get(x_key)))
        values.append(numeric)
    return labels, values


def build_multi_series(records: List[Dict[str, Any]], x_key: str, y_key: str, series_key: str):
    """Build labels + dataset list for grouped charts."""
    labels = []
    by_series = {}

    for row in records:
        if x_key not in row or y_key not in row or series_key not in row:
            continue
        numeric = to_float(row.get(y_key))
        if numeric is None:
            continue
        x_value = str(row.get(x_key))
        s_value = str(row.get(series_key))
        if x_value not in labels:
            labels.append(x_value)
        by_series.setdefault(s_value, {})[x_value] = numeric

    datasets = []
    for series_name, points in by_series.items():
        datasets.append({
            'label': series_name,
            'data': [points.get(label, 0) for label in labels],
        })
    return labels, datasets


def chart_from_records(chart_type: str, records: List[Dict[str, Any]], visual: Dict[str, Any], colors: Dict[str, str]):
    """Generate a chart configuration from mapped records."""
    x_key, y_key = infer_keys(records, visual.get('x_key'), visual.get('y_key'))
    if not x_key or not y_key:
        return None

    series_key = visual.get('series_key')
    if series_key:
        labels, dataset_rows = build_multi_series(records, x_key, y_key, series_key)
        if not labels or not dataset_rows:
            return None

        palette = [colors['primary'], colors['secondary'], colors['accent'], '#666666']
        datasets = []
        for idx, ds in enumerate(dataset_rows):
            tone = palette[idx % len(palette)]
            datasets.append({
                'label': ds['label'],
                'data': ds['data'],
                'borderColor': tone,
                'backgroundColor': tone + '20',
                'borderWidth': 2,
                'fill': chart_type == 'line',
                'tension': 0.3,
            })
        return {
            'type': chart_type,
            'data': {'labels': labels, 'datasets': datasets},
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {'legend': {'display': True}},
                'scales': {
                    'y': {'grid': {'color': colors['grid']}},
                    'x': {'grid': {'display': False}},
                },
            },
        }

    labels, values = extract_xy(records, x_key, y_key)
    if not labels or not values:
        return None

    metric_name = y_key.replace('_', ' ').title()
    if chart_type == 'line':
        return generate_line_chart(values, labels, metric_name, colors)
    if chart_type in ['bar', 'horizontal_bar']:
        config = generate_bar_chart(values, labels, metric_name, colors)
        if chart_type == 'horizontal_bar':
            config['options']['indexAxis'] = 'y'
        return config
    if chart_type in ['pie', 'donut']:
        config = generate_pie_chart(values, labels, colors)
        config['type'] = 'doughnut' if chart_type == 'donut' else 'pie'
        return config
    if chart_type == 'waterfall':
        return generate_waterfall_chart(values, labels, colors)
    return None


THEME_PALETTES = {
    'consulting': {
        'primary': '#003366',
        'secondary': '#6699CC',
        'accent': '#FF6B35',
        'grid': '#E5E5E5',
    },
}

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def resolve_colors(theme: str, colors_json: str = None) -> dict:
    """Resolve chart colour palette from theme + optional JSON overrides."""
    colors = dict(THEME_PALETTES.get(theme, THEME_PALETTES['consulting']))
    if colors_json:
        try:
            overrides = json.loads(colors_json)
            for key in ['primary', 'secondary', 'accent', 'grid']:
                val = overrides.get(key)
                if isinstance(val, str) and HEX_COLOR_RE.match(val.strip()):
                    colors[key] = val.strip().upper()
        except json.JSONDecodeError:
            print('⚠ Invalid colours JSON. Using theme defaults.')
    return colors


def generate_and_save(
    analysis_path: str,
    types_path: str,
    content_path: str = None,
    output_dir: str = '',
    theme: str = 'consulting',
    colors_json: str = None,
    overrides_path: str = None,
) -> None:
    """Generate chart configs and write files. Callable from pipeline or CLI."""
    colors = resolve_colors(theme, colors_json)

    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    content_index = {}
    if content_path:
        with open(content_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content_index = build_content_index(content)

    overrides = {}
    if overrides_path:
        op = Path(overrides_path)
        if op.exists():
            with open(op, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
        else:
            print(f"⚠ Overrides file not found: {overrides_path} (continuing without overrides)")

    with open(types_path, 'r', encoding='utf-8') as f:
        chart_types = json.load(f)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    slides = analysis.get('slides', [])
    for i, slide in enumerate(slides):
        slide_id = f"slide_{i+1}"
        chart_type = chart_types.get(slide_id, 'none')
        visual = dict(slide.get('visual', {}))
        slide_override = overrides.get(slide_id, {}) if isinstance(overrides, dict) else {}
        if isinstance(slide_override, dict):
            visual.update({
                key: value
                for key, value in slide_override.items()
                if key in {'source_file', 'x_key', 'y_key', 'series_key', 'data_file'}
            })
            chart_type = slide_override.get('chart_type', chart_type)

        if chart_type == 'none':
            continue

        records = []
        source_file = visual.get('source_file')
        if source_file:
            records = extract_records(content_index.get(source_file, {}))

        config = None
        if records:
            config = chart_from_records(chart_type, records, visual, colors)

        if config is None:
            if chart_type == 'line':
                config = generate_line_chart([1.8, 2.0, 2.2, 2.4], ['Q1', 'Q2', 'Q3', 'Q4'], 'Revenue (£M)', colors)
            elif chart_type == 'bar':
                config = generate_bar_chart([15, 23, 18, 12, 8], ['UK', 'Germany', 'France', 'Netherlands', 'Other'], 'Market Share (%)', colors)
            elif chart_type == 'waterfall':
                config = generate_waterfall_chart([100, 15, -5, 10, 120], ['Baseline', 'Volume', 'Price', 'Mix', 'Final'], colors)
            elif chart_type in ['pie', 'donut']:
                config = generate_pie_chart([35, 25, 20, 12, 8], ['Product A', 'Product B', 'Product C', 'Product D', 'Other'], colors)
                if chart_type == 'donut':
                    config['type'] = 'doughnut'
            else:
                print(f"⚠ Unsupported chart type '{chart_type}' for {slide_id}; skipping")
                continue

        output_name = visual.get('data_file') or slide.get('data_file') or f"chart_{i+1}.json"
        output_file = out / output_name
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Generated: {output_file}")

    print(f"\n✓ All charts saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Generate Chart.js configurations')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--types', required=True, help='Path to chart-types.json')
    parser.add_argument('--output', required=True, help='Output directory for chart configs')
    parser.add_argument('--theme', default='consulting', help='Theme name')
    parser.add_argument('--colors', help='Optional JSON colour overrides')
    parser.add_argument('--content', help='Optional path to ingested content.json')
    parser.add_argument('--overrides', help='Optional path to chart-overrides.json')
    args = parser.parse_args()
    generate_and_save(args.analysis, args.types, args.content, args.output, args.theme, args.colors, args.overrides)


if __name__ == '__main__':
    main()
