#!/usr/bin/env python3
"""
Generate Chart.js configurations from data.
"""

import argparse
import json
import re
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description='Generate Chart.js configurations')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--types', required=True, help='Path to chart-types.json')
    parser.add_argument('--output', required=True, help='Output directory for chart configs')
    parser.add_argument('--theme', default='consulting', help='Theme name')
    parser.add_argument('--colors', help='Optional JSON colour overrides')
    args = parser.parse_args()

    hex_re = re.compile(r'^#[0-9A-Fa-f]{6}$')

    def valid_color(value):
        return isinstance(value, str) and bool(hex_re.match(value.strip()))
    
    # Load theme colors
    themes = {
        'consulting': {
            'primary': '#003366',
            'secondary': '#6699CC',
            'accent': '#FF6B35',
            'grid': '#E5E5E5'
        }
    }
    colors = dict(themes.get(args.theme, themes['consulting']))
    if args.colors:
        try:
            overrides = json.loads(args.colors)
            for key in ['primary', 'secondary', 'accent', 'grid']:
                if valid_color(overrides.get(key)):
                    colors[key] = overrides[key].strip().upper()
        except json.JSONDecodeError:
            print('⚠ Invalid --colors JSON. Using theme defaults.')
    
    # Load analysis and chart types
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    with open(args.types, 'r', encoding='utf-8') as f:
        chart_types = json.load(f)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate charts
    slides = analysis.get('slides', [])
    for i, slide in enumerate(slides):
        slide_id = f"slide_{i+1}"
        chart_type = chart_types.get(slide_id, 'none')
        
        if chart_type == 'none':
            continue
        
        # In real implementation, would load actual data
        # For demo, generate sample configs
        if chart_type == 'line':
            config = generate_line_chart(
                data=[1.8, 2.0, 2.2, 2.4],
                labels=['Q1', 'Q2', 'Q3', 'Q4'],
                dataset_label='Revenue (£M)',
                colors=colors
            )
        elif chart_type == 'bar':
            config = generate_bar_chart(
                data=[15, 23, 18, 12, 8],
                labels=['UK', 'Germany', 'France', 'Netherlands', 'Other'],
                dataset_label='Market Share (%)',
                colors=colors
            )
        elif chart_type == 'waterfall':
            config = generate_waterfall_chart(
                data=[100, 15, -5, 10, 120],
                labels=['Baseline', 'Volume', 'Price', 'Mix', 'Final'],
                colors=colors
            )
        elif chart_type in ['pie', 'donut']:
            config = generate_pie_chart(
                data=[35, 25, 20, 12, 8],
                labels=['Product A', 'Product B', 'Product C', 'Product D', 'Other'],
                colors=colors
            )
        else:
            print(f"⚠ Unsupported chart type '{chart_type}' for {slide_id}; skipping")
            continue
        
        # Save config
        output_file = output_dir / f"chart_{i+1}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Generated: {output_file}")
    
    print(f"\n✓ All charts saved to: {args.output}")


if __name__ == '__main__':
    main()
