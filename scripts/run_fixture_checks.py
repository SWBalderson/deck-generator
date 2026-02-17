#!/usr/bin/env python3
"""Run fast fixture-based regression checks for deck-generator scripts."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'
FIXTURES = ROOT / 'examples' / 'fixtures'


def run(cmd):
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f'Command failed: {" ".join(cmd)}')
    return result


def read_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    with tempfile.TemporaryDirectory(prefix='deck-fixtures-') as tmp:
        tmp_path = Path(tmp)

        # 1) analysis validation passes on mapped fixture
        run([
            sys.executable,
            str(SCRIPTS / 'validate_analysis.py'),
            '--analysis',
            str(FIXTURES / 'analysis-mapped-sample.json'),
        ])

        # 2) detect chart type from structured content fixture
        detect_content = tmp_path / 'detect-content.json'
        detect_analysis = tmp_path / 'detect-analysis.json'
        detect_output = tmp_path / 'detect-types.json'

        timeseries_rows = read_json(FIXTURES / 'detect-timeseries.json')
        detect_content.write_text(
            json.dumps(
                {
                    'contents': {
                        'fixtures/detect-timeseries.json': {
                            'filename': 'detect-timeseries.json',
                            'type': 'json',
                            'data': timeseries_rows,
                        }
                    }
                },
                indent=2,
            ),
            encoding='utf-8',
        )
        detect_analysis.write_text(
            json.dumps(
                {
                    'title': 'Detect fixture',
                    'slides': [
                        {
                            'layout': 'chart-full',
                            'title': 'Quarterly trend improves over time.',
                            'data_file': 'chart_1.json',
                            'visual': {
                                'type': 'chart',
                                'chart_type': 'bar',
                                'data_file': 'chart_1.json',
                                'source_file': 'detect-timeseries.json',
                            },
                        }
                    ],
                },
                indent=2,
            ),
            encoding='utf-8',
        )

        run([
            sys.executable,
            str(SCRIPTS / 'detect_chart_type.py'),
            '--analysis',
            str(detect_analysis),
            '--content',
            str(detect_content),
            '--output',
            str(detect_output),
        ])
        detected = read_json(detect_output)
        if detected.get('slide_1') != 'line':
            raise RuntimeError(f"Expected slide_1=line, got {detected.get('slide_1')}")

        # 3) generate charts from mapped source data
        mapped_out = tmp_path / 'mapped-out'
        mapped_out.mkdir(parents=True, exist_ok=True)
        run([
            sys.executable,
            str(SCRIPTS / 'generate_charts.py'),
            '--analysis',
            str(FIXTURES / 'analysis-mapped-sample.json'),
            '--types',
            str(FIXTURES / 'chart-types-mapped-sample.json'),
            '--content',
            str(FIXTURES / 'content-mapped-sample.json'),
            '--output',
            str(mapped_out),
            '--theme',
            'consulting',
        ])
        chart_1 = read_json(mapped_out / 'chart_1.json')
        if chart_1.get('type') != 'line':
            raise RuntimeError('Expected mapped chart type line.')

        # 4) override file forces output name/type path
        override_out = tmp_path / 'override-out'
        override_out.mkdir(parents=True, exist_ok=True)
        run([
            sys.executable,
            str(SCRIPTS / 'generate_charts.py'),
            '--analysis',
            str(FIXTURES / 'analysis-mapped-sample.json'),
            '--types',
            str(FIXTURES / 'chart-types-mapped-sample.json'),
            '--content',
            str(FIXTURES / 'content-mapped-sample.json'),
            '--overrides',
            str(FIXTURES / 'chart-overrides-sample.json'),
            '--output',
            str(override_out),
            '--theme',
            'consulting',
        ])
        override_chart_path = override_out / 'chart_1_override.json'
        if not override_chart_path.exists():
            raise RuntimeError('Expected override output chart_1_override.json to exist.')
        override_chart = read_json(override_chart_path)
        if override_chart.get('type') != 'bar':
            raise RuntimeError('Expected override chart type bar.')

        # Build content used by consulting-quality fixture checks
        # (re-using demo source files from examples)
        run([
            sys.executable,
            str(SCRIPTS / 'ingest_documents.py'),
            '--files',
            str(ROOT / 'examples' / 'demo-presentation' / 'source_docs' / 'q4_strategy_brief.md'),
            str(ROOT / 'examples' / 'demo-presentation' / 'source_docs' / 'market_data.csv'),
            '--output',
            str(tmp_path / 'smoke-content.json'),
        ])

        # 5) consulting quality linter strict pass fixture
        consulting_report = tmp_path / 'consulting-quality-report.json'
        run([
            sys.executable,
            str(SCRIPTS / 'lint_consulting_quality.py'),
            '--analysis',
            str(FIXTURES / 'consulting-quality-good.json'),
            '--content',
            str(tmp_path / 'smoke-content.json'),
            '--strict',
            '--threshold',
            '70',
            '--report-out',
            str(consulting_report),
        ])
        report = read_json(consulting_report)
        if report.get('overall_score', 0) < 70:
            raise RuntimeError('Expected consulting quality score >= 70 for good fixture.')

    print('✓ Fixture checks passed')


if __name__ == '__main__':
    main()
