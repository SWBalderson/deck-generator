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

## Skill Authoring And Packaging

This repository keeps `README.md` at repo root for human documentation.

For Anthropic-style skill quality and distribution checks, see:

- `references/skill-trigger-guidelines.md`
- `references/skill-troubleshooting.md`
- `references/skill-evaluation-matrix.md`
- `references/distribution-packaging.md`
- `references/release-checklist.md`

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

## Presentation Principles

Every deck generated by this tool is designed around five principles drawn from professional consulting practice. These principles shape how the LLM is instructed to structure slides, how the linter scores the output, and how the iterative editing workflow guides you toward a stronger narrative.

### 1. Action Titles (weight: 25/100)

A slide title is not a label — it is the slide's conclusion. Readers who only skim the title strip should understand the full argument.

**The rule:** Every content slide title must be a complete sentence containing a decisive verb and ending with a period.

| Weak | Strong |
|------|--------|
| Revenue Overview | Revenue grew 18% year-on-year, driven by new product lines. |
| Market Position | The firm holds the largest market share in three of five segments. |
| Risks | Supply chain concentration creates material downside risk. |

**What the linter checks:**
- Title ends with a period (claim format, not label format).
- Title contains an action verb (improves, reduces, enables, drives, demonstrates, etc.).
- Title is longer than four words (guards against topic stubs like "Costs" or "Summary").
- Optionally flags titles that lack an implication signal (impact/result language) or a quantified outcome.

### 2. The Pyramid Principle (weight: 20/100)

Lead with the answer, then support it. The audience should hear the conclusion first and the evidence second — not wade through background before reaching the point.

**The rule:** The deck opens with an executive summary stating the core message. Each slide's first bullet directly supports the headline claim. The final substantive slide closes with explicit recommendations or next steps.

**How this works in practice:**
- The executive summary belongs at position 2 or 3 (immediately after the title slide). If the first substantive slide appears later than position 3, the linter flags the deck for burying the lead.
- Within each slide, the first bullet should contain the strongest evidence for the title's claim — ideally quantified or verb-led.
- The last substantive slide is checked for recommendation language (should, recommend, next step, priority, action, must).

**What the linter checks:**
- Executive conclusion slide appears early (positions 2–3).
- First bullet on each content slide contains supporting evidence with a detail field populated.
- Final substantive slide contains recommendation or next-step language.

### 3. MECE — Mutually Exclusive, Collectively Exhaustive (weight: 20/100)

Each slide should cover a distinct aspect of the argument. Topics should not overlap, and taken together they should cover the full scope of the story.

**The rule:** No two slides should be substantially about the same thing. Within a slide, bullets should not repeat each other. Sections (if used) should contain at least two supporting slides.

**What the linter checks:**
- **Slide-level overlap**: computes Jaccard similarity between the keyword sets of every pair of substantive slides. Pairs with similarity above 0.55 are flagged as potential duplication.
- **Bullet-level overlap**: checks whether bullets within a single slide share the same opening words, indicating repetition.
- **Section completeness**: if a section divider slide exists, at least two supporting slides should follow it.

**How to fix overlap flags:**
- Merge near-duplicate slides into one and sharpen the combined title.
- Split a vague slide into two distinct claims if the underlying content warrants it.
- Rewrite bullet openings to ensure each makes a different point.

### 4. Minimalist Design (weight: 15/100)

Slides are a visual medium. Dense text belongs in the speaker notes or a leave-behind document, not on the slide itself.

**The rule:** Content slides should have 3–5 bullets. Individual bullets should be concise (roughly 24 words or fewer). The total word count for a slide (title + all bullets) should stay below 120 words.

| Check | Threshold | Severity |
|-------|-----------|----------|
| Bullet count | 3–5 per content slide | Warning |
| Bullet length | ≤ 24 words each | Warning |
| Slide word count | ≤ 120 words total | Warning |
| Title length | ≤ 110 characters | Warning |

