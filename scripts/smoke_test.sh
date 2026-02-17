#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="${1:-$ROOT_DIR/.temp/smoke}"
DECK_DIR="$WORK_DIR/smoke_deck"

if [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python3" ]]; then
  PYTHON_BIN="$VIRTUAL_ENV/bin/python3"
elif [[ -x "$ROOT_DIR/.venv/bin/python3" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
elif [[ -x "$ROOT_DIR/../../../.venv/bin/python3" ]]; then
  PYTHON_BIN="$ROOT_DIR/../../../.venv/bin/python3"
else
  PYTHON_BIN="python3"
fi

CONTENT_JSON="$WORK_DIR/content.json"
ANALYSIS_REQUEST_JSON="$WORK_DIR/analysis_request.json"
ANALYSIS_JSON="$WORK_DIR/analysis.json"
CHART_TYPES_JSON="$WORK_DIR/chart-types.json"

echo "[smoke] root: $ROOT_DIR"
echo "[smoke] work: $WORK_DIR"
echo "[smoke] python: $PYTHON_BIN"

"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys

missing = [
    name for name in ["docling", "pandas", "PIL", "jinja2"]
    if importlib.util.find_spec(name) is None
]
if missing:
    print(
        "[smoke] missing python modules: " + ", ".join(missing) +
        ". Install with: pip install docling pandas Pillow Jinja2",
        file=sys.stderr,
    )
    sys.exit(1)
PY

rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

cp "$ROOT_DIR/examples/fixtures/smoke-analysis.json" "$ANALYSIS_JSON"

"$PYTHON_BIN" "$ROOT_DIR/scripts/ingest_documents.py" \
  --files \
  "$ROOT_DIR/examples/demo-presentation/source_docs/q4_strategy_brief.md" \
  "$ROOT_DIR/examples/demo-presentation/source_docs/market_data.csv" \
  --output "$CONTENT_JSON"

"$PYTHON_BIN" "$ROOT_DIR/scripts/analyze_content.py" \
  --content "$CONTENT_JSON" \
  --audience mixed \
  --output "$ANALYSIS_REQUEST_JSON"

"$PYTHON_BIN" "$ROOT_DIR/scripts/detect_chart_type.py" \
  --analysis "$ANALYSIS_JSON" \
  --content "$CONTENT_JSON" \
  --output "$CHART_TYPES_JSON"

"$PYTHON_BIN" "$ROOT_DIR/scripts/create_slidev_project.py" \
  --theme consulting \
  --output "$DECK_DIR"

"$PYTHON_BIN" "$ROOT_DIR/scripts/generate_charts.py" \
  --analysis "$ANALYSIS_JSON" \
  --types "$CHART_TYPES_JSON" \
  --content "$CONTENT_JSON" \
  --output "$DECK_DIR/public/data" \
  --theme consulting

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_slides.py" \
  --analysis "$ANALYSIS_JSON" \
  --template "$ROOT_DIR/templates/slides.md.jinja2" \
  --output "$DECK_DIR/slides.md" \
  --deck-dir "$DECK_DIR" \
  --lint

"$PYTHON_BIN" "$ROOT_DIR/scripts/export_deck.py" \
  --deck-dir "$DECK_DIR" \
  --analysis "$ANALYSIS_JSON" \
  --formats spa \
  --base /

echo "[smoke] success"
echo "[smoke] deck output: $DECK_DIR"
