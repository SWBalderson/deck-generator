# Example Pipeline Configs

## `cross-tool-minimal.json`

Minimal config for adapter integration and compatibility checks.

- Runs `ingest -> analyze` only
- Uses dry-run execution by default
- Does not require `analysis_path`

## Verification Commands

```bash
./scripts/smoke_compat.sh
./scripts/smoke_compat.sh examples/configs/cross-tool-minimal.json
python scripts/run_pipeline.py --config examples/configs/cross-tool-minimal.json --dry-run
```

## Expected Smoke Outputs

- `[compat] basic schema checks passed`
- pipeline command list for ingest and analyze steps
- `Pipeline completed.`
- `[compat] dry-run pipeline check passed`
