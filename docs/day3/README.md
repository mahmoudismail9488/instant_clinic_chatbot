# Day 3 — grounded answer layer

Strict, citation-backed answers on top of Day 2 retrieval.

## Quick commands

```bash
uv run clinic grounded "Who should be screened for type 2 diabetes?"
uv run clinic grounded "Do I have diabetes?"
uv run clinic test --out docs/day3/results.md
uv run clinic review --report
uv run --extra dev pytest backend/tests/test_grounded_answer.py
```

## Documents

| File | Purpose |
|---|---|
| [`CHECKLIST.md`](CHECKLIST.md) | Full lab checklist + failure log + API wiring |
| [`results.md`](results.md) | Supported / unsupported / unsafe matrix |
| [`citation_review.csv`](citation_review.csv) | Claim↔citation correctness reviews |

## Production path

The same `answer_question()` flow powers:

- `uv run clinic grounded …`
- `POST /query` (`uv run clinic-api`)
- Frontend workspace chat
