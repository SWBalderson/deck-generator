"""Tests for chart type detection logic."""

from detect_chart_type import (
    is_time_series,
    is_categorical_comparison,
    is_composition,
    is_waterfall_data,
    detect_chart_type,
    fallback_from_context,
)


class TestIsTimeSeries:
    def test_month_names(self, timeseries_data):
        assert is_time_series(timeseries_data) is True

    def test_quarter_labels(self):
        data = [{'period': 'Q1', 'val': 1}, {'period': 'Q2', 'val': 2}]
        assert is_time_series(data) is True

    def test_year_values(self):
        data = [{'year': '2024', 'val': 1}, {'year': '2025', 'val': 2}]
        assert is_time_series(data) is True

    def test_non_temporal(self):
        data = [{'name': 'Alpha', 'val': 1}, {'name': 'Beta', 'val': 2}]
        assert is_time_series(data) is False

    def test_empty_data(self):
        assert is_time_series([]) is False

    def test_single_row(self):
        assert is_time_series([{'month': 'Jan 2024', 'sales': 10}]) is False


class TestIsWaterfallData:
    def test_positive_and_negative(self, waterfall_data):
        assert is_waterfall_data(waterfall_data) is True

    def test_all_positive(self):
        data = [{'cat': 'A', 'val': 10}, {'cat': 'B', 'val': 20}, {'cat': 'C', 'val': 30}]
        assert is_waterfall_data(data) is False

    def test_too_few_rows(self):
        data = [{'cat': 'A', 'val': 10}, {'cat': 'B', 'val': -5}]
        assert is_waterfall_data(data) is False


class TestIsComposition:
    def test_valid_composition(self, composition_data):
        assert is_composition(composition_data) is True

    def test_too_many_categories(self):
        data = [{'s': chr(65 + i), 'v': i} for i in range(10)]
        assert is_composition(data) is False

    def test_single_item(self):
        assert is_composition([{'s': 'A', 'v': 100}]) is False


class TestDetectChartType:
    def test_timeseries_returns_line(self, timeseries_data):
        assert detect_chart_type(timeseries_data) == 'line'

    def test_waterfall_data(self, waterfall_data):
        assert detect_chart_type(waterfall_data) == 'waterfall'

    def test_composition_returns_pie_or_donut(self, composition_data):
        result = detect_chart_type(composition_data)
        assert result in ('pie', 'donut')

    def test_empty_data_returns_none(self):
        assert detect_chart_type([]) == 'none'

    def test_categorical_returns_bar(self):
        data = [{'name': f'Item {i}', 'value': i * 10} for i in range(8)]
        result = detect_chart_type(data)
        assert result in ('bar', 'horizontal_bar')


class TestFallbackFromContext:
    def test_growth_keyword(self):
        assert fallback_from_context('Revenue growth over time') == 'line'

    def test_composition_keyword(self):
        assert fallback_from_context('Market share breakdown') == 'donut'

    def test_change_keyword(self):
        assert fallback_from_context('Revenue bridge change analysis') == 'waterfall'

    def test_comparison_keyword(self):
        assert fallback_from_context('Regional comparison vs peers') == 'bar'

    def test_generic_falls_back_to_bar(self):
        assert fallback_from_context('Something unrelated') == 'bar'
