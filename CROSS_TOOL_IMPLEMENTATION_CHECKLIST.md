# Cross-Tool Compatibility Implementation Checklist

Goal: make `deck-generator` runnable from OpenCode, Claude Code, Codex CLI, Cursor, and similar tools through one shared pipeline.

## Item 1 - Create canonical implementation checklist

- [x] Add this checklist file with clear, commit-sized delivery items.
- [x] Keep this file updated as each item is completed.
- [x] End state for this item: committed to git.

## Item 2 - Introduce host-neutral pipeline contract

- [x] Add JSON schema for pipeline inputs (`schemas/pipeline-config.schema.json`).
- [x] Define required fields, defaults, optional paths, and execution controls.
- [x] Include strict validation guidance and machine-readable constraints.
- [x] End state for this item: committed to git.

## Item 3 - Implement single orchestration entrypoint

- [x] Add `scripts/run_pipeline.py` to orchestrate existing scripts.
- [x] Support non-interactive config-driven runs.
- [x] Support step range execution (`--from-step`, `--to-step`) and dry-run visibility.
- [x] Add clear actionable errors for missing prerequisites (for example missing `analysis.json`).
- [x] End state for this item: committed to git.

## Item 4 - Add cross-tool adapter templates

- [x] Add adapter docs/templates for OpenCode, Claude Code, Cursor, and Codex.
- [x] Ensure each adapter maps user input to the same config schema and runner command.
- [x] Include practical command file locations where applicable (for example `.cursor/commands`).
- [x] End state for this item: committed to git.

## Item 5 - Refactor skill docs to use shared runner

- [x] Update `SKILL.md` to use host-neutral execution core.
- [x] Remove hard coupling to OpenCode-only interaction semantics in workflow steps.
- [x] Keep OpenCode as an adapter, not the source of orchestration truth.
- [ ] End state for this item: committed to git.

## Item 6 - Add compatibility validation and CI-friendly smoke flow

- [ ] Add a compatibility smoke script that validates schema + pipeline dry run.
- [ ] Add sample config(s) under `examples/configs/` for quick verification.
- [ ] Document expected outputs and verification commands.
- [ ] End state for this item: committed to git.

## Item 7 - Update top-level documentation

- [ ] Update `README.md` with a canonical cross-tool workflow.
- [ ] Add per-tool quickstart references to adapter templates.
- [ ] Document Codex approval/sandbox and Cursor command-location considerations.
- [ ] End state for this item: committed to git.
