# Deck Generator — Claude Code Guide

This project is a professional consulting-style presentation generator using Slidev.

## Quick Start

```bash
pip install -r requirements.txt
npm install -g @slidev/cli
```

## Core Command

All workflows use the same pipeline entrypoint:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Config must conform to `schemas/pipeline-config.schema.json`.

## Slash Command

A ready-made Claude Code command is available at `adapters/claude/commands/deck-generate.md`.

To install into your project:

```bash
mkdir -p .claude/commands
cp adapters/claude/commands/deck-generate.md .claude/commands/
```

Then use: `/deck-generate path/to/deck.config.json`

## Workflow

1. Create a config JSON with `project_name`, `title`, `source_files`, and `output_root`.
2. Run the pipeline: `python scripts/run_pipeline.py --config <config.json>`
3. The pipeline produces `analysis_request.json`. Generate `analysis.json` from it and set `analysis_path` in config.
4. Rerun from `detect`: `python scripts/run_pipeline.py --config <config.json> --from-step detect`
5. Export formats are controlled by `export_formats` in config (`pdf`, `pptx`, `spa`).

## Key Directories

- `scripts/` — All pipeline logic (Python)
- `schemas/` — JSON schemas for config and analysis validation
- `assets/` — Vue components, layouts, and themes
- `templates/` — Jinja2 slide template
- `examples/` — Demo source docs and fixture data
- `adapters/` — Tool-specific adapter templates (Claude, Cursor, Codex, OpenCode)

## Testing

```bash
python scripts/run_fixture_checks.py        # Fast fixture regressions
./scripts/smoke_test.sh                      # Full end-to-end smoke test
./scripts/smoke_compat.sh                    # Schema + dry-run validation
```
