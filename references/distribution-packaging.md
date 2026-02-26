# Distribution And Packaging

This repository keeps `README.md` at the root for human readers.

When packaging a distributable skill folder, include only runtime skill assets.

## Include

- `SKILL.md`
- `scripts/`
- `schemas/`
- `templates/`
- `assets/`
- `references/`
- required adapter files for target tool

## Exclude

- repository-only docs that are not needed at runtime
- local caches (`__pycache__`, `.pytest_cache`)
- `.git/`
- CI-only artifacts

## Recommended Packaging Check

1. Confirm `SKILL.md` is present and valid frontmatter parses.
2. Confirm all referenced relative paths in `SKILL.md` exist.
3. Run:

```bash
python scripts/run_pipeline.py --config path/to/deck.config.json --dry-run
```

4. Run a real fixture check before release:

```bash
python scripts/run_fixture_checks.py
```
