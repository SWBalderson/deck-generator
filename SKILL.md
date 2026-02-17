---
name: deck-generator
description: Generate professional consulting-style presentation decks from multiple document sources. Includes document ingestion, auto-detect chart types, MidJourney prompts, image optimization, and git tracking. Exports to PDF, PPTX, and SPA.
compatability: opencode
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

### Step 0: Gather Parameters

Ask user via AskUserQuestion:

1. **Project Name**: "What would you like to name this presentation?"
   - Text input, used for folder naming
   - header: "Project Name"

2. **Theme**: "Which theme would you like to use?"
   - Options: "Consulting (default)", "Local theme by name", "Custom (specify colors)"
   - header: "Theme"

   If user chooses "Local theme by name", ask:
   - "Enter local theme name (folder name under assets/themes-local/)"
   - header: "Local Theme"

3. **Colors** (if custom): "Specify primary and secondary colors"
   - Options: "Primary hex color", "Secondary hex color"
   - header: "Colors"

4. **Logo**: "Path to your logo file (SVG recommended)"
   - Options: "Skip for now", "Custom SVG path"
   - header: "Logo"

5. **Document Files**: "Which documents should be included?"
   - Options: List all files in source_docs/ for multi-select
   - header: "Documents"

6. **Presentation Title**: "What is the presentation title?"
   - Text input
   - header: "Title"

7. **Subtitle/Author**: "Subtitle and author (optional)"
   - Text input
   - header: "Metadata"

8. **Output Formats**: "Which export formats?"
   - Options: "PDF", "PPTX", "SPA (web)", "All formats (recommended)"
   - header: "Export"

9. **Audience Mode**: "Who is the primary audience?"
   - Options: "Board", "Staff", "Parents", "Mixed"
   - header: "Audience"

### Step 1: Check Dependencies

Verify required dependencies are installed:
```bash
python3 --version  # >= 3.8
node --version     # >= 18
pip list | grep -E "docling|pandas|Pillow|Jinja2"
```

If missing, prompt user to install:
```bash
pip install docling pandas Pillow Jinja2
npm install -g @slidev/cli
```

Before exporting any deck to PDF/PPTX, ensure Playwright Chromium is installed in that deck project:

```bash
cd [deck_dir]
npm install -D playwright-chromium
```

### Step 2: Ingest Documents

Run: `python scripts/ingest_documents.py --files [file_list] --output .temp/content.json`

Supports: PDF, DOCX, PPTX, XLSX, CSV, JSON, MD, TXT, HTML

Stop on first error.

### Step 3: Analyze Content

Run helper (optional, recommended):
`python scripts/analyze_content.py --content .temp/content.json --audience [board|staff|parents|mixed] --output .temp/analysis_request.json`

Pass content.json to LLM:

"Analyze these documents and create a presentation structure with:

1. Executive summary slide
2. Section dividers where appropriate
3. Content slides with action titles (complete sentences)
4. Data visualization slides where data is present
5. Conclusion/next steps slide

For each slide, provide:
- Action title (complete sentence stating the main message)
- 3-5 bullet points with bold key phrases
- Chart type recommendation (or 'none')
- Data mapping fields when charted: `source_file`, `x_key`, `y_key`, optional `series_key`
- Data file reference for generated chart config (`data_file`, e.g. `chart_N.json`)
- MidJourney prompt concept
- Source citations

Follow consulting best practices:
- One message per slide
- MECE structure where applicable
- Pyramid principle (conclusion first)
- Data-driven insights
- Clear source attribution
- Use British English spelling and grammar by default (for example: "organisation", "optimise", "programme", "analyse")"

Return: structured JSON with slides array

### Step 4: Detect Chart Types

Run: `python scripts/detect_chart_type.py --analysis .temp/analysis.json --content .temp/content.json --overrides .temp/chart-overrides.json --output .temp/chart-types.json`

Auto-detects:
- Time series → Line chart
- Categorical comparison → Bar chart
- Composition → Pie/Donut
- Value changes → Waterfall
- Matrix data → Bubble
- Project timeline → Gantt

Stop on first error.

