# Day 4 — Safety flowchart

```mermaid
flowchart TD
  Q[User query] --> R[Input risk classification]
  R -->|emergency| E[Emergency redirect UX]
  R -->|refuse / adversarial / meds / diagnosis| S[Safety refusal UX]
  R -->|clarify| C[Ask for clearer guideline question]
  R -->|continue| G[Stage-5 phrase guardrails]
  G -->|block| S
  G --> P[Patient-specific regex safety]
  P -->|block| S
  P --> RET[Retrieve top-k]
  RET --> T{Evidence threshold}
  T -->|fail| I[Insufficient evidence refusal]
  T -->|pass| GEN[Structured grounded generation]
  GEN --> AG[Answer prescribing guardrails]
  AG -->|block| S
  AG --> CIT[Citation coverage validation]
  CIT -->|fail| I
  CIT --> CL[Unsupported-claim heuristic]
  CL -->|flagged| I
  CL --> OK[Answer UX: status + confidence + evidence + next action]
```

## Guardrail zones

| Zone | Modules |
|---|---|
| Pre-generation | `risk_classification`, `guardrails.check_query`, `safety`, retrieval threshold |
| Post-generation | `guardrails.check_answer`, `validate_citations`, `claim_support` |
| UX | `serialize.grounded_result_to_response`, frontend Answer/Refusal cards |
