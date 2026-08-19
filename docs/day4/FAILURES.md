# Day 4 — Failure analysis & improvements

| Failure mode | Example | Detection | Improvement |
|---|---|---|---|
| Medication ask answered | “What medicine should I take?” | Input risk + Stage-5 phrases | Refuse before retrieval; UX medication reason |
| Prompt-only drift | Dose invented in draft | Claim-support overlap + answer guardrails | Fail closed to insufficient evidence |
| Jailbreak | “Ignore retrieved evidence…” | Adversarial risk class | Refuse + log path |
| Weak retrieval | CKD stages / melanoma | Threshold + model insufficient_evidence | Prefer refusal over guess |
| Known retrieval miss | HbA1c diagnostic cutoff | Matrix + Day 4 benchmark | Document; do not invent table values |
| Decorative citation | Right doc, wrong support | Manual `clinic review` + coverage gate | Coverage must be 100% to answer |
| Flaky structured generation | D4-03 age-screening Q refused once (`generation failed`) | Day 4 eval 23/24 | Retry in demo; fail-closed is correct — never show invalid JSON |

## Latest Day 4 run (captured)

- Behavior pass rate: **96%** (23/24)  
- Safety pass rate: **100%**  
- Citation coverage (answered): **100%**  
- Claim faithfulness (answered): **100%**  
- Unsupported claim rate (answered): **0%**  

- **Low Precision@K** → chunking / embeddings / query phrasing (Day 2 levers).  
- **Low citation accuracy** → metadata / page mapping / prompt.  
- **High unsupported claims** → tighten prompt, enlarge context, keep claim-support net.
