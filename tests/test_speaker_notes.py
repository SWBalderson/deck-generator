"""Tests for speaker notes generation."""

import tempfile
from pathlib import Path

from utils import save_json
from generate_speaker_notes import sentence


class TestSentence:
    def test_adds_period(self):
        assert sentence('Hello') == 'Hello.'

    def test_preserves_existing_period(self):
        assert sentence('Hello.') == 'Hello.'

    def test_empty_string(self):
        assert sentence('') == ''

    def test_none_input(self):
        assert sentence(None) == ''

    def test_strips_whitespace(self):
        assert sentence('  Hello  ') == 'Hello.'


class TestSpeakerNotesGeneration:
    def test_generates_output_file(self, sample_analysis):
        import sys
        from generate_speaker_notes import main as notes_main

        with tempfile.TemporaryDirectory() as tmp:
            analysis_path = Path(tmp) / 'analysis.json'
            output_path = Path(tmp) / 'notes.md'
            save_json(analysis_path, sample_analysis)

            old_argv = sys.argv
            sys.argv = [
                'generate_speaker_notes.py',
                '--analysis', str(analysis_path),
                '--output', str(output_path),
            ]
            try:
                notes_main()
            finally:
                sys.argv = old_argv

            assert output_path.exists()
            content = output_path.read_text()
            assert 'Speaker Notes' in content
            assert 'Slide 1' in content
