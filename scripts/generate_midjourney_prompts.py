#!/usr/bin/env python3
"""
Generate contextual MidJourney prompts based on slide content analysis.
"""

import argparse
import json
from pathlib import Path


PROMPT_TEMPLATES = {
    'academic': {
        'keywords': ['academic', 'education', 'learning', 'school', 'pupil', 'student', 'study', 'knowledge', 'excellence', 'curriculum', 'pathway'],
        'templates': [
            "Elegant academic setting, books and knowledge symbols, warm library atmosphere with soft lighting. {primary} and {secondary} color tones. Scholarly, aspirational mood. Clean, minimal composition. No text.",
            "Abstract education concept, geometric books and learning symbols, upward growth visualization. {primary} primary with {secondary} accents. Professional, clean design. No text or numbers.",
            "Modern classroom or study environment, focused learning atmosphere, warm natural light. {primary} and {secondary} sophisticated palette. Inspirational, calm mood. No people, no text."
        ]
    },
    'boarding': {
        'keywords': ['boarding', 'residential', 'accommodation', 'home', 'family', 'stay', 'overnight', 'flexible', 'welfare', 'pastoral'],
        'templates': [
            "Serene residential campus scene, traditional architecture with modern comforts, welcoming atmosphere. {primary} and {secondary} color scheme. Warm, safe, inviting mood. Golden hour lighting. No text.",
            "Cozy dormitory or residential hall interior, comfortable living space, homely environment. {primary} and {secondary} warm tones. Comfort, security, belonging mood. No people, no text.",
            "Abstract home-away-from-home concept, welcoming door or window imagery, warmth and care symbolism. {primary} primary with {secondary} accents. Trustworthy, nurturing atmosphere. No text."
        ]
    },
    'performing_arts': {
        'keywords': ['performance', 'arts', 'dance', 'drama', 'music', 'theatre', 'stage', 'creative', 'ensemble', 'academy', 'talent'],
        'templates': [
            "Elegant stage or performance venue, dramatic spotlighting, artistic atmosphere. {primary} and {secondary} with theatrical lighting. Creative, inspiring, professional mood. No performers, no text.",
            "Musical instruments or dance studio abstract, flowing movement suggestion, artistic expression. {primary} primary with {secondary} and subtle {accent} highlights. Sophisticated, cultured atmosphere. No text.",
            "Grand concert hall or theatre interior, ornate architecture, artistic excellence. {primary} and {secondary} elegant palette. Aspirational, prestigious mood. No people, no text."
        ]
    },
    'strategy': {
        'keywords': ['strategy', 'vision', 'plan', 'growth', 'future', 'development', 'goal', 'mission', 'strategic'],
        'templates': [
            "Abstract strategic visualization, geometric pathways leading upward, clear direction concept. {primary} primary with {secondary} accents. Forward-looking, purposeful mood. Clean, minimal design. No text.",
            "Futuristic horizon or pathway visualization, journey toward success, aspirational imagery. {primary} and {secondary} sophisticated tones. Hopeful, determined atmosphere. No text or numbers.",
            "Abstract compass or navigation concept, clear direction and purpose symbolism. {primary} primary with gold or amber accent. Thoughtful, confident mood. Minimal, professional design. No text."
        ]
    },
    'revenue': {
        'keywords': ['revenue', 'financial', 'income', 'business', 'commercial', 'monetize', 'profit', 'economic', 'sustainable', 'diversification'],
        'templates': [
            "Abstract growth and prosperity visualization, upward trending geometric shapes, success concept. {primary} primary with {secondary} accents. Optimistic, professional mood. Clean, minimal design. No text or numbers.",
            "Sophisticated business growth concept, abstract financial stability imagery, trustworthy aesthetic. {primary} and {secondary} corporate palette. Reliable, prosperous atmosphere. No text.",
            "Diversified streams or multiple pathways concept, branching success visualization. {primary} primary with {secondary} elements. Strategic, balanced mood. No text or numbers."
        ]
    },
    'data': {
        'keywords': ['data', 'analytics', 'metrics', 'insight', 'monitoring', 'measurement', 'statistics', 'digital'],
        'templates': [
            "Abstract data visualization concept, elegant chart or graph elements, analytical sophistication. {primary} and {secondary} tech-forward palette. Clean, intelligent, precise mood. No text or numbers.",
            "Digital transformation visualization, flowing data streams, modern analytical aesthetic. {primary} primary with {secondary} accents. Professional, innovative atmosphere. No text.",
            "Geometric network or connected nodes, information flow concept, intelligent systems. {primary} and {secondary} sophisticated tones. Insightful, modern mood. No text or numbers."
        ]
    },
    'community': {
        'keywords': ['community', 'partnership', 'collaboration', 'stakeholder', 'together', 'network', 'relationship', 'engagement'],
        'templates': [
            "Abstract community connection concept, intersecting pathways or shared space, unity symbolism. {primary} primary with {secondary} accents. Warm, collaborative, inclusive mood. No people, no text.",
            "Interlocking geometric shapes or shared foundation concept, partnership and support imagery. {primary} and {secondary} harmonious palette. Trustworthy, connected atmosphere. No text.",
            "Converging pathways or meeting point abstraction, shared purpose visualization. {primary} primary with {secondary} elements. Welcoming, unified mood. No text."
        ]
    },
    'default': {
        'templates': [
            "Professional consulting presentation graphic, abstract geometric visualization, corporate sophistication. {primary} primary with {secondary} accents. Clean minimalist design. No text, no numbers.",
            "Elegant abstract composition, balanced geometric forms, professional aesthetic. {primary} and {secondary} sophisticated palette. Calm, authoritative mood. No text.",
            "Abstract organizational concept, structured yet dynamic forms, institutional excellence. {primary} primary with {secondary} elements. Trustworthy, established atmosphere. No text."
        ]
    }
}


