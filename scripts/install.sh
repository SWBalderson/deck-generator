#!/usr/bin/env bash
# install.sh — Set up deck-generator for any AI coding tool.
#
# Usage:
#   ./scripts/install.sh [--tool cursor|claude|codex|opencode|all] [--project-dir PATH]
#
# Installs Python dependencies and copies tool-specific adapter files
# into the correct locations for each tool.

set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="all"
PROJECT_DIR="$(pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)   TOOL="$2"; shift 2 ;;
    --project-dir) PROJECT_DIR="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--tool cursor|claude|codex|opencode|all] [--project-dir PATH]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "deck-generator install"
echo "  Skill root:  $SKILL_ROOT"
echo "  Project dir: $PROJECT_DIR"
echo "  Tool:        $TOOL"
echo

# -- Python dependencies --
echo "Installing Python dependencies..."
pip install -r "$SKILL_ROOT/requirements.txt" --quiet 2>/dev/null || {
  python3 -m pip install -r "$SKILL_ROOT/requirements.txt" --quiet
}
echo "  Done."
echo

# -- Node global: slidev CLI --
if command -v npm >/dev/null 2>&1; then
  if ! command -v slidev >/dev/null 2>&1; then
    echo "Installing Slidev CLI globally..."
    npm install -g @slidev/cli --silent 2>/dev/null || true
    echo "  Done."
  else
    echo "Slidev CLI already installed."
  fi
else
  echo "WARNING: npm not found — install Node.js to use Slidev export features."
fi
echo

install_cursor() {
  echo "Setting up Cursor adapter..."
  mkdir -p "$PROJECT_DIR/.cursor/commands"
  mkdir -p "$PROJECT_DIR/.cursor/skills/deck-generator"
  cp "$SKILL_ROOT/adapters/cursor/commands/deck-generate.md" "$PROJECT_DIR/.cursor/commands/"
  cp "$SKILL_ROOT/adapters/cursor/skill/SKILL.md" "$PROJECT_DIR/.cursor/skills/deck-generator/"
  echo "  Installed: .cursor/commands/deck-generate.md"
  echo "  Installed: .cursor/skills/deck-generator/SKILL.md"
}

install_claude() {
  echo "Setting up Claude Code adapter..."
  mkdir -p "$PROJECT_DIR/.claude/commands"
  cp "$SKILL_ROOT/adapters/claude/commands/deck-generate.md" "$PROJECT_DIR/.claude/commands/"
  cp "$SKILL_ROOT/CLAUDE.md" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null || true
  echo "  Installed: .claude/commands/deck-generate.md"
  echo "  Copied:    CLAUDE.md (if exists)"
}

install_codex() {
  echo "Setting up Codex adapter..."
  cp "$SKILL_ROOT/AGENTS.md" "$PROJECT_DIR/AGENTS.md" 2>/dev/null || true
  echo "  Copied: AGENTS.md"
}

install_opencode() {
  echo "Setting up OpenCode adapter..."
  echo "  OpenCode discovers the skill via SKILL.md in the .opencode/skills directory."
  echo "  No additional setup required."
}

case "$TOOL" in
  cursor)    install_cursor ;;
  claude)    install_claude ;;
  codex)     install_codex ;;
  opencode)  install_opencode ;;
  all)
    install_cursor
    echo
    install_claude
    echo
    install_codex
    echo
    install_opencode
    ;;
  *)
    echo "Unknown tool: $TOOL"
    echo "Valid tools: cursor, claude, codex, opencode, all"
    exit 1
    ;;
esac

echo
echo "Install complete. Run the pipeline with:"
echo "  python $SKILL_ROOT/scripts/run_pipeline.py --config path/to/deck.config.json"
