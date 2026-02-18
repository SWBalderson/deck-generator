"""Tests for shared utility functions."""

from utils import (
    normalise_words,
    jaccard,
    build_content_index,
    extract_records,
    to_float,
    split_fragments,
    extract_source_text,
)


class TestNormaliseWords:
    def test_filters_stop_words(self):
        result = normalise_words('the quick brown fox and the lazy dog')
        assert 'the' not in result
        assert 'and' not in result
        assert 'quick' in result
        assert 'brown' in result

    def test_empty_string(self):
        assert normalise_words('') == []

    def test_none_input(self):
        assert normalise_words(None) == []

    def test_short_words_excluded(self):
        result = normalise_words('a to is it me go')
        assert result == []


class TestJaccard:
    def test_identical_sets(self):
        assert jaccard({'a', 'b'}, {'a', 'b'}) == 1.0

    def test_disjoint_sets(self):
        assert jaccard({'a', 'b'}, {'c', 'd'}) == 0.0

    def test_partial_overlap(self):
        assert jaccard({'a', 'b', 'c'}, {'b', 'c', 'd'}) == 0.5

    def test_empty_sets(self):
        assert jaccard(set(), set()) == 0.0
        assert jaccard({'a'}, set()) == 0.0


class TestBuildContentIndex:
    def test_indexes_by_path_and_basename(self, sample_content):
        idx = build_content_index(sample_content)
        assert 'data.csv' in idx
        assert idx['data.csv']['type'] == 'csv'

    def test_indexes_by_filename_field(self):
        content = {
            'contents': {
                '/long/path/report.csv': {
                    'filename': 'report.csv',
                    'type': 'csv',
                    'data': [],
                }
            }
        }
        idx = build_content_index(content)
        assert 'report.csv' in idx
        assert '/long/path/report.csv' in idx

    def test_empty_content(self):
        assert build_content_index({}) == {}
        assert build_content_index({'contents': {}}) == {}


class TestExtractRecords:
    def test_list_data(self):
        doc = {'data': [{'a': 1}, {'a': 2}]}
        assert extract_records(doc) == [{'a': 1}, {'a': 2}]

    def test_nested_dict_data(self):
        doc = {'data': {'sheet1': [{'x': 1}]}}
        assert extract_records(doc) == [{'x': 1}]

    def test_empty_document(self):
        assert extract_records({}) == []
        assert extract_records(None) == []

    def test_non_dict_rows_filtered(self):
        doc = {'data': [{'a': 1}, 'not a dict', {'b': 2}]}
        result = extract_records(doc)
        assert len(result) == 2


class TestToFloat:
    def test_integer(self):
        assert to_float(42) == 42.0

    def test_float(self):
        assert to_float(3.14) == 3.14

    def test_numeric_string(self):
        assert to_float('100') == 100.0

    def test_comma_separated(self):
        assert to_float('1,234') == 1234.0

    def test_percentage(self):
        assert to_float('45%') == 45.0

    def test_non_numeric_string(self):
        assert to_float('hello') is None

    def test_none_input(self):
        assert to_float(None) is None

    def test_empty_string(self):
        assert to_float('') is None


class TestSplitFragments:
    def test_splits_on_sentence_boundaries(self):
        text = 'First sentence. Second sentence! Third?'
        result = split_fragments(text)
        assert len(result) == 3

    def test_empty_string(self):
        assert split_fragments('') == []

    def test_none_input(self):
        assert split_fragments(None) == []


class TestExtractSourceText:
    def test_prefers_content_field(self):
        doc = {'content': 'hello', 'text': 'world'}
        assert extract_source_text(doc) == 'hello'

    def test_falls_back_to_text(self):
        doc = {'text': 'world'}
        assert extract_source_text(doc) == 'world'

    def test_falls_back_to_data_json(self):
        doc = {'data': [1, 2, 3]}
        result = extract_source_text(doc)
        assert '1' in result

    def test_empty_document(self):
        assert extract_source_text({}) == ''
        assert extract_source_text(None) == ''
