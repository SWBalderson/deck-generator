---
name: deck-generator
description: Generate professional consulting-style presentation decks from multiple document sources. Includes document ingestion, auto-detect chart types, MidJourney prompts, image optimisation, and git tracking. Exports to PDF, PPTX, and SPA.
---

# Deck Generator

Create professional consulting-style presentation decks from your documents.

## Features

- **Multi-format Ingestion**: PDF, DOCX, PPTX, XLSX, CSV, JSON, MD, TXT
- **Auto-detect Charts**: Automatically selects best chart type based on data
- **Chart.js Plugins**: Waterfall, Gantt, Harvey Balls, and more
- **Contextual MidJourney Prompts**: Analyses slide content for relevant visual prompts
- **Image Optimisation**: Auto-resizes and optimises MidJourney images
- **Git Tracking**: Automatic git initialisation and commits
- **Custom Themes**: Customisable for any organisation or consulting firm
- **Iterative Editing**: Regenerate specific slides or entire deck via prompts

## Workflow

This skill wraps a shared, host-neutral pipeline. All business logic lives in `scripts/`.

### Step 0: Collect Parameters

Collect these required inputs:

1. `project_name`
2. `title`
3. `source_files` (array of file paths)
4. `output_root` (directory for output)

Plus optional inputs: `theme`, `colors`, `logo_path`, `subtitle`, `author`, `audience`, `analysis_path`, `export_formats`, `export_base`.

Write a config JSON matching `schemas/pipeline-config.schema.json`.

### Step 1: Run Pipeline

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Partial rerun:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
```

### Step 2: Analysis Handoff

The pipeline generates `analysis_request.json` from source files. Use the LLM to produce `analysis.json`, then set `analysis_path` in config and rerun from `detect` onward.

### Step 3: Exports and Git

- Exports controlled via `export_formats` (`pdf`, `pptx`, `spa`).
- Git behaviour controlled by `execution.git_mode`: `manual` (default), `auto`, `off`.

## Cursor Command

A ready-made command file is available at `adapters/cursor/commands/deck-generate.md`.

To install, copy it to your project:

```bash
mkdir -p .cursor/commands
cp <skill-path>/adapters/cursor/commands/deck-generate.md .cursor/commands/
```

Then invoke with `/deck-generate path/to/deck.config.json` in Cursor chat.

## Dependencies

**Python:** `pip install -r requirements.txt`
**Node:** `npm install -g @slidev/cli`
**Per-deck export:** `cd [deck_dir] && npm install -D playwright-chromium`

## Output Files

- `{project}_deck/slides.md` — Main presentation
- `{project}_deck/public/images/` — User-populated image folder
- `{project}_deck/public/data/` — Chart data files
- `{project}_deck/{project}.pdf` — PDF export
- `{project}_deck/{project}.pptx` — PowerPoint export
- `{project}_deck/dist/` — Static web app
- `{project}_deck/midjourney-prompts.md` — Image generation prompts
