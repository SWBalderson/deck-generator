---
name: deck-generator
description: Generate consulting-style presentation decks from source documents with charts and exports. Use when users ask to create a deck, turn docs into slides, build a board or staff presentation, regenerate specific slides, or export to pdf, pptx, or spa. Not for one-off image design or simple single-chart questions.
compatibility: opencode; requires Python 3.8+, Node.js 18+, filesystem write access, shell access, and network access for package installation.
metadata:
  author: deck-generator maintainers
  version: 2.1.0
  category: workflow-automation
  support: ./AGENTS.md
---

# Deck Generator

Generate consulting-style Slidev decks from mixed document sources using a shared pipeline.

## Use This Skill When

- User asks to create a full presentation from files.
- User asks to regenerate slides, apply slide locks, or rerun build/export.
- User asks for deck exports (`pdf`, `pptx`, `spa`) from a project config.

## Do Not Use This Skill When

- The task is a single static graphic, poster, or isolated visual without deck generation.
- The user only needs generic writing help unrelated to pipeline outputs.

## Required Inputs

Create a config JSON that matches `schemas/pipeline-config.schema.json` with:

1. `project_name`
2. `title`
3. `source_files` (array)
4. `output_root`

Common optional fields:

- `theme`, `colors`, `logo_path`
- `subtitle`, `author`, `audience`
- `analysis_path` (required after `analyze`)
- `export_formats`, `export_base`
- `execution` controls (`from_step`, `to_step`, `dry_run`, `git_mode`, lint toggles)

## Workflow

1. Run pipeline:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

2. If pipeline stops after `analyze`, generate `analysis.json` from `analysis_request.json`, set `analysis_path`, then continue:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step detect
```

3. For partial reruns:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
```

4. Exports and git mode:

- `export_formats`: `pdf`, `pptx`, `spa`
- `execution.git_mode`: `manual` (default), `auto`, `off`

## Iterative Edits

Use targeted edits where possible (lock slides, regenerate specific slides) instead of full regeneration.

```bash
python scripts/apply_iterative_controls.py \
  --base-analysis [deck_dir]/.temp/analysis.json \
  --new-analysis [deck_dir]/.temp/analysis.new.json \
  --output [deck_dir]/.temp/analysis.json \
  --locks-file [deck_dir]/.temp/slide-locks.json \
  --lock-slides 2 5 \
  --regenerate-only 4
```

## Manual User Step For Images

1. Generate images from `midjourney-prompts.md`.
2. Save files in `[deck_dir]/public/images/` using expected filenames.
3. Rebuild to auto-enable available images.

```bash
python scripts/build_slides.py --analysis .temp/analysis.json --template templates/slides.md.jinja2 --output slides.md --deck-dir .
```

## Critical Troubleshooting

- Missing `analysis_path` after `analyze`: set `analysis_path` in config, rerun from `detect`.
- Export dependency errors: install `playwright-chromium` in deck directory.
- Chart/schema validation errors: run `python scripts/validate_analysis.py --analysis <analysis.json>` and fix required fields.

For complete playbooks and diagnostics, use the reference docs below.

## References

- `references/skill-trigger-guidelines.md`
- `references/skill-troubleshooting.md`
- `references/skill-evaluation-matrix.md`
- `references/distribution-packaging.md`
- `adapters/opencode/README.md`
- `adapters/claude/commands/deck-generate.md`
- `adapters/cursor/commands/deck-generate.md`
- `adapters/codex/README.md`
