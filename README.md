# Deck Generator Skill

Professional consulting-style presentation generator using Slidev.

## Quick Start

```bash
# Install dependencies
pip install docling pandas Pillow Jinja2
npm install -g @slidev/cli

# Use the skill
# (Skill will guide you through the process)
```

For PDF and PPTX export rendering, install Playwright Chromium in each generated deck project:

```bash
npm install -D playwright-chromium
```

## Workflow

1. Place source documents in `source_docs/` folder
2. Run skill and answer questions
3. Generate MidJourney images using provided prompts
4. Place images in `public/images/`
5. Rebuild slides (images are auto-detected)
6. Re-export presentation

## Chart Types Supported

- **Bar/Column**: Categorical comparisons
- **Line**: Time series trends
- **Pie/Donut**: Composition (≤6 categories)
- **Waterfall**: Value changes/decomposition
- **Gantt**: Project timelines
- **Bubble**: 2x2 matrices
- **Harvey Balls**: Qualitative assessments

## Theme System

Default theme: Professional consulting (navy #003366, light blue #6699CC)

Create custom themes for organisations/firms:
- Colors auto-applied to all charts
- Logo appears on every slide
- Fonts customizable
- CSS variables for easy overrides

For local/private themes that should not be pushed to GitHub, use:

```text
assets/themes-local/<theme-name>/theme.css
assets/themes-local/<theme-name>/uno.config.ts
```

Theme resolution order:
1. `assets/themes/<theme-name>/`
2. `assets/themes-local/<theme-name>/`
3. fallback to `assets/themes/consulting/`

## Directory Structure

```
{project}_deck/
├── slides.md                    # Edit this file
├── public/
│   ├── images/                  # Add MidJourney images here
│   └── data/                    # Chart data (auto-generated)
├── components/                  # Vue components
├── layouts/                     # Slide layouts
├── styles/                      # Theme styles
├── {project}.pdf                # PDF export
├── {project}.pptx               # PowerPoint export
├── dist/                        # Static web app
└── midjourney-prompts.md        # Image prompts
```

## Git Integration

Every presentation is automatically tracked in git:
- Initial commit on creation
- Each regeneration creates a new commit
- View history: `git log`
- Rollback: `git checkout [commit]`

## Tips

- Use high-resolution logos (SVG preferred)
- Generate images at 1920x1080 or larger
- Keep source documents focused for better summaries
- Use iterative editing to refine the story

## Example Usage

```bash
# Create a presentation about Q4 results
# Place files in source_docs/:
#   - q4_strategy_brief.md
#   - market_data.csv
#   - competitor_analysis.pdf

# Run skill - it will:
# 1. Ask for project name (e.g., "q4-results")
# 2. Ingest all documents
# 3. Generate analysis and slide structure
# 4. Create charts and prompts
# 5. Export to all formats

# Output: q4-results_deck/ folder with:
# - q4-results.pdf
# - q4-results.pptx
# - dist/ (web version)
# - midjourney-prompts.md
```
