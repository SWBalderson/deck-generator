#!/usr/bin/env python3
"""
Export presentation to multiple formats.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from validate_analysis import validate_analysis_payload
from utils import load_json


def resolve_slidev_runner() -> List[str]:
    """Resolve Slidev runner command from available tooling."""
    if shutil.which('bunx'):
        return ['bunx', 'slidev']
    if shutil.which('npx'):
        return ['npx', 'slidev']
    raise RuntimeError('Neither bunx nor npx is available to run Slidev')


def export_format(
    deck_dir: Path,
    format_type: str,
    timeout: int = 60000,
    wait: int = 1000,
    base: str = '/',
):
    """Export to specific format."""
    output_name = deck_dir.name.replace('_deck', '')
    runner = resolve_slidev_runner()

    if format_type == 'pdf':
        cmd = runner + [
            'export',
            '--output',
            f'{output_name}.pdf',
            '--timeout',
            str(timeout),
            '--wait',
            str(wait),
        ]
    elif format_type == 'pptx':
        cmd = runner + [
            'export',
            '--format',
            'pptx',
            '--output',
            f'{output_name}.pptx',
            '--timeout',
            str(timeout),
            '--wait',
            str(wait),
        ]
    elif format_type == 'spa':
        if not (base.startswith('/') and base.endswith('/')):
            raise ValueError("'base' must start and end with '/'")
        cmd = runner + ['build', '--out', 'dist', '--base', base]
    else:
        raise ValueError(f"Unknown format: {format_type}")

    try:
        subprocess.run(cmd, cwd=deck_dir, check=True, capture_output=True, text=True)
        print(f"✓ Exported {format_type.upper()}")
        return True
    except subprocess.CalledProcessError as e:
        print(
            f"✗ Failed to export {format_type}: {e.stderr or e.stdout}",
            file=sys.stderr,
        )
        return False


def export_all(
    deck_dir: str,
    formats: List[str],
    analysis_path: str = None,
    base: str = '/',
    timeout: int = 60000,
    wait: int = 1000,
) -> int:
    """Export all requested formats. Callable from pipeline or CLI."""
    dd = Path(deck_dir)

    if not dd.exists():
        print(f"✗ Deck directory not found: {dd}", file=sys.stderr)
        raise FileNotFoundError(f"Deck directory not found: {dd}")

    if analysis_path:
        payload = load_json(Path(analysis_path))
        errors = validate_analysis_payload(payload)
        if errors:
            msg = '✗ Analysis validation failed:\n' + '\n'.join(f'  - {e}' for e in errors)
            print(msg, file=sys.stderr)
            raise ValueError(msg)

    success = []
    failed = []

    for fmt in formats:
        if export_format(dd, fmt, timeout, wait, base):
            success.append(fmt)
        else:
            failed.append(fmt)
            break

    if success:
        print(f"\n✓ Exported: {', '.join(success)}")
    if failed:
        print(f"✗ Failed: {', '.join(failed)}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(description='Export presentation')
    parser.add_argument('--deck-dir', required=True, help='Path to deck directory')
    parser.add_argument('--formats', nargs='+', default=['pdf', 'pptx', 'spa'],
                       help='Formats to export (pdf, pptx, spa)')
    parser.add_argument('--timeout', type=int, default=60000, help='Export timeout in ms')
    parser.add_argument('--wait', type=int, default=1000, help='Per-slide render wait in ms for export')
    parser.add_argument('--base', default='/', help="Base path for SPA build (must start and end with '/')")
    parser.add_argument('--analysis', help='Optional analysis.json path to validate before export')
    args = parser.parse_args()

    rc = export_all(args.deck_dir, args.formats, args.analysis, args.base, args.timeout, args.wait)
    return rc


if __name__ == '__main__':
    sys.exit(main())