def analyze_slide_content(title: str, bullets: list) -> str:
    """Analyze slide content to determine the best visual category."""
    content = title.lower()
    for bullet in bullets:
        if isinstance(bullet, dict):
            content += ' ' + bullet.get('main', '').lower()
            content += ' ' + bullet.get('detail', '').lower()
        elif isinstance(bullet, str):
            content += ' ' + bullet.lower()
    
    # Score each category based on keyword matches
    scores = {}
    for category, data in PROMPT_TEMPLATES.items():
        if category == 'default':
            continue
        score = 0
        keywords = data.get('keywords', [])
        for keyword in keywords:
            if keyword in content:
                score += 1
        scores[category] = score
    
    # Return category with highest score, or default if no matches
    if scores:
        best_category = max(scores.items(), key=lambda x: x[1])[0]
        if scores[best_category] > 0:
            return best_category
    
    return 'default'


def generate_contextual_prompt(slide: dict, theme_colors: dict, variation: int = 0) -> tuple[str, str]:
    """Generate a contextual MidJourney prompt based on slide content."""
    title = slide.get('title', '')
    bullets = slide.get('bullets', [])
    
    # Analyze content to determine category
    category = analyze_slide_content(title, bullets)
    category_data = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES['default'])
    
    # Select template based on variation
    templates = category_data.get('templates', PROMPT_TEMPLATES['default']['templates'])
    template = templates[variation % len(templates)]
    
    # Format with theme colors
    formatted = template.format(
        primary=theme_colors['primary'],
        secondary=theme_colors['secondary'],
        accent=theme_colors.get('accent', theme_colors['secondary'])
    )
    
    return formatted, category


def get_theme_colors(theme: str) -> dict:
    """Get theme colors for prompt generation."""
    themes = {
        'consulting': {
            'primary': '#003366 (Navy Blue)',
            'secondary': '#6699CC (Light Blue)',
            'accent': '#FF6B35 (Coral)'
        }
    }
    
    # Default to consulting if theme not found
    return themes.get(theme, themes['consulting'])


