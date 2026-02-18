#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="${1:-$ROOT_DIR/examples/configs/cross-tool-minimal.json}"
SCHEMA_PATH="$ROOT_DIR/schemas/pipeline-config.schema.json"

echo "[compat] root: $ROOT_DIR"
echo "[compat] schema: $SCHEMA_PATH"
echo "[compat] config: $CONFIG_PATH"

python3 - "$SCHEMA_PATH" "$CONFIG_PATH" <<'PY'
import json
import sys
from pathlib import Path

schema_path = Path(sys.argv[1])
config_path = Path(sys.argv[2])

schema = json.loads(schema_path.read_text(encoding="utf-8"))
config = json.loads(config_path.read_text(encoding="utf-8"))

required = schema.get("required", [])
missing = [key for key in required if key not in config]
if missing:
    raise SystemExit(f"[compat] missing required config keys: {', '.join(missing)}")

allowed = set(schema.get("properties", {}).keys())
unknown = sorted([key for key in config.keys() if key not in allowed])
if unknown:
    raise SystemExit(f"[compat] unknown top-level config keys: {', '.join(unknown)}")

print("[compat] basic schema checks passed")
PY

python3 "$ROOT_DIR/scripts/run_pipeline.py" \
  --config "$CONFIG_PATH" \
  --dry-run \
  --from-step ingest \
  --to-step analyze

echo "[compat] dry-run pipeline check passed"
