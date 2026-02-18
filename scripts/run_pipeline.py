#!/usr/bin/env python3
"""
Run the deck-generator pipeline from one host-neutral config file.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


STEP_ORDER = [
    "ingest",
    "analyze",
    "detect",
    "charts",
    "project",
    "build",
    "export",
    "commit",
    "cleanup",
]


def resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_config(config_path: Path) -> Dict:
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def defaulted_config(config: Dict) -> Dict:
    execution = {
        "from_step": "ingest",
        "to_step": "export",
        "dry_run": False,
        "stop_on_error": True,
        "git_mode": "manual",
        "clean_temp": False,
        "lint": True,
        "lint_strict": False,
        "consulting_lint": False,
        "consulting_lint_strict": False,
        "consulting_lint_threshold": 70,
    }
    execution.update(config.get("execution", {}))

    merged = {
        "theme": "consulting",
        "audience": "mixed",
        "subtitle": "",
        "author": "",
        "export_formats": ["spa"],
        "export_base": "/",
        "colors": {},
        **config,
    }
    merged["execution"] = execution
    return merged


def validate_config(config: Dict) -> None:
    required = ["project_name", "title", "source_files", "output_root"]
    missing = [field for field in required if not config.get(field)]
    if missing:
        raise ValueError(f"Missing required config fields: {', '.join(missing)}")

    if not isinstance(config.get("source_files"), list) or not config["source_files"]:
        raise ValueError("'source_files' must be a non-empty array")

    if any(step not in STEP_ORDER for step in [config["execution"]["from_step"], config["execution"]["to_step"]]):
        raise ValueError("'execution.from_step' and 'execution.to_step' must be valid step names")

    if STEP_ORDER.index(config["execution"]["from_step"]) > STEP_ORDER.index(config["execution"]["to_step"]):
        raise ValueError("'execution.from_step' must not come after 'execution.to_step'")

    git_mode = config["execution"].get("git_mode")
    if git_mode not in {"manual", "auto", "off"}:
        raise ValueError("'execution.git_mode' must be one of: manual, auto, off")

    base = config.get("export_base", "/")
    if not (base.startswith("/") and base.endswith("/")):
        raise ValueError("'export_base' must start and end with '/'")


def should_run(step: str, from_step: str, to_step: str) -> bool:
    index = STEP_ORDER.index(step)
    return STEP_ORDER.index(from_step) <= index <= STEP_ORDER.index(to_step)


def run_cmd(command: List[str], cwd: Path, dry_run: bool) -> None:
    print("$", " ".join(command))
    if dry_run:
        return
    subprocess.run(command, cwd=cwd, check=True)


def require_analysis(config: Dict, base_dir: Path) -> Path:
    raw = config.get("analysis_path")
    if not raw:
        raise ValueError(
            "analysis_path is required for detect/charts/build/export steps. "
            "Generate analysis.json from analysis_request.json with your preferred LLM and set analysis_path in config."
        )
    path = resolve_path(raw, base_dir)
    if not path.exists():
        raise ValueError(f"analysis_path does not exist: {path}")
    return path


def run_git_commit(deck_dir: Path, dry_run: bool) -> None:
    status_cmd = ["git", "status", "--porcelain"]
    if dry_run:
        print("$", " ".join(status_cmd))
        print("$ git add .")
        print("$ git commit -m [deck-generator] Pipeline update")
        return

    status = subprocess.run(status_cmd, cwd=deck_dir, capture_output=True, text=True, check=True)
    if not status.stdout.strip():
        print("No git changes detected; skipping commit step.")
        return

    subprocess.run(["git", "add", "."], cwd=deck_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "[deck-generator] Pipeline update"],
        cwd=deck_dir,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deck-generator pipeline from config")
    parser.add_argument("--config", required=True, help="Path to pipeline config JSON")
    parser.add_argument("--from-step", choices=STEP_ORDER, help="Optional runtime override for first step")
    parser.add_argument("--to-step", choices=STEP_ORDER, help="Optional runtime override for last step")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 1

    skill_root = Path(__file__).parent.parent
    scripts_dir = skill_root / "scripts"
    templates_dir = skill_root / "templates"

    config = defaulted_config(load_config(config_path))
    if args.from_step:
        config["execution"]["from_step"] = args.from_step
    if args.to_step:
        config["execution"]["to_step"] = args.to_step
    if args.dry_run:
        config["execution"]["dry_run"] = True

    try:
        validate_config(config)
    except ValueError as exc:
        print(f"Config validation failed: {exc}", file=sys.stderr)
        return 1

    output_root = resolve_path(config["output_root"], config_dir)
    deck_dir = output_root / f"{config['project_name']}_deck"
    temp_dir = output_root / f".{config['project_name']}_temp"
    content_json = temp_dir / "content.json"
    analysis_request_json = temp_dir / "analysis_request.json"
    chart_types_json = temp_dir / "chart-types.json"

    dry_run = bool(config["execution"]["dry_run"])
    output_root.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    from_step = config["execution"]["from_step"]
    to_step = config["execution"]["to_step"]

    print(f"Pipeline config: {config_path}")
    print(f"Deck directory: {deck_dir}")
    print(f"Step range: {from_step} -> {to_step}")

    try:
        if should_run("ingest", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "ingest_documents.py"),
                "--files",
                *[str(resolve_path(item, config_dir)) for item in config["source_files"]],
                "--output",
                str(content_json),
            ]
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("analyze", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "analyze_content.py"),
                "--content",
                str(content_json),
                "--audience",
                config["audience"],
                "--output",
                str(analysis_request_json),
            ]
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        needs_analysis = any(
            should_run(step, from_step, to_step)
            for step in ["detect", "charts", "build", "export"]
        )
        analysis_path = require_analysis(config, config_dir) if needs_analysis else None

        if should_run("detect", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "detect_chart_type.py"),
                "--analysis",
                str(analysis_path),
                "--content",
                str(content_json),
                "--output",
                str(chart_types_json),
            ]
            if config.get("chart_overrides_path"):
                command.extend([
                    "--overrides",
                    str(resolve_path(config["chart_overrides_path"], config_dir)),
                ])
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("charts", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "generate_charts.py"),
                "--analysis",
                str(analysis_path),
                "--types",
                str(chart_types_json),
                "--content",
                str(content_json),
                "--output",
                str(deck_dir / "public" / "data"),
                "--theme",
                config["theme"],
            ]
            if config.get("chart_overrides_path"):
                command.extend([
                    "--overrides",
                    str(resolve_path(config["chart_overrides_path"], config_dir)),
                ])
            if config.get("colors"):
                command.extend(["--colors", json.dumps(config["colors"])])
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("project", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "create_slidev_project.py"),
                "--theme",
                config["theme"],
                "--output",
                str(deck_dir),
            ]
            if config.get("logo_path"):
                command.extend(["--logo", str(resolve_path(config["logo_path"], config_dir))])
            if config.get("colors"):
                command.extend(["--colors", json.dumps(config["colors"])])
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("build", from_step, to_step):
            command = [
                sys.executable,
                str(scripts_dir / "build_slides.py"),
                "--analysis",
                str(analysis_path),
                "--template",
                str(templates_dir / "slides.md.jinja2"),
                "--output",
                str(deck_dir / "slides.md"),
                "--deck-dir",
                str(deck_dir),
            ]
            if config["execution"].get("lint"):
                command.append("--lint")
            if config["execution"].get("lint_strict"):
                command.append("--lint-strict")
            if config["execution"].get("consulting_lint"):
                command.extend(["--consulting-lint", "--content", str(content_json)])
            if config["execution"].get("consulting_lint_strict"):
                command.extend([
                    "--consulting-lint-strict",
                    "--consulting-lint-threshold",
                    str(config["execution"]["consulting_lint_threshold"]),
                ])
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("export", from_step, to_step):
            formats = config.get("export_formats", ["spa"])
            command = [
                sys.executable,
                str(scripts_dir / "export_deck.py"),
                "--deck-dir",
                str(deck_dir),
                "--analysis",
                str(analysis_path),
                "--base",
                config.get("export_base", "/"),
                "--formats",
                *formats,
            ]
            run_cmd(command, cwd=skill_root, dry_run=dry_run)

        if should_run("commit", from_step, to_step):
            mode = config["execution"].get("git_mode", "manual")
            if mode == "auto":
                run_git_commit(deck_dir, dry_run=dry_run)
            elif mode == "manual":
                print("Git mode is manual; skipping auto-commit step.")
            else:
                print("Git mode is off; skipping commit step.")

        if should_run("cleanup", from_step, to_step):
            if config["execution"].get("clean_temp"):
                if dry_run:
                    print(f"$ rm -rf {temp_dir}")
                else:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(f"Removed temp directory: {temp_dir}")
            else:
                print("clean_temp=false; keeping temp directory.")

    except subprocess.CalledProcessError as exc:
        print(f"Pipeline step failed with exit code {exc.returncode}: {' '.join(exc.cmd)}", file=sys.stderr)
        return exc.returncode
    except ValueError as exc:
        print(f"Pipeline validation error: {exc}", file=sys.stderr)
        return 1

    print("Pipeline completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
