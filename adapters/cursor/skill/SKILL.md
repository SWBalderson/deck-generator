---
name: deck-generator
description: Generate consulting-style decks from source documents using the shared pipeline. Use when users ask to create a presentation from files, regenerate specific slides, or export to pdf, pptx, or spa. Not for standalone image design requests.
compatibility: cursor; requires Python 3.8+, Node.js 18+, filesystem write access, shell access, and network access for package installation.
metadata:
  author: deck-generator maintainers
  version: 2.1.0
  category: workflow-automation
  support: ../../../AGENTS.md
---

# Deck Generator (Cursor)

Thin adapter for the shared deck pipeline.

## Required Inputs

Create a config JSON matching `schemas/pipeline-config.schema.json` with:

1. `project_name`
2. `title`
3. `source_files`
4. `output_root`

## Core Commands

Run full pipeline:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

Continue after `analyze`:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step detect
```

Partial rerun:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
```

## Cursor Command

Install command file from `adapters/cursor/commands/deck-generate.md`, then run:

`/deck-generate path/to/deck.config.json`

## Troubleshooting

- If pipeline stops after `analyze`, provide `analysis_path` and rerun from `detect`.
- If export fails, install `playwright-chromium` inside the deck directory.
- If validation fails, run `python scripts/validate_analysis.py --analysis <analysis.json>`.

## References

- `../../../references/skill-trigger-guidelines.md`
- `../../../references/skill-troubleshooting.md`
- `../../../references/skill-evaluation-matrix.md`
- `../../../references/distribution-packaging.md`
