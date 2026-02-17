#!/usr/bin/env python3
"""
Create Slidev project structure with custom theme.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def resolve_theme_dir(skill_dir: Path, theme: str) -> Path:
    """Resolve theme directory from shared or local theme folders."""
    shared = skill_dir / 'assets' / 'themes' / theme
    if (shared / 'theme.css').exists() and (shared / 'uno.config.ts').exists():
        return shared

    local = skill_dir / 'assets' / 'themes-local' / theme
    if (local / 'theme.css').exists() and (local / 'uno.config.ts').exists():
        return local

    fallback = skill_dir / 'assets' / 'themes' / 'consulting'
    print(
        f"⚠ Theme '{theme}' not found in assets/themes or assets/themes-local. "
        "Falling back to 'consulting'."
    )
    return fallback


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def normalise_colors(colors: dict) -> dict:
    """Normalise and validate optional theme colour overrides."""
    allowed = {'primary', 'secondary', 'accent', 'background', 'text', 'text-light'}
    normalised = {}
    for key, value in colors.items():
        if key not in allowed:
            continue
        if not isinstance(value, str):
            continue
        candidate = value.strip()
        if HEX_COLOR_RE.match(candidate):
            normalised[key] = candidate.upper()
    return normalised


def apply_color_overrides(output_dir: Path, colors: dict):
    """Apply colour overrides to copied theme files."""
    if not colors:
        return

    css_path = output_dir / 'styles' / 'theme.css'
    uno_path = output_dir / 'uno.config.ts'

    css_replacements = {
        '--slide-primary': colors.get('primary'),
        '--slide-secondary': colors.get('secondary'),
        '--slide-accent': colors.get('accent'),
        '--slide-bg': colors.get('background'),
        '--slide-text': colors.get('text'),
        '--slide-text-light': colors.get('text-light'),
    }
    uno_replacements = {
        'primary': colors.get('primary'),
        'secondary': colors.get('secondary'),
        'accent': colors.get('accent'),
        'background': colors.get('background'),
        'text': colors.get('text'),
        'text-light': colors.get('text-light'),
    }

    css = css_path.read_text(encoding='utf-8')
    for variable, value in css_replacements.items():
        if value:
            css = re.sub(
                rf"({re.escape(variable)}\s*:\s*)#[0-9A-Fa-f]{{6}}",
                rf"\1{value}",
                css,
            )
    css_path.write_text(css, encoding='utf-8')

    uno = uno_path.read_text(encoding='utf-8')
    for key, value in uno_replacements.items():
        if value:
            uno = re.sub(
                rf"((?:'{re.escape(key)}'|{re.escape(key)})\s*:\s*)'#[0-9A-Fa-f]{{6}}'",
                rf"\1'{value}'",
                uno,
            )
    uno_path.write_text(uno, encoding='utf-8')


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
    
    # Apply colour overrides if provided
    if colors:
        apply_color_overrides(output_dir, colors)

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
            colors = normalise_colors(json.loads(args.colors))
        except json.JSONDecodeError:
            print("⚠ Invalid --colors JSON. Ignoring colour overrides.")

    create_project(output_dir, args.theme, colors, args.logo)


if __name__ == '__main__':
    main()
