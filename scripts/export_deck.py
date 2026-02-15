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
        result = subprocess.run(cmd, cwd=deck_dir, check=True, capture_output=True, text=True)
        print(f"✓ Exported {format_type.upper()}")
        return True
    except subprocess.CalledProcessError as e:
        print(
            f"✗ Failed to export {format_type}: {e.stderr or e.stdout}",
            file=sys.stderr,
        )
        return False


def main():
    parser = argparse.ArgumentParser(description='Export presentation')
    parser.add_argument('--deck-dir', required=True, help='Path to deck directory')
    parser.add_argument('--formats', nargs='+', default=['pdf', 'pptx', 'spa'], 
                       help='Formats to export (pdf, pptx, spa)')
    parser.add_argument('--timeout', type=int, default=60000, help='Export timeout in ms')
    parser.add_argument('--wait', type=int, default=1000, help='Per-slide render wait in ms for export')
    parser.add_argument('--base', default='/', help="Base path for SPA build (must start and end with '/')")
    args = parser.parse_args()
    
    deck_dir = Path(args.deck_dir)
    
    if not deck_dir.exists():
        print(f"✗ Deck directory not found: {deck_dir}", file=sys.stderr)
        sys.exit(1)
    
    success = []
    failed = []
    
    for fmt in args.formats:
        if export_format(deck_dir, fmt, args.timeout, args.wait, args.base):
            success.append(fmt)
        else:
            failed.append(fmt)
            sys.exit(1)  # Stop on first error
    
    print(f"\n✓ Exported: {', '.join(success)}")
    if failed:
        print(f"✗ Failed: {', '.join(failed)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
