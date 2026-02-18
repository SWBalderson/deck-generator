# Deck Generator Skill

Professional consulting-style presentation generator using Slidev.

## Quick Start

```bash
# Install dependencies
pip install docling pandas Pillow Jinja2
npm install -g @slidev/cli

# Run compatibility smoke check (schema + dry-run)
./scripts/smoke_compat.sh
```

## Canonical Cross-Tool Workflow

All tools should use the same core pipeline command:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Config contract:

- `schemas/pipeline-config.schema.json`

Starter config:

- `examples/configs/cross-tool-minimal.json`

Partial reruns:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
```

If your flow includes detect/build/export, provide `analysis_path` in config after generating `analysis.json` from `analysis_request.json`.

## Tool Adapter Quickstarts

- OpenCode: `adapters/opencode/README.md`
- Claude Code: `adapters/claude/commands/deck-generate.md`
- Cursor: `adapters/cursor/commands/deck-generate.md`
- Codex CLI: `adapters/codex/README.md`

### Cursor command location

Place project commands in `.cursor/commands/*.md` and invoke them with `/` in Cursor chat.

### Codex safety defaults

Use project-level `.codex/config.toml` with explicit approval and sandbox settings, for example:

```toml
[permissions]
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

For PDF and PPTX export rendering, install Playwright Chromium in each generated deck project:

```bash
npm install -D playwright-chromium
```

## Workflow

1. Create config JSON matching `schemas/pipeline-config.schema.json`
2. Run `python scripts/run_pipeline.py --config <config.json>`
3. Generate `analysis.json` from `analysis_request.json` when required
4. Re-run from `detect` onward once `analysis_path` is set
5. Generate MidJourney images using provided prompts
6. Place images in `public/images/`
7. Rebuild/export (for example `--from-step build --to-step export`)

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

## Audience Modes

Tune deck tone and detail for the primary audience:

- `board` - strategic implications, risk, and governance decisions
- `staff` - implementation detail and operational ownership
- `parents` - plain-language outcomes and wellbeing impact
- `mixed` - balanced strategic and practical framing

Helper script example:

```bash
python scripts/analyze_content.py --content .temp/content.json --audience board --output .temp/analysis_request.json
```

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

Optional quality linting:

```bash
python scripts/lint_slides.py --analysis .temp/analysis.json
python scripts/lint_slides.py --analysis .temp/analysis.json --strict
```

Or run during build:

```bash
python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --lint
python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --lint --lint-strict
```

Advanced consulting-quality linting (scored report):

```bash
python scripts/lint_consulting_quality.py --analysis .temp/analysis.json --content .temp/content.json --report-out .temp/consulting-quality-report.json
python scripts/lint_consulting_quality.py --analysis .temp/analysis.json --content .temp/content.json --strict --threshold 70
```

Consulting-quality score model (100 points):

- `action_titles`: 25
- `pyramid`: 20
- `mece`: 20
- `minimalist`: 15
- `data_evidence`: 20

Severity bands:

- `90-100`: Excellent
- `75-89`: Good
- `60-74`: Needs refinement
- `<60`: Rework recommended

The report JSON includes:

- `overall_score`, `overall_band`
- `category_scores`, `category_penalties`
- `blocking_issues`, `warnings`
- `slide_findings`
- `recommended_fixes` (ranked by impact)

Or run during build:

```bash
python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --consulting-lint --content .temp/content.json
python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --consulting-lint --consulting-lint-strict --consulting-lint-threshold 70 --content .temp/content.json
```

## Speaker Notes

Generate presenter notes from analysis output:

```bash
python scripts/generate_speaker_notes.py --analysis .temp/analysis.json --output speaker-notes.md
python scripts/generate_speaker_notes.py --analysis .temp/analysis.json --output speaker-notes.md --style detailed
```

## Citation Traceability

Generate a bullet-to-source citation trace file:

```bash
python scripts/generate_citation_trace.py --analysis .temp/analysis.json --content .temp/content.json --output citation-trace.json
```

This creates slide-by-slide citation mappings with matched source excerpts where keyword overlap is sufficient.

## Iterative Slide Controls

Preserve locked slides and selectively regenerate only chosen slides:

```bash
python scripts/apply_iterative_controls.py \
  --base-analysis .temp/analysis.json \
  --new-analysis .temp/analysis.new.json \
  --output .temp/analysis.json \
  --locks-file .temp/slide-locks.json \
  --lock-slides 2 5 \
  --regenerate-only 4
```

Use `--unlock-slides` to remove locks.

## Smoke Test

Run an end-to-end smoke pipeline (ingest -> analyse helper -> detect -> chart -> build -> export SPA):

```bash
./scripts/smoke_test.sh
```

Optional custom work directory:

```bash
./scripts/smoke_test.sh /tmp/deck-generator-smoke
```

## Fixture Checks

Run fast fixture regressions:

```bash
python scripts/run_fixture_checks.py
```

CI runs both fixture checks and the smoke pipeline on push/PR via `.github/workflows/ci.yml`.
Fixture checks include a strict consulting-quality linter pass on `examples/fixtures/consulting-quality-good.json`.

To run the same strict gate locally:

```bash
python scripts/lint_consulting_quality.py \
  --analysis examples/fixtures/consulting-quality-good.json \
  --content .temp/content.json \
  --strict \
  --threshold 70
```

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
