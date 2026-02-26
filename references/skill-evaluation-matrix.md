# Skill Evaluation Matrix

Use this for lightweight regression after prompt/frontmatter changes.

## Trigger Evaluation

| Prompt | Expected | Actual | Notes |
|---|---|---|---|
| Create a deck from these files | Trigger |  |  |
| Turn docs into slides with charts | Trigger |  |  |
| Export this deck to pptx | Trigger |  |  |
| Design one poster image | No trigger |  |  |
| Explain this Python error | No trigger |  |  |

Target: 90 percent or better correct trigger behavior across test prompts.

## Functional Evaluation

| Scenario | Check | Pass/Fail | Notes |
|---|---|---|---|
| Full run | Deck folder created |  |  |
| Analyze handoff | `analysis_request.json` generated |  |  |
| Detect onward | Build succeeds with `analysis_path` |  |  |
| Export | Requested formats produced |  |  |
| Iterative controls | Locked slides preserved |  |  |

## Baseline vs Skill Comparison

| Metric | Without skill | With skill |
|---|---:|---:|
| User clarification turns |  |  |
| Total tool calls |  |  |
| Failed calls/retries |  |  |
| Total tokens (if available) |  |  |
| Time to completed export |  |  |

Goal: fewer retries and fewer clarifications while preserving output quality.
