# Deck Generator

Turn your documents into polished, consulting-style presentation decks — automatically.

Feed in a collection of PDFs, spreadsheets, Word documents, or Markdown files and get back a complete [Slidev](https://sli.dev) presentation with data-driven charts, themed styling, MidJourney image prompts, speaker notes, and exports to PDF, PowerPoint, and the web.

The skill works with any AI coding tool — Cursor, Claude Code, OpenCode, or Codex — through a shared Python pipeline and thin tool-specific adapters.

## What It Does

1. **Ingests your documents** — PDF, DOCX, PPTX, XLSX, CSV, JSON, Markdown, plain text.
2. **Prepares an analysis request** — structured JSON ready for an LLM to propose slide titles, bullets, chart mappings, and layout choices.
3. **Detects the right chart types** — analyses data shape and context to pick between bar, line, pie, waterfall, Gantt, or Harvey Balls.
4. **Generates Chart.js configs** — maps source data to axes and applies your theme colours.
5. **Scaffolds a Slidev project** — installs dependencies, copies your theme, logo, and Vue components.
6. **Renders slides** — builds `slides.md` from a Jinja2 template, auto-enables any images you've placed in `public/images/`.
7. **Exports** — PDF, PPTX, or a static web app (SPA).
8. **Commits to git** — every generation is version-controlled so you can diff or rollback.

Along the way it also produces **contextual MidJourney prompts**, **speaker notes**, a **citation trace** mapping bullets back to source excerpts, and a **consulting-quality score** based on action titles, pyramid structure, MECE, minimalism, and data evidence.

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Slidev CLI
npm install -g @slidev/cli

# 3. Run the pipeline
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Or use the one-step installer that also copies adapter files for your tool of choice:

```bash
./scripts/install.sh --tool cursor --project-dir /path/to/your/project
```

## How the Pipeline Works

Everything flows through a single command:

```bash
python scripts/run_pipeline.py --config deck.config.json
```

The config file follows `schemas/pipeline-config.schema.json`. At minimum you need:

| Field | Description |
|-------|-------------|
| `project_name` | Slug like `q4-results` |
| `title` | Human-readable presentation title |
| `source_files` | Array of document paths |
| `output_root` | Directory where the deck folder is created |

The pipeline runs these steps in order:

```
ingest → analyse → detect → charts → project → build → export → commit → cleanup
```

After `analyse`, the pipeline produces `analysis_request.json`. You generate `analysis.json` from it using your preferred LLM, set `analysis_path` in config, then re-run from `detect`:

```bash
python scripts/run_pipeline.py --config deck.config.json --from-step detect
```

Other useful flags:

```bash
--from-step build --to-step export   # Partial re-run
--dry-run                            # Print steps without executing
```

## Tool Support

The core pipeline is tool-agnostic. Each AI coding tool gets a thin adapter that maps user input to the shared `run_pipeline.py` command.

| Tool | Adapter Location | Setup |
|------|-----------------|-------|
| **Cursor** | `adapters/cursor/` | Copy command + skill to `.cursor/` |
| **Claude Code** | `adapters/claude/` | Copy command to `.claude/commands/` |
| **Codex** | `AGENTS.md` | Already discoverable at repo root |
| **OpenCode** | `SKILL.md` | Already discoverable at skill root |

The install script handles this automatically:

```bash
./scripts/install.sh --tool all --project-dir /path/to/project
```

For Codex, the recommended sandbox config is:

```toml
# .codex/config.toml
[permissions]
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

## Charts

The skill auto-detects the best chart type from your data, or you can override per-slide with a `chart-overrides.json` file.

| Type | Best For |
|------|----------|
| Bar / Column | Categorical comparisons |
| Line | Time-series trends |
| Pie / Donut | Composition (up to 6 categories) |
| Waterfall | Value changes and bridges |
| Gantt | Project timelines |
| Harvey Balls | Qualitative assessments |

Chart mappings are driven by `visual.source_file`, `x_key`, `y_key`, and optional `series_key` fields in the analysis JSON. See `schemas/analysis.schema.json` for the full contract.

## Themes

The default theme is a professional consulting style (navy `#003366`, light blue `#6699CC`, accent `#FF6B35`). All colours are exposed as CSS variables — `--slide-primary`, `--slide-secondary`, `--slide-accent`, `--slide-text`, `--slide-text-light`, `--slide-grid` — so custom themes propagate automatically to charts and Vue components.

### Custom Colours via Config

Pass colour overrides directly in your pipeline config:

```json
{
  "colors": {
    "primary": "#0B2A4A",
    "secondary": "#5B7C99",
    "accent": "#D48A27"
  }
}
```

### Local / Private Themes

For branding that shouldn't be committed to the repository:

```bash
python scripts/create_local_theme.py --theme-name my-brand \
  --primary '#0B2A4A' --secondary '#5B7C99' --accent '#D48A27'
```

This scaffolds files under `assets/themes-local/my-brand/`, which is git-ignored. Theme resolution order: named theme → local theme → fallback to `consulting`.

## Audience Modes

Tune the tone and detail of the generated deck for its primary audience:

| Mode | Focus |
|------|-------|
| `board` | Strategic implications, risk, governance |
| `staff` | Implementation detail, operational ownership |
| `parents` | Plain-language outcomes, wellbeing impact |
| `mixed` | Balanced strategic and practical framing |

Set via `"audience": "board"` in your config.

## Quality Assurance

### Slide Linting

Basic checks on title quality, bullet counts, and source citations. Enable in config:

```json
{ "execution": { "lint": true, "lint_strict": false } }
```

### Consulting-Quality Scoring

A scored report (out of 100) based on five consulting principles:

| Category | Weight | Checks |
|----------|--------|--------|
| Action titles | 25 | Complete sentences with verbs and conclusions |
| Pyramid structure | 20 | Lead with the answer, support with evidence |
| MECE | 20 | Mutually exclusive, collectively exhaustive slide topics |
| Minimalism | 15 | 3–5 bullets per slide, no filler |
| Data evidence | 20 | Charts linked to source data, citations present |

Enable with `"consulting_lint": true` in the execution config. Score bands: 90+ Excellent, 75–89 Good, 60–74 Needs refinement, below 60 Rework recommended.

### Citation Traceability

Maps each slide bullet back to the source document excerpt it was drawn from:

```bash
python scripts/generate_citation_trace.py \
  --analysis .temp/analysis.json \
  --content .temp/content.json \
  --output citation-trace.json
```

## Iterative Editing

After generating a deck, you can refine it without starting over:

- **Lock slides** — protect specific slides from regeneration.
- **Regenerate only** — target individual slides for re-generation.
- **Merge** — combine new analysis with a base, respecting locks.

```bash
python scripts/apply_iterative_controls.py \
  --base-analysis .temp/analysis.json \
  --new-analysis .temp/analysis.new.json \
  --output .temp/analysis.json \
  --locks-file .temp/slide-locks.json \
  --lock-slides 2 5 \
  --regenerate-only 4
```

Then re-run the pipeline from `build` to pick up the changes.

## Output Structure

```
{project}_deck/
├── slides.md                    Main presentation file
├── public/
│   ├── images/                  Drop MidJourney images here
│   └── data/                    Auto-generated chart configs
├── components/                  Vue slide components
├── layouts/                     Slidev layouts
├── styles/                      Theme CSS
├── {project}.pdf                PDF export
├── {project}.pptx               PowerPoint export
├── dist/                        Static web app
├── midjourney-prompts.md        Image generation prompts
├── speaker-notes.md             Presenter notes
└── consulting-quality-report.json  Quality score report
```

## Testing

The project has three levels of testing:

```bash
# Unit tests (93 tests, runs in <1s)
python -m pytest tests/ -v

# Fixture regression checks (chart detection, generation, validation, linting)
python scripts/run_fixture_checks.py

# End-to-end smoke test (full pipeline minus LLM)
./scripts/smoke_test.sh
```

CI runs all three on every push and pull request via `.github/workflows/ci.yml`.

## Recent Changes

### Architecture Refactor

**Shared utilities module** — Duplicated functions (`build_content_index`, `extract_records`, `normalise_words`, `jaccard`, `to_float`, and others) have been extracted into `scripts/utils.py`. Five consumer scripts now import from this single module instead of maintaining their own copies.

**Direct function calls** — The pipeline orchestrator (`run_pipeline.py`) now imports and calls step functions in-process instead of spawning a new Python subprocess for each step. This eliminates 7 process spawns per full pipeline run, significantly reducing execution time. Validation and linting in `build_slides.py` also use direct imports rather than subprocess calls.

**Lazy imports and converter reuse** — Heavy dependencies (`docling`, `pandas`) are now imported lazily inside the functions that need them, so importing the pipeline module is fast. The `DocumentConverter` is instantiated once and reused across all files during ingestion.

### Cross-Tool Compatibility

**Cursor skill definition** — Added `adapters/cursor/skill/SKILL.md` with Cursor-friendly frontmatter and an improved command template that guides users through config creation.

**CLAUDE.md and AGENTS.md** — Added discovery files so Claude Code and Codex can find the skill and understand its workflow, sandbox requirements, and available scripts.

**Multi-tool install script** — `scripts/install.sh` automates dependency installation and adapter file placement for any supported tool.

### Quality and Testing

**Pytest suite** — 93 unit tests covering shared utilities, chart type detection, analysis validation (positive and negative cases), slide linting, consulting quality scoring, iterative controls, and speaker notes.

**Negative test fixtures** — Validation tests now cover invalid payloads: missing fields, wrong types, charts without data files, images without filenames, and invalid visual types.

**Requirements pinned** — `requirements.txt` with compatible version ranges for reproducible installs.

### Component Improvements

**CSS variable theming** — Hard-coded colour values in `DeckActionTitle`, `DeckSource`, `DeckHarveyBall`, `DeckWaterfall`, and the Jinja2 template have been replaced with CSS custom properties (`--slide-primary`, `--slide-secondary`, etc.) with sensible fallbacks. Custom themes now apply consistently everywhere.

**DeckWaterfall error handling** — The waterfall chart component now validates fetch responses, checks for missing or mismatched data, and displays a styled error message instead of silently failing.

**DeckLogo cleanup** — The logo candidate list has been trimmed from 20 entries to 8 (SVG and PNG only), and the component hides itself entirely when no logo resolves rather than leaving a broken image element.

## Dependencies

| Dependency | Purpose |
|-----------|---------|
| Python 3.8+ | Pipeline scripts |
| Node.js 18+ | Slidev rendering and export |
| [docling](https://github.com/DS4SD/docling) | PDF, DOCX, PPTX, HTML ingestion |
| [pandas](https://pandas.pydata.org/) | CSV and tabular data processing |
| [Pillow](https://python-pillow.org/) | Image optimisation |
| [Jinja2](https://jinja.palletsprojects.com/) | Slide template rendering |
| [pytest](https://docs.pytest.org/) | Unit testing |
| [@slidev/cli](https://sli.dev/) | Presentation rendering and export |
| playwright-chromium | PDF/PPTX export (per-deck install) |

## Licence

See repository root for licence terms.
