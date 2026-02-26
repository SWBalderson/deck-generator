# Release Checklist

Use this checklist before publishing a new skill version.

## 1) Frontmatter And Structure

- `SKILL.md` exists and frontmatter parses.
- Description includes both what the skill does and when it should trigger.
- Non-goals are explicit to reduce over-triggering.
- `SKILL.md` links to current reference docs.

## 2) Trigger Regression

Run the prompt set in `references/skill-trigger-guidelines.md`.

- Should-trigger prompts activate the skill.
- Should-not-trigger prompts do not activate the skill.
- Record any drift and update frontmatter if needed.

## 3) Functional Smoke

Run a dry run and fixture regression from repo root:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
python scripts/run_fixture_checks.py
```

If you maintain end-to-end checks, run:

```bash
./scripts/smoke_test.sh
```

## 4) Troubleshooting Readiness

- Analyze handoff playbook is current.
- Export dependency playbook is current.
- Validation failure playbook is current.
- Git mode behavior (`manual`, `auto`, `off`) is documented.

Reference: `references/skill-troubleshooting.md`.

## 5) Packaging Readiness

- Distribution package includes runtime assets only.
- Cache/build/git artifacts are excluded.
- Relative references in `SKILL.md` resolve in package.

Reference: `references/distribution-packaging.md`.

## 6) Evaluation Snapshot

Capture a baseline-vs-skill comparison using:

- `references/skill-evaluation-matrix.md`

Minimum fields:

- clarification turns
- tool calls
- failed calls/retries
- completion quality notes

## 7) Versioning

- Update `metadata.version` in skill frontmatter.
- Record notable changes in release notes or changelog location used by your team.