**How to fix density flags:**
- Move supporting detail into the `detail` field of the bullet (rendered smaller) or into speaker notes entirely.
- Split a dense slide into two slides with tighter scopes.
- Cut filler words — the linter rewards precision over verbosity.

### 5. Data Evidence (weight: 20/100)

Claims must be grounded. Every substantive slide should cite its source. Chart slides should map to real data. Numeric claims in titles need numeric support in the body.

**The rule:** Content, two-column, and chart-full slides must have a `source` field. Chart slides must specify `data_file`, `source_file`, `x_key`, and `y_key`. If the title contains a number, percentage, or currency symbol, the bullets or chart data should contain matching numeric evidence.

**What the linter checks:**
- Missing `source` citation on any evidence-led slide (blocking severity — the most impactful single fix).
- Missing chart mapping metadata (`data_file`, `source_file`, `x_key`, `y_key`) on chart slides (blocking).
- Chart slides without an explicit `insight` field summarising the key takeaway.
- Numeric claims in titles without numeric support in the body.
- When a citation trace is provided, a low match ratio (below 60% by default) is flagged.

### How the Principles Are Enforced

The principles are applied at three points in the pipeline:

1. **LLM instruction** — `analyze_content.py` embeds the principles directly in the prompt sent to the LLM, asking for action titles, MECE decomposition, 3–5 bullets per slide, source citations, and concrete chart mappings. This gives the best chance of a clean first pass.

2. **Basic slide lint** — `lint_slides.py` runs fast checks on title quality (period, verb), bullet count (3–5), and source citations. Enabled via `"lint": true` in config.

3. **Consulting-quality lint** — `lint_consulting_quality.py` runs the full scoring model across all five categories, producing a report with an overall score (out of 100), per-category breakdowns, blocking issues, warnings, and a ranked list of the top five fixes by impact.

### Enabling Quality Checks

In your pipeline config:

```json
{
  "execution": {
    "lint": true,
    "lint_strict": false,
    "consulting_lint": true,
    "consulting_lint_strict": false,
    "consulting_lint_threshold": 70
  }
}
```

| Flag | Effect |
|------|--------|
| `lint` | Run basic slide lint (title, bullets, sources) |
| `lint_strict` | Fail the build if any basic lint warnings exist |
| `consulting_lint` | Run full consulting-quality scoring |
| `consulting_lint_strict` | Fail the build if blocking issues exist or score is below threshold |
| `consulting_lint_threshold` | Minimum acceptable score in strict mode (default: 70) |

### Score Bands

| Score | Band | Meaning |
|-------|------|---------|
| 90–100 | Excellent | Ready for a senior audience with minimal revision |
| 75–89 | Good | Solid structure; minor refinements needed |
| 60–74 | Needs refinement | Several principles need attention before presenting |
| Below 60 | Rework recommended | Significant structural issues; revisit the narrative |

### Standalone Linting

You can run the linters directly without the full pipeline:

```bash
# Basic lint
python scripts/lint_slides.py --analysis .temp/analysis.json
python scripts/lint_slides.py --analysis .temp/analysis.json --strict

# Consulting-quality report
python scripts/lint_consulting_quality.py \
  --analysis .temp/analysis.json \
  --content .temp/content.json \
  --report-out consulting-quality-report.json

# Strict gate (fail if score < 70 or blocking issues exist)
python scripts/lint_consulting_quality.py \
  --analysis .temp/analysis.json \
  --content .temp/content.json \
  --strict --threshold 70
```

The report JSON contains `overall_score`, `overall_band`, `category_scores`, `category_penalties`, `blocking_issues`, `warnings`, `slide_findings`, and `recommended_fixes` (ranked by impact).

### Citation Traceability

Maps each slide bullet back to the source document excerpt it was drawn from, so you can verify that claims are grounded in the original material:

```bash
python scripts/generate_citation_trace.py \
  --analysis .temp/analysis.json \
  --content .temp/content.json \
  --output citation-trace.json
```

When a citation trace is available, the consulting-quality linter cross-references it to check that a sufficient proportion of bullets can be traced to source material.

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

MIT — see [LICENSE](LICENSE) for details.
