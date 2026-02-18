# Deck Generator — Agent Guide

This project generates consulting-style presentation decks from document sources.

## For AI Coding Agents (Codex, OpenCode, etc.)

### Pipeline Entrypoint

All operations go through the same command:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json
```

### Config Contract

Config must match `schemas/pipeline-config.schema.json`.

Required fields: `project_name`, `title`, `source_files`, `output_root`.

A minimal example is at `examples/configs/cross-tool-minimal.json`.

### Creating a Config

When a user asks to generate a deck, collect:

1. **project_name** — slug like `q4-results` (alphanumeric, hyphens, underscores)
2. **title** — human-readable presentation title
3. **source_files** — array of document paths (PDF, DOCX, CSV, MD, etc.)
4. **output_root** — directory where `{project_name}_deck` will be created

Optional: `theme`, `audience` (board/staff/parents/mixed), `colors`, `logo_path`, `subtitle`, `author`.

Write the config as JSON, then run the pipeline.

### Step-by-Step Execution

The pipeline has these steps in order: `ingest`, `analyze`, `detect`, `charts`, `project`, `build`, `export`, `commit`, `cleanup`.

- After `analyze`, the pipeline produces `analysis_request.json`. You must generate `analysis.json` from it and set `analysis_path` in config before continuing.
- Partial reruns: `--from-step <step> --to-step <step>`
- Dry run: `--dry-run`

### Sandbox Considerations

This skill needs:
- **Filesystem write access** to the output directory (for deck creation)
- **Network access** for `npm install` / `bun add` during project scaffolding
- **Shell access** to run Python and Node.js commands

Recommended Codex config (`.codex/config.toml`):

```toml
[permissions]
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

### Testing

```bash
python scripts/run_fixture_checks.py        # Fast fixture regressions
./scripts/smoke_test.sh                      # Full end-to-end smoke test
```

### Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_pipeline.py` | Orchestrator — run this |
| `scripts/ingest_documents.py` | Multi-format document ingestion |
| `scripts/analyze_content.py` | Prepare analysis request for LLM |
| `scripts/detect_chart_type.py` | Auto-detect chart types from data |
| `scripts/generate_charts.py` | Generate Chart.js configurations |
| `scripts/build_slides.py` | Render slides.md from template + analysis |
| `scripts/export_deck.py` | Export to PDF, PPTX, or SPA |
| `scripts/validate_analysis.py` | Validate analysis.json structure |
| `scripts/lint_slides.py` | Slide quality linting |
| `scripts/lint_consulting_quality.py` | Consulting quality scoring |
