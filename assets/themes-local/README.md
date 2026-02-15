# Local Themes

Place local-only themes in this directory.

Quick start:

```bash
python scripts/create_local_theme.py \
  --theme-name my-brand \
  --primary '#003366' \
  --secondary '#6699CC' \
  --accent '#FF6B35'
```

Each theme should follow:

```
assets/themes-local/<theme-name>/theme.css
assets/themes-local/<theme-name>/uno.config.ts
```

Notes:
- This directory is intentionally git-ignored for child theme folders, so private themes are not pushed.
- The skill will resolve themes in this order:
  1) `assets/themes/<theme-name>` (shared)
  2) `assets/themes-local/<theme-name>` (local/private)
- If a requested theme is not found, it falls back to `consulting`.
- To overwrite an existing local theme scaffold, run with `--force`.
