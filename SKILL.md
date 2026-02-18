---
name: deck-generator
description: Generate professional consulting-style presentation decks from multiple document sources. Includes document ingestion, auto-detect chart types, MidJourney prompts, image optimization, and git tracking. Exports to PDF, PPTX, and SPA.
compatibility: opencode
---

# Deck Generator

Create professional consulting-style presentation decks from your documents.

## Features

- **Multi-format Ingestion**: PDF, DOCX, PPTX, XLSX, CSV, JSON, MD, TXT
- **Auto-detect Charts**: Automatically selects best chart type based on data
- **Chart.js Plugins**: Waterfall, Gantt, Harvey Balls, and more
- **Contextual MidJourney Prompts**: Analyzes slide content to generate relevant, non-repetitive visual prompts
- **Auto-Enable Images**: Automatically detects and enables images when placed in public/images/
- **Fixed Static Export**: Proper HTML rendering without code block issues
- **Image Optimization**: Auto-resizes and optimizes MidJourney images
- **Git Tracking**: Automatic git initialization and commits
- **Custom Themes**: Customizable for any organisation or consulting firm
- **Iterative Editing**: Regenerate specific slides or entire deck via prompts

## Workflow

This skill is the OpenCode adapter over a shared, host-neutral pipeline.

### Step 0: Collect Parameters

Collect required inputs in the host tool, then write a pipeline config JSON that matches:

- `schemas/pipeline-config.schema.json`

Required inputs:

1. `project_name`
2. `title`
3. `source_files` (array)
4. `output_root`

Common optional inputs:

- `theme`, `colors`, `logo_path`
- `subtitle`, `author`, `audience`
- `analysis_path` (required for detect/build/export stages)
- `export_formats`, `export_base`
- `execution` controls (`from_step`, `to_step`, `dry_run`, `git_mode`, lint toggles)

### Step 1: Run Shared Pipeline

Run the same core command used by all adapters:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Partial rerun examples:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
```

### Step 2: Analysis Handoff

The pipeline generates `analysis_request.json` from source files. Use your preferred LLM to produce `analysis.json`, then set `analysis_path` in config and rerun from `detect` onward.

### Step 3: Exports and Git Policy

- Exports are controlled via `export_formats` (`pdf`, `pptx`, `spa`).
- Git behavior is controlled by `execution.git_mode`:
  - `manual` (default)
  - `auto`
  - `off`

### Step 4: Tool-specific Adapters

See adapter templates:

- `adapters/opencode/README.md`
- `adapters/claude/commands/deck-generate.md`
- `adapters/cursor/commands/deck-generate.md`
- `adapters/codex/README.md`

## Iterative Editing

After viewing the presentation, request changes via prompt:

**Available Commands:**

- "Add a slide about [topic] after slide [N]"
- "Remove slide [N]"
- "Change the chart on slide [N] to [type]"
- "Update the title of slide [N] to [new title]"
- "Make slide [N] focus more on [aspect]"
- "Add a comparison table to slide [N]"
- "Update the data on slide [N] with [new data]"
- "Regenerate with emphasis on [theme]"
- "Lock slide [N]"
- "Unlock slide [N]"
- "Regenerate only slide [N]"
- "Optimise images" (runs image optimisation)
- "Export only [format]"
- "Show me the MidJourney prompts again"

**Process:**
1. User requests change
2. Skill updates slides.md and/or analysis.json
3. Apply locks/selective regeneration controls as needed
4. Skill regenerates affected charts
5. Skill re-exports all formats
6. Skill commits changes to git

Iterative controls helper:

```bash
python scripts/apply_iterative_controls.py \
  --base-analysis [deck_dir]/.temp/analysis.json \
  --new-analysis [deck_dir]/.temp/analysis.new.json \
  --output [deck_dir]/.temp/analysis.json \
  --locks-file [deck_dir]/.temp/slide-locks.json \
  --lock-slides 2 5 \
  --regenerate-only 4
