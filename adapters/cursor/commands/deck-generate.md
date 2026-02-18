# deck-generate

Run the shared deck-generator pipeline with a config file.

## Usage

- Place this file in `.cursor/commands/deck-generate.md`.
- Run in Cursor chat: `/deck-generate path/to/deck.config.json`

## Command Prompt

1. If no argument is provided, help the user create a config JSON matching `schemas/pipeline-config.schema.json`. Ask for:
   - `project_name` (slug, e.g. `q4-results`)
   - `title` (presentation title)
   - `source_files` (list of document paths)
   - `output_root` (where to create the deck)
   - Optionally: `theme`, `audience`, `colors`, `logo_path`

   Write the config to `deck.config.json` in the workspace root.

2. Confirm that the config file exists and validate it:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS" --dry-run
```

3. Execute the full pipeline:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS"
```

4. Return:
   - Deck output path
   - Generated artefacts
   - Any failed step and the exact remediation command

## Partial Rerun

Use this when slides exist and only build/export is needed:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS" --from-step build --to-step export
```

## Analysis Handoff

If the pipeline stops after `analyze`, read the generated `analysis_request.json`,
produce `analysis.json` from it, then update the config with `analysis_path` and rerun:

```bash
python scripts/run_pipeline.py --config "$ARGUMENTS" --from-step detect
```
