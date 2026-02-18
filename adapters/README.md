# Deck Generator Adapters

These adapter templates map tool-specific workflows to the same host-neutral pipeline command:

```bash
python scripts/run_pipeline.py --config <path-to-config.json>
```

All adapters should collect user intent and write a config that conforms to:

- `schemas/pipeline-config.schema.json`

Then call the same runner command. Keep business logic in `scripts/`, not in adapter prompts.

## Included Adapters

- `adapters/opencode/` - OpenCode skill adapter guidance
- `adapters/claude/` - Claude Code slash command templates
- `adapters/cursor/` - Cursor command templates
- `adapters/codex/` - Codex CLI setup and command templates
