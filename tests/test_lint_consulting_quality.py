"""Tests for consulting quality linting and scoring."""

from lint_consulting_quality import lint_analysis, score_from_issues, rank_fixes


class TestScoreFromIssues:
    def test_no_issues_gives_perfect_score(self):
        score, cats, penalties = score_from_issues([])
        assert score == 100
        assert all(v > 0 for v in cats.values())

    def test_penalties_reduce_score(self):
        issues = [
            {'category': 'action_titles', 'severity': 'warn', 'impact': 10},
            {'category': 'pyramid', 'severity': 'warn', 'impact': 10},
        ]
        score, cats, penalties = score_from_issues(issues)
        assert score < 100
        assert penalties['action_titles'] == 10

    def test_info_severity_not_penalised(self):
        issues = [{'category': 'action_titles', 'severity': 'info', 'impact': 25}]
        score, _, _ = score_from_issues(issues)
        assert score == 100


class TestRankFixes:
    def test_ranks_by_impact(self):
        issues = [
            {'suggestion': 'Fix A', 'impact': 5, 'severity': 'warn', 'category': 'x'},
            {'suggestion': 'Fix B', 'impact': 10, 'severity': 'warn', 'category': 'x'},
        ]
        ranked = rank_fixes(issues)
        assert ranked[0]['suggestion'] == 'Fix B'

    def test_groups_duplicate_suggestions(self):
        issues = [
            {'suggestion': 'Same fix', 'impact': 3, 'severity': 'warn', 'category': 'x'},
            {'suggestion': 'Same fix', 'impact': 3, 'severity': 'warn', 'category': 'x'},
        ]
        ranked = rank_fixes(issues)
        assert ranked[0]['occurrences'] == 2
        assert ranked[0]['impact'] == 6

    def test_limits_to_five(self):
        issues = [
            {'suggestion': f'Fix {i}', 'impact': i, 'severity': 'warn', 'category': 'x'}
            for i in range(10)
        ]
        ranked = rank_fixes(issues)
        assert len(ranked) <= 5


class TestLintAnalysis:
    def test_good_fixture_scores_well(self, sample_analysis):
        report = lint_analysis(sample_analysis, {}, {}, 0.6)
        assert report['overall_score'] >= 50

    def test_empty_deck_produces_report(self):
        payload = {'title': 'Empty', 'slides': []}
        report = lint_analysis(payload, {}, {}, 0.6)
        assert 'overall_score' in report

    def test_missing_sources_flagged(self):
        payload = {
            'title': 'Test',
            'slides': [
                {
                    'layout': 'content',
                    'title': 'Slide improves something.',
                    'bullets': [
                        {'main': 'A', 'detail': 'd'},
                        {'main': 'B', 'detail': 'd'},
                        {'main': 'C', 'detail': 'd'},
                    ],
                },
            ],
        }
        report = lint_analysis(payload, {}, {}, 0.6)
        blocking = report.get('blocking_issues', [])
        assert any('source' in i.get('message', '').lower() for i in blocking)

    def test_overlapping_slides_flagged(self):
        slide = {
            'layout': 'content',
            'title': 'Revenue growth improves dramatically.',
            'source': 'report.csv',
            'bullets': [
                {'main': 'Revenue growth', 'detail': 'Revenue increased significantly.'},
                {'main': 'Margin growth', 'detail': 'Margin improved over time.'},
                {'main': 'Volume growth', 'detail': 'Volume expansion continued.'},
            ],
        }
        payload = {'title': 'Test', 'slides': [dict(slide), dict(slide)]}
        report = lint_analysis(payload, {}, {}, 0.6)
        warnings = report.get('warnings', [])
        assert any('overlap' in w.get('message', '').lower() for w in warnings)
