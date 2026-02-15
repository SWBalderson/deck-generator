#!/usr/bin/env python3
"""Scaffold a local/private theme under assets/themes-local."""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    return slug


def validate_hex(label: str, value: str) -> None:
    if not HEX_COLOR_RE.match(value):
        raise ValueError(f"{label} must be a 6-digit hex value like #003366")


def prompt_text(label: str, default: Optional[str] = None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default


def prompt_hex(label: str, default: str) -> str:
    while True:
        value = prompt_text(label, default)
        try:
            validate_hex(label, value)
            return value
        except ValueError as exc:
            print(f"✗ {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local deck-generator theme")
    parser.add_argument("--theme-name", help="Theme name (for example: my-brand)")
    parser.add_argument("--primary", help="Primary colour hex (for example: #003366)")
    parser.add_argument("--secondary", help="Secondary colour hex (for example: #6699CC)")
    parser.add_argument("--accent", help="Accent colour hex (for example: #FF6B35)")
    parser.add_argument("--background", default="#FFFFFF", help="Background colour hex")
    parser.add_argument("--text", default="#1F2937", help="Body text colour hex")
    parser.add_argument("--force", action="store_true", help="Overwrite if theme already exists")
    args = parser.parse_args()

    interactive = not all([args.theme_name, args.primary, args.secondary, args.accent])
    if interactive and not sys.stdin.isatty():
        print(
            "✗ Missing required arguments. Provide --theme-name, --primary, --secondary, and --accent "
            "or run interactively in a terminal.",
            file=sys.stderr,
        )
        return 1

    if interactive:
        print("Create local theme (private, not pushed to git)")
        args.theme_name = args.theme_name or prompt_text("Theme name", "my-brand")
        args.primary = args.primary or prompt_hex("Primary (#RRGGBB)", "#003366")
        args.secondary = args.secondary or prompt_hex("Secondary (#RRGGBB)", "#6699CC")
        args.accent = args.accent or prompt_hex("Accent (#RRGGBB)", "#FF6B35")
        args.background = prompt_hex("Background (#RRGGBB)", args.background)
        args.text = prompt_hex("Body text (#RRGGBB)", args.text)

    theme_name = slugify(args.theme_name)
    if not theme_name:
        print("✗ Theme name must contain at least one letter or number", file=sys.stderr)
        return 1

    try:
        validate_hex("primary", args.primary)
        validate_hex("secondary", args.secondary)
        validate_hex("accent", args.accent)
        validate_hex("background", args.background)
        validate_hex("text", args.text)
    except ValueError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    skill_dir = Path(__file__).resolve().parent.parent
    theme_dir = skill_dir / "assets" / "themes-local" / theme_name

    if theme_dir.exists() and not args.force:
        if interactive:
            overwrite = prompt_text("Theme exists. Overwrite? (y/N)", "N").lower()
            if overwrite in {"y", "yes"}:
                args.force = True
        if not args.force:
            print(f"✗ Theme already exists: {theme_dir}", file=sys.stderr)
            print("  Use --force to overwrite.", file=sys.stderr)
            return 1

    theme_dir.mkdir(parents=True, exist_ok=True)

    theme_css = f"""/* Local private theme: {theme_name} */

:root {{
  --slide-primary: {args.primary};
  --slide-secondary: {args.secondary};
  --slide-accent: {args.accent};
  --slide-background: {args.background};
  --slide-text: {args.text};

  --slide-border: #E5E7EB;
  --slide-grid: #EEF2F7;
  --slide-overlay: rgba(0, 0, 0, 0.35);
}}

.slidev-layout {{
  background-color: var(--slide-background);
  color: var(--slide-text);
  font-family: 'Source Sans 3', 'Inter', 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.4;
}}

h1, h2, h3 {{
  font-family: 'Source Serif 4', 'Libre Baskerville', Georgia, 'Times New Roman', serif;
  color: var(--slide-primary);
  font-weight: 600;
  line-height: 1.3;
}}

.slide-title {{
  font-family: Georgia, serif;
  color: var(--slide-primary);
}}

.slide-source {{
  color: var(--slide-secondary);
}}

.section-slide {{
  border-top: 3px solid var(--slide-accent);
  border-bottom: 3px solid var(--slide-accent);
}}
"""

    uno_config = f"""import {{ defineConfig }} from 'unocss'

export default defineConfig({{
  theme: {{
    colors: {{
      primary: '{args.primary}',
      secondary: '{args.secondary}',
      accent: '{args.accent}',
      background: '{args.background}',
      text: '{args.text}',
      border: '#E5E7EB',
      grid: '#EEF2F7',
      overlay: 'rgba(0, 0, 0, 0.35)',
    }},
    fontFamily: {{
      serif: '"Source Serif 4", "Libre Baskerville", Georgia, "Times New Roman", serif',
      sans: '"Source Sans 3", Inter, "Helvetica Neue", Arial, sans-serif',
    }},
  }},
}})
"""

    (theme_dir / "theme.css").write_text(theme_css, encoding="utf-8")
    (theme_dir / "uno.config.ts").write_text(uno_config, encoding="utf-8")

    print(f"✓ Local theme created: {theme_name}")
    print(f"  Path: {theme_dir}")
    print("  Use this theme name in the skill when prompted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
