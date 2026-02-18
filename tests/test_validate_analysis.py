"""Tests for analysis validation, including negative cases."""

from validate_analysis import validate_analysis_payload


class TestValidPayloads:
    def test_valid_analysis(self, sample_analysis):
        errors = validate_analysis_payload(sample_analysis)
        assert errors == []

    def test_minimal_valid(self):
        payload = {
            'title': 'Deck',
            'slides': [
                {'layout': 'title', 'title': 'Hello.'},
            ],
        }
        assert validate_analysis_payload(payload) == []


class TestInvalidPayloads:
    def test_not_a_dict(self):
        errors = validate_analysis_payload([])
        assert any('JSON object' in e for e in errors)

    def test_missing_title(self):
        payload = {'slides': [{'layout': 'title', 'title': 'Hi.'}]}
        errors = validate_analysis_payload(payload)
        assert any('title' in e.lower() for e in errors)

    def test_empty_title(self):
        payload = {'title': '', 'slides': [{'layout': 'title', 'title': 'Hi.'}]}
        errors = validate_analysis_payload(payload)
        assert any('title' in e.lower() for e in errors)

    def test_missing_slides(self):
        payload = {'title': 'Deck'}
        errors = validate_analysis_payload(payload)
        assert any('slides' in e.lower() for e in errors)

    def test_empty_slides_array(self):
        payload = {'title': 'Deck', 'slides': []}
        errors = validate_analysis_payload(payload)
        assert any('slides' in e.lower() for e in errors)

    def test_invalid_layout(self):
        payload = {
            'title': 'Deck',
            'slides': [{'layout': 'invalid', 'title': 'Slide.'}],
        }
        errors = validate_analysis_payload(payload)
        assert any('layout' in e.lower() for e in errors)

    def test_missing_slide_title(self):
        payload = {
            'title': 'Deck',
            'slides': [{'layout': 'content'}],
        }
        errors = validate_analysis_payload(payload)
        assert any('title' in e.lower() for e in errors)

    def test_chart_without_data_file(self):
        payload = {
            'title': 'Deck',
            'slides': [{
                'layout': 'chart-full',
                'title': 'Chart slide.',
                'visual': {'type': 'chart', 'chart_type': 'bar'},
            }],
        }
        errors = validate_analysis_payload(payload)
        assert any('data_file' in e for e in errors)

    def test_chart_without_chart_type(self):
        payload = {
            'title': 'Deck',
            'slides': [{
                'layout': 'chart-full',
                'title': 'Chart slide.',
                'visual': {'type': 'chart', 'data_file': 'chart_1.json'},
            }],
        }
        errors = validate_analysis_payload(payload)
        assert any('chart_type' in e for e in errors)

    def test_image_without_filename(self):
        payload = {
            'title': 'Deck',
            'slides': [{
                'layout': 'content',
                'title': 'Image slide.',
                'visual': {'type': 'image'},
            }],
        }
        errors = validate_analysis_payload(payload)
        assert any('filename' in e for e in errors)

    def test_invalid_visual_type(self):
        payload = {
            'title': 'Deck',
            'slides': [{
                'layout': 'content',
                'title': 'Slide.',
                'visual': {'type': 'video'},
            }],
        }
        errors = validate_analysis_payload(payload)
        assert any('visual.type' in e for e in errors)

    def test_slide_not_dict(self):
        payload = {
            'title': 'Deck',
            'slides': ['not a dict'],
        }
        errors = validate_analysis_payload(payload)
        assert any('object' in e.lower() for e in errors)
