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
3. Skill creates a Slidev project (including `git init` and initial staging)
4. Generate MidJourney images using provided prompts
5. Place images in `public/images/`
6. Rebuild slides (images are auto-detected)
7. Re-export presentation

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

For custom colour overrides, pass JSON to both project scaffolding and chart generation:

```bash
python scripts/create_slidev_project.py --theme consulting --colors '{"primary":"#0B2A4A","secondary":"#5B7C99"}' --output my-deck
python scripts/generate_charts.py --analysis .temp/analysis.json --types .temp/chart-types.json --content .temp/content.json --overrides .temp/chart-overrides.json --output my-deck/public/data --theme consulting --colors '{"primary":"#0B2A4A","secondary":"#5B7C99"}'
```

For local/private themes that should not be pushed to GitHub, use:

```text
assets/themes-local/<theme-name>/theme.css
assets/themes-local/<theme-name>/uno.config.ts
```

Theme resolution order:
1. `assets/themes/<theme-name>/`
2. `assets/themes-local/<theme-name>/`
3. fallback to `assets/themes/consulting/`

### Create a Local Theme (Recommended)

Use the helper script to scaffold a local theme quickly (interactive wizard):

```bash
python scripts/create_local_theme.py
```

Or non-interactively:

```bash
python scripts/create_local_theme.py \
  --theme-name my-brand \
  --primary '#0B2A4A' \
  --secondary '#5B7C99' \
  --accent '#D48A27'
```

This creates:

```text
assets/themes-local/my-brand/theme.css
assets/themes-local/my-brand/uno.config.ts
```

Then run the skill and choose **Local theme by name** with `my-brand`.

### Manual Local Theme Format

If you prefer manual setup, create these files directly:

```text
assets/themes-local/<theme-name>/theme.css
assets/themes-local/<theme-name>/uno.config.ts
```

At minimum, define these CSS variables in `theme.css`:
- `--slide-primary`
- `--slide-secondary`
- `--slide-accent`
- `--slide-background`
- `--slide-text`

Important:
- `assets/themes-local/*` is git-ignored (except docs placeholders), so private themes stay local.
- If a local theme is missing required files, the skill falls back to `consulting`.

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
- Repository initialised and files staged on project creation
- Initial commit after first full generation/export
- Each regeneration creates a new commit
- View history: `git log`
- Rollback: `git checkout [commit]`

## Tips

- Use high-resolution logos (SVG preferred)
- Logo autodetection supports both `public/logo.*` and `public/images/logo.*`
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

## Chart Fixtures

Use these fixtures to validate chart rendering compatibility:

- `examples/fixtures/chart-data-only.json` - legacy data-only shape
- `examples/fixtures/chart-full-config.json` - full Chart.js config shape
- `examples/fixtures/detect-timeseries.json` - expected detection: `line`
- `examples/fixtures/detect-composition.json` - expected detection: `pie`/`donut`
- `examples/fixtures/detect-waterfall.json` - expected detection: `waterfall`
- `examples/fixtures/analysis-mapped-sample.json` + `content-mapped-sample.json` + `chart-types-mapped-sample.json` - source-to-chart mapping fixture
- `examples/fixtures/chart-overrides-sample.json` - manual override fixture format

## Validation

Validate `analysis.json` before build/export:

```bash
python scripts/validate_analysis.py --analysis .temp/analysis.json
```

`scripts/build_slides.py` now runs this validation automatically.

## Analysis Chart Mapping Contract

When a slide requests a chart, include these fields in `slide.visual`:

- `source_file`: source dataset filename from ingestion
- `x_key`: column/key for x-axis labels
- `y_key`: column/key for values
- `series_key` (optional): grouping field for multi-series charts
- `data_file`: generated chart config output (for example `chart_5.json`)

Optional override file (`chart-overrides.json`) can force chart type and mapping by slide id:

```json
{
  "slide_3": {
    "chart_type": "bar",
    "source_file": "school-metrics.csv",
    "x_key": "term",
    "y_key": "attendance"
  }
}
```

Schema reference: `schemas/analysis.schema.json`
