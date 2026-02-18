"""Tests for slide quality linting."""

from lint_slides import lint_analysis


class TestLintAnalysis:
    def test_clean_analysis_passes(self, sample_analysis):
        warnings = lint_analysis(sample_analysis)
        missing_source = [w for w in warnings if 'missing source' in w]
        assert len(missing_source) == 0

    def test_missing_source_citation(self):
        payload = {
            'slides': [{
                'layout': 'content',
                'title': 'Slide improves clarity.',
                'bullets': [
                    {'main': 'A', 'detail': 'detail'},
                    {'main': 'B', 'detail': 'detail'},
                    {'main': 'C', 'detail': 'detail'},
                ],
            }],
        }
        warnings = lint_analysis(payload)
        assert any('source' in w.lower() for w in warnings)

    def test_too_many_bullets(self):
        payload = {
            'slides': [{
                'layout': 'content',
                'title': 'Slide shows progress.',
                'source': 'report.csv',
                'bullets': [{'main': f'Point {i}', 'detail': ''} for i in range(8)],
            }],
        }
        warnings = lint_analysis(payload)
        assert any('bullets' in w for w in warnings)

    def test_too_few_bullets(self):
        payload = {
            'slides': [{
                'layout': 'content',
                'title': 'Slide shows progress.',
                'source': 'report.csv',
                'bullets': [{'main': 'Only one', 'detail': ''}],
            }],
        }
        warnings = lint_analysis(payload)
        assert any('bullets' in w for w in warnings)

    def test_weak_title_no_verb(self):
        payload = {
            'slides': [{
                'layout': 'content',
                'title': 'Revenue overview',
                'source': 'report.csv',
                'bullets': [
                    {'main': 'A', 'detail': 'd'},
                    {'main': 'B', 'detail': 'd'},
                    {'main': 'C', 'detail': 'd'},
                ],
            }],
        }
        warnings = lint_analysis(payload)
        assert any('verb' in w.lower() for w in warnings)

    def test_title_skipped_on_non_content_layout(self):
        payload = {
            'slides': [
                {'layout': 'title', 'title': 'Welcome'},
                {'layout': 'end', 'title': 'Thanks'},
            ],
        }
        warnings = lint_analysis(payload)
        source_warnings = [w for w in warnings if 'source' in w.lower()]
        assert len(source_warnings) == 0
