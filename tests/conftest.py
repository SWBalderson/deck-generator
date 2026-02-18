"""Shared fixtures for deck-generator tests."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def sample_analysis():
    return {
        'title': 'Test Presentation',
        'subtitle': 'Subtitle',
        'slides': [
            {
                'layout': 'title',
                'title': 'Welcome to the presentation.',
                'subtitle': 'A subtitle',
            },
            {
                'layout': 'content',
                'title': 'Revenue performance improved materially.',
                'source': 'report.csv',
                'bullets': [
                    {'main': 'Growth', 'detail': 'Revenue increased by 20%.'},
                    {'main': 'Margin', 'detail': 'Margin held steady at 12%.'},
                    {'main': 'Outlook', 'detail': 'Growth expected to continue.'},
                ],
                'visual': {'type': 'none'},
            },
            {
                'layout': 'chart-full',
                'title': 'Quarterly trend shows consistent growth.',
                'source': 'data.csv',
                'data_file': 'chart_1.json',
                'visual': {
                    'type': 'chart',
                    'chart_type': 'line',
                    'data_file': 'chart_1.json',
                    'source_file': 'data.csv',
                    'x_key': 'quarter',
                    'y_key': 'revenue',
                },
            },
            {
                'layout': 'end',
                'title': 'Questions?',
            },
        ],
    }


@pytest.fixture
def sample_content():
    return {
        'contents': {
            'data.csv': {
                'filename': 'data.csv',
                'type': 'csv',
                'data': [
                    {'quarter': 'Q1', 'revenue': 100},
                    {'quarter': 'Q2', 'revenue': 120},
                    {'quarter': 'Q3', 'revenue': 140},
                    {'quarter': 'Q4', 'revenue': 160},
                ],
                'columns': ['quarter', 'revenue'],
            },
        },
        'errors': [],
        'total_files': 1,
        'successful': 1,
        'failed': 0,
    }


@pytest.fixture
def timeseries_data():
    return [
        {'month': 'Jan 2024', 'sales': 100},
        {'month': 'Feb 2024', 'sales': 120},
        {'month': 'Mar 2024', 'sales': 130},
    ]


@pytest.fixture
def waterfall_data():
    return [
        {'category': 'Base', 'change': 100},
        {'category': 'Growth', 'change': 25},
        {'category': 'Cost', 'change': -10},
        {'category': 'Total', 'change': 115},
    ]


@pytest.fixture
def composition_data():
    return [
        {'segment': 'A', 'share': 40},
        {'segment': 'B', 'share': 30},
        {'segment': 'C', 'share': 20},
        {'segment': 'D', 'share': 10},
    ]
