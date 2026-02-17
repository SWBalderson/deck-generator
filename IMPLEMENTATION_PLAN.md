# Deck Generator Implementation Plan

Last updated: 2026-02-17
Owner: @SWBalderson
Status: Active

## How to use this plan

- Use this as the single source of truth for roadmap execution.
- Work top-to-bottom by phase unless a blocker forces reordering.
- Keep one in-progress item per phase.
- After each work session, update the status checkboxes and append an entry to the progress log.

## Roadmap summary

1. Stabilise rendering and workflow consistency.
2. Make charts truly data-driven from ingested sources.
3. Add validation and quality guardrails.
4. Add advanced authoring features (audience modes, notes, citations, slide locks).

---

## Phase 1 - Stabilisation (High priority)

### Objectives

- Eliminate blank/malformed chart slides.
- Align docs with actual script behaviour.
- Ensure custom colours and logo discovery work consistently.

### Tasks

- [x] **P1.1 Chart contract fix**
  - Update `assets/components/DeckChart.vue` to support full chart config JSON (`type`, `data`, `options`) and backward-compatible data-only JSON.
  - Add defensive error handling and console diagnostics.
- [x] **P1.2 Docs/workflow consistency**
  - Update `SKILL.md` and `README.md` to remove contradictory git-init sequencing.
  - Keep one canonical workflow order.
- [x] **P1.3 Colour propagation**
  - Wire `--colors` through project creation and chart generation.
  - Ensure theme CSS and chart palettes use selected colours.
- [x] **P1.4 Logo fallback paths**
  - Extend `assets/components/DeckLogo.vue` to include `/images/logo*` and `/images/logo-title*` candidates.

### Acceptance criteria

- [x] Charts render from current generated JSON without blank chart slides.
- [x] Custom colour inputs visibly affect deck theme and chart output.
- [x] Logo loads from both `public/logo.*` and `public/images/logo.*`.
- [x] Workflow docs match what scripts actually do.

### Estimate

- Size: S-M
- Target: 2-4 days

---

## Phase 2 - Data-Driven Chart Pipeline (Core capability)

### Objectives

- Generate chart values from real input data instead of demo values.
- Improve chart-type detection using dataset structure.

### Tasks

- [x] **P2.1 Analysis data contract**
  - Define and document chart mapping fields in `analysis.json` (for example `data_file`, `x_key`, `y_key`, `series_key`).
- [x] **P2.2 Data-based type detection**
  - Refactor `scripts/detect_chart_type.py` to load and inspect real datasets where available.
  - Keep context heuristics as fallback.
- [x] **P2.3 Real chart generation**
  - Refactor `scripts/generate_charts.py` to map source columns to chart datasets.
  - Remove hard-coded demo values.
- [ ] **P2.4 Manual overrides**
  - Add optional `chart-overrides.json` support to force chart type/field mappings.

### Acceptance criteria

- [ ] CSV/XLSX/JSON-driven slides render charts from actual source values.
- [ ] Type detection behaves predictably on fixture datasets.
- [ ] Overrides can force chart type and mapping without code changes.

### Estimate

- Size: M-L
- Target: 5-8 days

---

## Phase 3 - Validation and QA guardrails

### Objectives

- Fail fast on invalid deck structures.
- Improve output quality and diagnostics.

### Tasks

- [ ] **P3.1 Analysis schema**
  - Introduce JSON schema for `analysis.json`.
- [ ] **P3.2 Validation script**
  - Add `scripts/validate_analysis.py` and integrate into build/export path.
- [ ] **P3.3 Slide quality lints**
  - Add optional `scripts/lint_slides.py` checks (missing sources, empty bullets, weak action titles).
- [ ] **P3.4 Error handling cleanup**
  - Replace broad `except:` blocks with typed exceptions and user-actionable errors.

### Acceptance criteria

- [ ] Invalid analysis fails with clear remediation guidance.
- [ ] Lint catches key quality issues before export.
- [ ] Common failure paths produce actionable diagnostics.

### Estimate

- Size: M
- Target: 3-5 days

---

## Phase 4 - Advanced features (Differentiators)

### Objectives

- Extend functionality for stronger real-world authoring workflows.

### Tasks

- [ ] **P4.1 Audience modes**
  - Support modes like `board`, `staff`, `parents` to tune tone/detail.
- [ ] **P4.2 Speaker notes**
  - Generate concise presenter notes per slide.
- [ ] **P4.3 Citation traceability**
  - Link slide bullets to source excerpts/pages where possible.
- [ ] **P4.4 Iterative controls**
  - Add slide-level locks and selective regeneration support.

### Acceptance criteria

- [ ] Audience mode can be selected at generation time.
- [ ] Notes/citations are generated when requested.
- [ ] Locked slides remain unchanged during iterative edits.

### Estimate

- Size: M-L
- Target: 5-10 days

---

## Testing and CI workstream (parallel)

- [x] Add fixture datasets for chart detection and generation.
- [ ] Add smoke test script: ingest -> analyse -> detect -> chart -> build -> export.
- [ ] Run smoke + fixture tests in CI for each PR.

---

## Recommended PR sequence

1. Chart contract fix + regression fixtures.
2. Docs workflow cleanup + logo fallback + colour wiring.
3. Real data mapping in chart generation.
4. Data-based chart detection + override support.
5. Analysis validation + lint tooling.
6. Advanced features split into focused PRs.

---

## Progress log

Use this format:

`YYYY-MM-DD - PR/commit - Completed tasks - Notes/blockers`

- 2026-02-17 - Plan created - Initial roadmap baseline established.
- 2026-02-17 - (pending commit) - Completed P1.1 chart contract fix and added chart fixtures - Renderer now supports both data-only and full Chart.js config JSON.
- 2026-02-17 - (pending commit) - Completed P1.2 docs/workflow consistency - SKILL and README now match project creation + git initialisation behaviour.
- 2026-02-17 - (pending commit) - Completed P1.3 colour propagation - `--colors` now applies to copied theme files and chart generation palettes.
- 2026-02-17 - (pending commit) - Completed P1.4 logo fallback paths - Deck logo now resolves from `public/logo.*` and `public/images/logo.*`.
- 2026-02-17 - (pending commit) - Completed P2.1 analysis data contract - Added `source_file`/`x_key`/`y_key`/`series_key` guidance for charted slides.
- 2026-02-17 - (pending commit) - Completed P2.2 data-based type detection - Detector now reads ingested content when `source_file` is provided and falls back to context heuristics.
- 2026-02-17 - (pending commit) - Completed P2.3 real chart generation - Chart configs now use mapped source rows (`source_file`, `x_key`, `y_key`, optional `series_key`) with sample fallback only when mapping is unavailable.

---

## Current next actions

- [ ] Start **P1.3 Colour propagation** in project and chart generation scripts.
- [ ] Start **P2.2 Data-based type detection** in `scripts/detect_chart_type.py`.
- [ ] Start **P2.3 Real chart generation** in `scripts/generate_charts.py`.
- [x] Expand fixtures to cover source-to-chart mapping cases.
- [ ] Start **P2.4 Manual overrides** support for chart type/field mappings.