### Step 5: Generate Charts

Run: `python scripts/generate_charts.py --analysis .temp/analysis.json --types .temp/chart-types.json --content .temp/content.json --overrides .temp/chart-overrides.json --output [deck_dir]/public/data/ --theme [theme] --colors [colors]`

Generates Chart.js configurations with:
- Theme colors
- Responsive sizing
- Proper legends/labels
- Data from ingested files

Stop on first error.

### Step 6: Generate Contextual MidJourney Prompts

Run: `python scripts/generate_midjourney_prompts.py --analysis .temp/analysis.json --output [deck_dir]/midjourney-prompts.md --theme [theme]`

**New: Content-Aware Prompt Generation**

The prompt generator now analyzes each slide's content to create contextual visual prompts:

- **Academic/Education slides** → Library, scholarly, learning imagery
- **Boarding/Residential slides** → Campus, home, welcoming environments
- **Performing Arts slides** → Stage, theatre, musical instruments
- **Strategy/Vision slides** → Pathways, growth, forward-looking concepts
- **Revenue/Financial slides** → Growth, prosperity, business visualization
- **Data/Analytics slides** → Charts, networks, digital concepts
- **Community slides** → Connection, collaboration, shared spaces

Each slide gets 3 prompt variations with different visual approaches.

Stop on first error.

### Step 7: Create Slidev Project

Run: `python scripts/create_slidev_project.py --theme [theme] --colors [colors] --logo [logo] --output [deck_dir]/`

Scaffolds:
- Slidev project structure
- Custom layouts and components
- Theme CSS with selected colors
- UnoCSS configuration
- public/images/ folder (empty, ready for MidJourney images)
- public/data/ folder (with chart JSONs)
- Git repository initialised (`git init` + staged files)

Stop on first error.

### Step 8: Initialize Git Commit

Run:
```bash
cd [deck_dir]
# repository is already initialised by create_slidev_project.py
# ensure all generated files are staged
git add .
git commit -m "Initial deck structure"
```

Stop on first error.

### Step 9: Build Slides

Run: `python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output [deck_dir]/slides.md --deck-dir [deck_dir]`

Optional quality checks:
- Add `--lint` to show warnings without blocking build
- Add `--lint --lint-strict` to fail on lint warnings

Generates complete slides.md with:
- All slide content
- Chart component references
- **Auto-enabled images** (detects existing images in public/images/)
- Source citations

**New: Automatic Image Detection**

The build script now checks for existing images in `public/images/`:
- ✓ Images that exist are automatically enabled in the presentation
- ⚠ Missing images are hidden (no broken image icons)
- Just add your MidJourney images to the folder and rebuild

Stop on first error.

### Step 9b: Generate Speaker Notes (Optional)

Run:
`python scripts/generate_speaker_notes.py --analysis .temp/analysis.json --output [deck_dir]/speaker-notes.md`

Use `--style detailed` when you want fuller presenter talking points.

### Step 9c: Generate Citation Trace (Optional)

Run:
`python scripts/generate_citation_trace.py --analysis .temp/analysis.json --content .temp/content.json --output [deck_dir]/citation-trace.json`

This produces per-bullet source excerpt matches to improve evidence traceability.

### Step 10: Export

Run:
```bash
cd [deck_dir]
bunx slidev export --output [name].pdf --timeout 60000 --wait 1000
bunx slidev export --format pptx --output [name].pptx --timeout 60000 --wait 1000
bunx slidev build --out dist --base /
```

If Bun is unavailable, use `npx slidev ...` equivalents.

If using the helper script, validate analysis during export:

```bash
python scripts/export_deck.py --deck-dir [deck_dir] --analysis .temp/analysis.json --formats pdf pptx spa
```

Important: for static hosting under a subpath, set `--base` to a path that starts and ends with `/` (example: `/talks/q4-review/`).

Stop on first error.

### Step 11: Commit

Run:
```bash
cd [deck_dir]
git add .
git commit -m "[deck-generator] Initial presentation generation"
```

### Step 12: Cleanup

Remove .temp/ folder:
```bash
rm -rf .temp/
```

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
