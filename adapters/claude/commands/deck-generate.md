---
description: Generate a presentation deck from config
argument-hint: [config-path]
allowed-tools: Bash(python:*), Read
---

Use the shared deck-generator pipeline with config `$1`:

1. Validate config path and schema with dry run: !`python scripts/run_pipeline.py --config "$1" --dry-run`
2. Run pipeline: !`python scripts/run_pipeline.py --config "$1"`
3. Report:
   - Deck output directory
   - Exported formats
   - Any failures and next actions

If caller asks for partial rerun, run:

!`python scripts/run_pipeline.py --config "$1" --from-step build --to-step export`
