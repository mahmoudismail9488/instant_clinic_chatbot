# Day 4 — Safety, Guardrails & Internal Evaluation

Sources: [`source/Day4.pptx`](source/Day4.pptx), [`source/Day4_Safety_Evaluation.ipynb`](source/Day4_Safety_Evaluation.ipynb)

## Lab checklist

| # | Deliverable | Status | Where |
|---|---|---|---|
| 1 | Evaluation dataset (20–30 Qs) | done | `eval/day4_benchmark.csv` (24) |
| 2 | Input-risk classification | done | `backend/app/pipeline/risk_classification.py` |
| 3 | Retrieval threshold calibrated | done | `clinic calibrate` + `DEFAULT_EVIDENCE_THRESHOLD` |
| 4 | Unsupported-claim detection | done | `backend/app/pipeline/claim_support.py` (wired in `grounded_run`) |
| 5 | Metrics (≥1 retrieval + ≥1 citation/faithfulness + ≥1 safety) | done | `clinic day4-eval` |
| 6 | Normal / ambiguous / unsafe / OOS tests | done | benchmark + API smoke |
| 7 | Failure + improvement log | done | [`FAILURES.md`](FAILURES.md) |
| 8 | UX: status, confidence, evidence, next action | done | Answer/Refusal cards |
| 9 | Successful-answer demo | ready | Screening question |
| 10 | Safe-refusal demo | ready | Diagnosis / medication / adversarial |

## Commands

```bash
uv run clinic day4-eval
uv run --extra dev pytest backend/tests/test_day4_safety.py backend/tests/test_guardrails.py -q
```

## Documents in this folder

| File | Purpose |
|---|---|
| [`SAFETY_FLOW.md`](SAFETY_FLOW.md) | End-to-end safety flowchart |
| [`READINESS_SCORECARD.md`](READINESS_SCORECARD.md) | Day 5 gate checklist |
| [`EVALUATION_RESULTS.md`](EVALUATION_RESULTS.md) | Generated metrics (after `day4-eval`) |
| [`FAILURES.md`](FAILURES.md) | Failure analysis table |
| [`source/`](source/) | Original Day 4 deck + notebook |
