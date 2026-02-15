#!/usr/bin/env python3
"""
Optimize images for presentation (resize, compress).
"""

import argparse
import sys
from pathlib import Path
from PIL import Image


def optimize_image(input_path: Path, output_path: Path, max_width: int = 1920, quality: int = 85):
    """Optimize a single image."""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
        print(f"✓ Optimized: {input_path.name} -> {output_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Failed: {input_path.name} - {str(e)}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Optimize images')
    parser.add_argument('--input-dir', required=True, help='Input images directory')
    parser.add_argument('--output-dir', required=True, help='Output images directory')
    parser.add_argument('--max-width', type=int, default=1920, help='Max width in pixels')
    parser.add_argument('--quality', type=int, default=85, help='JPEG quality (1-100)')
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"✗ Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Process all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = [f for f in input_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    if not images:
        print("No images found to optimize")
        return 0
    
    success = 0
    failed = 0
    
    for img_path in images:
        output_path = output_dir / f"{img_path.stem}.jpg"
        if optimize_image(img_path, output_path, args.max_width, args.quality):
            success += 1
        else:
            failed += 1
            sys.exit(1)  # Stop on first error
    
    print(f"\n✓ Optimized {success} images | Failed {failed}")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