def generate_prompts_for_slide(slide: dict, slide_num: int, theme_colors: dict) -> list:
    """Generate multiple prompt variations for a slide."""
    prompts = []
    title = slide.get('title', '')
    
    # Generate 3 variations
    for variation in range(3):
        prompt_text, category = generate_contextual_prompt(slide, theme_colors, variation)
        prompts.append({
            'variation': variation + 1,
            'category': category,
            'prompt': f"{prompt_text} --ar 16:9 --style raw --v 6"
        })
    
    return prompts


def main():
    parser = argparse.ArgumentParser(description='Generate contextual MidJourney prompts')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--output', required=True, help='Output markdown file')
    parser.add_argument('--theme', default='consulting', help='Theme name')
    args = parser.parse_args()
    
    # Load theme colors
    colors = get_theme_colors(args.theme)
    
    # Load analysis
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # Generate prompts - ONLY for slides with visual.type == 'image'
    output_lines = [
        "# MidJourney Prompts",
        "",
        f"Theme: {args.theme}",
        f"Colors: Primary={colors['primary']}, Secondary={colors['secondary']}, Accent={colors['accent']}",
        "",
        "## Instructions",
        "",
        "1. Review the content analysis for each slide below",
        "2. Copy the desired prompt variation into MidJourney",
        "3. Generate 4 variations in MidJourney",
        "4. Select the best image and save to `public/images/` with the exact filename shown",
        "5. The slide will automatically display the image when it exists",
        "",
        "---",
        ""
    ]
    
    slides = analysis.get('slides', [])
    image_slides = []
    
    # Filter only slides that need images
    for i, slide in enumerate(slides):
        slide_num = i + 1
        visual = slide.get('visual', {})
        
        # Only generate prompts for slides explicitly marked as image type
        if visual.get('type') == 'image' and visual.get('filename'):
            image_slides.append((slide_num, slide))
    
    if not image_slides:
        output_lines.append("*No slides requiring images were found in the presentation structure.*")
        output_lines.append("")
        output_lines.append("To add images to a slide, ensure the analysis.json has:")
        output_lines.append("```json")
        output_lines.append('"visual": {')
        output_lines.append('  "type": "image",')
        output_lines.append('  "filename": "slide-XX-category.png"')
        output_lines.append('}')
        output_lines.append("```")
    else:
        output_lines.append(f"## Generated Prompts for {len(image_slides)} Slide(s)")
        output_lines.append("")
        
        for slide_num, slide in image_slides:
            visual = slide.get('visual', {})
            filename = visual.get('filename', f'slide-{slide_num:02d}-default.png')
            title = slide.get('title', 'Untitled')
            bullets = slide.get('bullets', [])
            
            # Analyze content
            category = analyze_slide_content(title, bullets)
            
            output_lines.append(f"### Slide {slide_num}: {title}")
            output_lines.append("")
            output_lines.append(f"**Content Category:** {category.replace('_', ' ').title()}")
            output_lines.append("")
            output_lines.append(f"**Save as:** `{filename}`")
            output_lines.append("")
            
            # Generate multiple variations
            prompts = generate_prompts_for_slide(slide, slide_num, colors)
            
            for prompt_data in prompts:
                output_lines.append(f"**Variation {prompt_data['variation']}:**")
                output_lines.append("```")
                output_lines.append(prompt_data['prompt'])
                output_lines.append("```")
                output_lines.append("")
            
            output_lines.append("---")
            output_lines.append("")
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"✓ Generated {len(image_slides)} contextual MidJourney prompts: {output_path}")
    if image_slides:
        categories = set()
        for _, slide in image_slides:
            category = analyze_slide_content(slide.get('title', ''), slide.get('bullets', []))
            categories.add(category)
        print(f"✓ Content categories detected: {', '.join(sorted(categories))}")


if __name__ == '__main__':
    main()
