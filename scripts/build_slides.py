#!/usr/bin/env python3
"""
Build slides.md from template and analysis.
Auto-detects existing images and enables them automatically.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from jinja2 import Template


def check_existing_images(slides: list, output_dir: Path) -> list:
    """Check which images exist and mark them for inclusion."""
    images_dir = output_dir / 'public' / 'images'
    
    updated_slides = []
    for slide in slides:
        visual = slide.get('visual', {})
        
        # If slide has an image filename specified
        if visual.get('type') == 'image' and visual.get('filename'):
            image_path = images_dir / visual['filename']
            
            if image_path.exists():
                # Image exists - keep it enabled
                print(f"  ✓ Found image: {visual['filename']}")
            else:
                # Image doesn't exist - disable it but keep filename for reference
                print(f"  ⚠ Missing image: {visual['filename']} (will be hidden)")
                # Create a copy of visual with type set to none
                visual = visual.copy()
                visual['type'] = 'none'
                slide = slide.copy()
                slide['visual'] = visual
        
        updated_slides.append(slide)
    
    return updated_slides


def main():
    parser = argparse.ArgumentParser(description='Build slides')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--template', required=True, help='Path to slides.md.jinja2')
    parser.add_argument('--output', required=True, help='Output slides.md path')
    parser.add_argument('--deck-dir', help='Deck directory for image detection (optional)')
    parser.add_argument('--lint', action='store_true', help='Run slide quality lint before rendering')
    parser.add_argument('--lint-strict', action='store_true', help='Fail build on lint warnings (requires --lint)')
    args = parser.parse_args()
    
    # Load template
    with open(args.template, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    
    # Load analysis
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    validator = Path(__file__).parent / 'validate_analysis.py'
    validate_cmd = [sys.executable, str(validator), '--analysis', args.analysis]
    validation = subprocess.run(validate_cmd, capture_output=True, text=True)
    if validation.returncode != 0:
        print(validation.stderr.strip(), file=sys.stderr)
        sys.exit(1)

    if args.lint:
        linter = Path(__file__).parent / 'lint_slides.py'
        lint_cmd = [sys.executable, str(linter), '--analysis', args.analysis]
        if args.lint_strict:
            lint_cmd.append('--strict')
        lint_result = subprocess.run(lint_cmd, capture_output=True, text=True)
        if lint_result.stdout.strip():
            print(lint_result.stdout.strip())
        if lint_result.returncode != 0:
            if lint_result.stderr.strip():
                print(lint_result.stderr.strip(), file=sys.stderr)
            sys.exit(1)
    
    slides = analysis.get('slides', [])
    
    # Check for existing images if deck directory provided
    if args.deck_dir:
        output_dir = Path(args.deck_dir)
        print(f"Checking for existing images in {output_dir}/public/images/...")
        slides = check_existing_images(slides, output_dir)
        print()
    
    # Render
    rendered = template.render(
        title=analysis.get('title', 'Presentation'),
        subtitle=analysis.get('subtitle', ''),
        author=analysis.get('author', ''),
        slides=slides,
        theme=analysis.get('theme', 'consulting'),
        primary_color='#003366',
        secondary_color='#6699CC'
    )
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    
    print(f"✓ Slides built: {args.output}")
    
    # Count images
    image_count = sum(1 for s in slides if s.get('visual', {}).get('type') == 'image')
    if image_count > 0:
        print(f"✓ {image_count} image(s) enabled in presentation")


if __name__ == '__main__':
    main()
