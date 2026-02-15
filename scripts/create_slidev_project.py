#!/usr/bin/env python3
"""
Create Slidev project structure with custom theme.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def resolve_theme_dir(skill_dir: Path, theme: str) -> Path:
    """Resolve theme directory from shared or local theme folders."""
    shared = skill_dir / 'assets' / 'themes' / theme
    if shared.exists():
        return shared

    local = skill_dir / 'assets' / 'themes-local' / theme
    if local.exists():
        return local

    fallback = skill_dir / 'assets' / 'themes' / 'consulting'
    print(
        f"⚠ Theme '{theme}' not found in assets/themes or assets/themes-local. "
        "Falling back to 'consulting'."
    )
    return fallback


def create_project(output_dir: Path, theme: str, colors: dict, logo: Optional[str] = None):
    """Create Slidev project structure."""
    
    # Create directories
    dirs = ['public/images', 'public/data', 'components', 'layouts', 'styles', '.temp']
    for d in dirs:
        (output_dir / d).mkdir(parents=True, exist_ok=True)
    
    # Initialize with bun/npm
    try:
        subprocess.run(['bun', 'init', '-y'], cwd=output_dir, check=True, capture_output=True)
    except:
        try:
            subprocess.run(['npm', 'init', '-y'], cwd=output_dir, check=True, capture_output=True)
        except Exception as e:
            print(f"✗ Failed to initialize project: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Install dependencies
    deps = ['@slidev/cli', 'vue-chartjs', 'chart.js', 'chartjs-adapter-date-fns']
    try:
        subprocess.run(['bun', 'add'] + deps, cwd=output_dir, check=True, capture_output=True)
        subprocess.run(['bun', 'add', '-d', 'playwright-chromium'], cwd=output_dir, check=True, capture_output=True)
    except:
        try:
            subprocess.run(['npm', 'install'] + deps, cwd=output_dir, check=True, capture_output=True)
            subprocess.run(['npm', 'install', '-D', 'playwright-chromium'], cwd=output_dir, check=True, capture_output=True)
        except Exception as e:
            print(f"✗ Failed to install dependencies: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Copy theme files
    skill_dir = Path(__file__).parent.parent
    theme_dir = resolve_theme_dir(skill_dir, theme)

    shutil.copy(theme_dir / 'theme.css', output_dir / 'styles' / 'theme.css')
    shutil.copy(theme_dir / 'uno.config.ts', output_dir / 'uno.config.ts')
    
    # Copy layouts and components
    layouts_dir = skill_dir / 'assets' / 'layouts'
    components_dir = skill_dir / 'assets' / 'components'
    
    if layouts_dir.exists():
        for f in layouts_dir.glob('*.vue'):
            shutil.copy(f, output_dir / 'layouts' / f.name)
    
    if components_dir.exists():
        for f in components_dir.glob('*.vue'):
            shutil.copy(f, output_dir / 'components' / f.name)
    
    # Copy logo
    if logo and Path(logo).exists():
        logo_path = Path(logo)
        suffix = logo_path.suffix.lower() or '.svg'
        shutil.copy(logo_path, output_dir / 'public' / f'logo{suffix}')
    
    # Create slidev.config.ts
    config = f"""import {{ defineConfig }} from '@slidev/cli'

export default defineConfig({{
  theme: 'none',
  fonts: {{
    sans: 'Inter',
    serif: 'Georgia',
  }},
  css: ['styles/theme.css'],
}})
"""
    
    with open(output_dir / 'slidev.config.ts', 'w') as f:
        f.write(config)
    
    # Initialize git
    try:
        subprocess.run(['git', 'init'], cwd=output_dir, check=True, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=output_dir, check=True, capture_output=True)
    except Exception as e:
        print(f"⚠ Warning: Git initialization failed: {e}")
    
    print(f"✓ Slidev project created at: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Create Slidev project')
    parser.add_argument('--theme', default='consulting', help='Theme name')
    parser.add_argument('--colors', help='JSON string of colors')
    parser.add_argument('--logo', help='Path to logo file')
    parser.add_argument('--output', required=True, help='Output directory')
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    colors = {}
    if args.colors:
        try:
            colors = json.loads(args.colors)
        except:
            pass
    
    create_project(output_dir, args.theme, colors, args.logo)


if __name__ == '__main__':
    main()
