# OpenCode Adapter

OpenCode should act as a thin adapter over the shared pipeline.

## Adapter Contract

1. Collect parameters from the user.
2. Write a config JSON that matches `schemas/pipeline-config.schema.json`.
3. Execute:

```bash
python scripts/run_pipeline.py --config <config.json>
```

4. If the user requests partial reruns, use:

```bash
python scripts/run_pipeline.py --config <config.json> --from-step <step> --to-step <step>
```

## Notes

- Keep prompt content focused on user interaction and input gathering.
- Do not duplicate script orchestration logic in the skill adapter.
- Keep git behavior explicit via `execution.git_mode` in config.
