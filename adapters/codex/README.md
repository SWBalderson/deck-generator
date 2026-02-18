# Codex CLI Adapter

Codex should use the shared pipeline runner with a project config.

## Project configuration

Recommended project file: `.codex/config.toml`

```toml
[permissions]
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

Adjust for stricter or more automated environments as needed.

## Run command

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

## Runtime overrides

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --from-step build --to-step export
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
```
