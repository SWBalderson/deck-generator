# deck-generate

Run the shared deck pipeline with a config file.

## Usage

- Place this file in `.cursor/commands/deck-generate.md`.
- Run in Cursor chat: `/deck-generate path/to/deck.config.json`

## Command Prompt

1. Confirm that the argument path exists.
2. Execute:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS"
```

3. Return:
- deck output path
- generated artifacts
- any failed step and the exact remediation command

## Partial rerun

Use this when slides exist and only build/export is needed:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS" --from-step build --to-step export
```
