#!/usr/bin/env python3
"""Scaffold a local/private theme under assets/themes-local."""

import argparse
import re
import sys
from pathlib import Path


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    return slug


def validate_hex(label: str, value: str) -> None:
    if not HEX_COLOR_RE.match(value):
        raise ValueError(f"{label} must be a 6-digit hex value like #003366")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local deck-generator theme")
    parser.add_argument("--theme-name", required=True, help="Theme name (for example: my-brand)")
    parser.add_argument("--primary", required=True, help="Primary colour hex (for example: #003366)")
    parser.add_argument("--secondary", required=True, help="Secondary colour hex (for example: #6699CC)")
    parser.add_argument("--accent", required=True, help="Accent colour hex (for example: #FF6B35)")
    parser.add_argument("--background", default="#FFFFFF", help="Background colour hex")
    parser.add_argument("--text", default="#1F2937", help="Body text colour hex")
    parser.add_argument("--force", action="store_true", help="Overwrite if theme already exists")
    args = parser.parse_args()

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
