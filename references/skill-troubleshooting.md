# Skill Troubleshooting

## Pipeline Stops After `analyze`

Symptom: `analysis_request.json` exists and workflow cannot continue.

Cause: `analysis_path` is missing or points to a missing file.

Action:

1. Generate `analysis.json` from `analysis_request.json`.
2. Set `analysis_path` in config.
3. Resume:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step detect
```

## Export Fails With Browser Dependency Errors

Symptom: PDF or PPTX export fails at `export` step.

Cause: `playwright-chromium` missing in generated deck project.

Action:

```bash
npm install -D playwright-chromium --prefix path/to/<project>_deck
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step export
```

## Analysis Validation Or Chart Mapping Errors

Symptom: Build fails with missing fields for charts/images/slides.

Cause: `analysis.json` does not satisfy schema constraints.

Action:

```bash
python scripts/validate_analysis.py --analysis path/to/analysis.json
```

Fix required fields called out by validator, then rerun from `detect` or `build` as needed.

## Git Mode Confusion

Symptom: Unexpected commits or missing commits.

Cause: `execution.git_mode` does not match intent.

Action:

- `manual`: no automatic commit, user controls git actions.
- `auto`: pipeline can initialize and commit changes.
- `off`: no git operations.

Set desired mode in config, then rerun from `commit` or full pipeline.
