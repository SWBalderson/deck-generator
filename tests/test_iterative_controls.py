"""Tests for iterative slide lock and merge controls."""

import json
import tempfile
from pathlib import Path

from apply_iterative_controls import parse_indexes
from utils import load_json, save_json


class TestParseIndexes:
    def test_valid_indexes(self):
        assert parse_indexes([1, 3, 5]) == {1, 3, 5}

    def test_filters_zero_and_negative(self):
        assert parse_indexes([0, -1, 2]) == {2}

    def test_empty_list(self):
        assert parse_indexes([]) == set()


class TestLockMerge:
    def _run_merge(self, base, new, lock_slides=None, regenerate_only=None, existing_locks=None):
        """Helper to run the merge logic from apply_iterative_controls."""
        from apply_iterative_controls import main as controls_main
        import sys

        with tempfile.TemporaryDirectory() as tmp:
            base_path = Path(tmp) / 'base.json'
            new_path = Path(tmp) / 'new.json'
            output_path = Path(tmp) / 'output.json'
            locks_path = Path(tmp) / 'locks.json'

            save_json(base_path, base)
            save_json(new_path, new)
            if existing_locks:
                save_json(locks_path, existing_locks)

            argv = [
                'apply_iterative_controls.py',
                '--base-analysis', str(base_path),
                '--new-analysis', str(new_path),
                '--output', str(output_path),
                '--locks-file', str(locks_path),
            ]
            if lock_slides:
                argv.extend(['--lock-slides'] + [str(s) for s in lock_slides])
            if regenerate_only:
                argv.extend(['--regenerate-only'] + [str(s) for s in regenerate_only])

            old_argv = sys.argv
            sys.argv = argv
            try:
                controls_main()
            finally:
                sys.argv = old_argv

            return load_json(output_path), load_json(locks_path)

    def test_locked_slide_preserved(self):
        base = {
            'title': 'Base',
            'slides': [
                {'layout': 'content', 'title': 'Original slide 1.'},
                {'layout': 'content', 'title': 'Original slide 2.'},
            ],
        }
        new = {
            'title': 'New',
            'slides': [
                {'layout': 'content', 'title': 'Changed slide 1.'},
                {'layout': 'content', 'title': 'Changed slide 2.'},
            ],
        }
        merged, locks = self._run_merge(base, new, lock_slides=[1])
        assert merged['slides'][0]['title'] == 'Original slide 1.'
        assert merged['slides'][1]['title'] == 'Changed slide 2.'
        assert 1 in locks['locked_slide_indexes']

    def test_regenerate_only_restricts_changes(self):
        base = {
            'title': 'Base',
            'slides': [
                {'layout': 'content', 'title': 'Slide 1.'},
                {'layout': 'content', 'title': 'Slide 2.'},
                {'layout': 'content', 'title': 'Slide 3.'},
            ],
        }
        new = {
            'title': 'New',
            'slides': [
                {'layout': 'content', 'title': 'New 1.'},
                {'layout': 'content', 'title': 'New 2.'},
                {'layout': 'content', 'title': 'New 3.'},
            ],
        }
        merged, _ = self._run_merge(base, new, regenerate_only=[2])
        assert merged['slides'][0]['title'] == 'Slide 1.'
        assert merged['slides'][1]['title'] == 'New 2.'
        assert merged['slides'][2]['title'] == 'Slide 3.'
