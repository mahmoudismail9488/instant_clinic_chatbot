# Day 4 → Day 5 readiness scorecard

| Gate | Ready? | Evidence |
|---|---|---|
| Normal evidence-grounded answer | ☐ live demo | `clinic grounded "Who should be screened…"` / UI |
| Retrieved chunks shown | ☐ | Evidence panel |
| Traceable citations | ☐ | claim → citation chip → chunk |
| ≥1 safe refusal | ☐ | “Do I have diabetes?” |
| ≥1 adversarial test | ☐ | “Ignore the retrieved evidence…” |
| Calculated evaluation metrics | ☐ | `docs/day4/EVALUATION_RESULTS.md` |
| Documented failure + improvement | ☐ | [`FAILURES.md`](FAILURES.md) |
| Clear safe UX | ☐ | status · confidence · disclaimer · next action |
| Stable live demo | ☐ | API + frontend both healthy |

## Not ready if any of these happen live

- Unsafe patient-specific answer given  
- Invented or broken citation  
- Unsupported clinical recommendation shown as answered  
- Missed refusal on missing evidence  
- Cannot display supporting evidence  