```

## Manual Steps (User)

1. **Generate Images**: Use midjourney-prompts.md to create images in MidJourney (3 variations per slide)
2. **Place Images**: Save images to `[deck_dir]/public/images/` with exact filenames from prompts
3. **Rebuild**: Run build script to auto-enable images: `python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --deck-dir .`
4. **Re-export**: Run export commands or ask skill to export

**Tip**: Images are automatically detected and enabled. No manual uncommenting needed!

## Output Files

- `{project}_deck/` - Complete Slidev project
  - `slides.md` - Main presentation file
  - `public/images/` - Image folder (user-populated)
  - `public/data/` - Chart data files
  - `{project}.pdf` - PDF export
  - `{project}.pptx` - PowerPoint export
  - `dist/` - Static web app
  - `midjourney-prompts.md` - Image generation prompts
  - `.git/` - Version control

## Dependencies

**System:**
- Python 3.8+
- Node.js 18+
- Bun or npm

**Python packages:**
```bash
pip install docling pandas Pillow Jinja2
```

**Node packages:**
```bash
npm install -g @slidev/cli
```

**Per-deck export dependency:**
```bash
cd [deck_dir]
npm install -D playwright-chromium
```

## Custom Theme System

### Available Themes

- **Consulting** (default) - Professional navy/blue corporate theme
- **Local themes** (optional) - private themes loaded from `assets/themes-local/<theme-name>/`

### Creating Custom Themes

To create a theme for an organisation:

1. Provide:
   - Theme name
   - Primary color (hex) - for authority, trust, titles
   - Secondary color (hex) - for warmth, backgrounds
   - Accent color (hex) - for restrained highlights only
   - Logo file (SVG)
   - Font preferences (optional)

2. Skill generates:
    - `assets/themes/{theme-name}/theme.css`
    - `assets/themes/{theme-name}/uno.config.ts`
    - Theme documentation in README.md
    - Theme can be reused for future presentations

### Local-Only Themes (Private)

Use local-only themes when you want private branding while keeping the shared skill repository generic.

Directory structure:

```text
assets/themes-local/<theme-name>/theme.css
assets/themes-local/<theme-name>/uno.config.ts
```

Resolution order when a theme is requested:
1. `assets/themes/<theme-name>/`
2. `assets/themes-local/<theme-name>/`
3. fallback to `assets/themes/consulting/`

`assets/themes-local/*` is git-ignored (except the placeholder docs), so private themes can be used locally without being pushed.

Quick scaffold command:

```bash
python scripts/create_local_theme.py
```

Non-interactive mode is also supported with flags for automation.

## Recent Improvements

### v2.0 - Major Quality Improvements

**1. Fixed Static Export Rendering (Critical Fix)**
- **Problem**: HTML indentation in templates caused Slidev to render content as code blocks, resulting in blank slides
- **Solution**: Rewrote `templates/slides.md.jinja2` with proper whitespace control using Jinja2's `{%-` and `-%}` tags
- **Result**: Exports now render correctly with full HTML content visible

**2. Contextual MidJourney Prompts**
- **Problem**: All prompts were generic (chess pieces, abstract shapes) and didn't match slide content
- **Solution**: Implemented content analysis that categorizes slides and generates contextual prompts:
  - Academic content → scholarly/educational imagery
  - Boarding content → residential/campus imagery
  - Performing arts → stage/theatre imagery
  - Strategy → growth/pathway imagery
  - Finance → prosperity/business imagery
  - Data → analytics/network imagery
- **Result**: 3 unique prompt variations per slide, visually relevant to content

**3. Automatic Image Detection**
- **Problem**: Users had to manually uncomment image references in slides.md
- **Solution**: `build_slides.py` now:
  - Scans `public/images/` for existing images
  - Auto-enables images that exist
  - Hides missing images (prevents broken image icons)
  - Reports which images were found/missing
- **Result**: Just drop images in the folder and rebuild - no manual editing needed

**4. Improved Build Process**
- Added `--deck-dir` parameter to `build_slides.py` for image detection
- Better error handling and informative console output
- Template now handles missing images gracefully

### Usage Notes

**To rebuild with new images:**
```bash
python scripts/build_slides.py \
  --analysis .temp/analysis.json \
  --template templates/slides.md.jinja2 \
  --output slides.md \
  --deck-dir .
```

**To regenerate contextual prompts:**
```bash
python scripts/generate_midjourney_prompts.py \
  --analysis .temp/analysis.json \
  --output midjourney-prompts.md \
  --theme consulting
```

### Smoke Test (Maintainer)

Run full non-LLM smoke flow for regression checks:

```bash
./scripts/smoke_test.sh
```

### Fixture + Quality Regression (Maintainer)

Run fast fixture checks, including strict consulting-quality gate:

```bash
python scripts/run_fixture_checks.py
```

CI enforcement:
- `.github/workflows/ci.yml` runs compile checks, fixture checks, and smoke pipeline on push/PR.
