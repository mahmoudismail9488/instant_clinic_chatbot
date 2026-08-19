# Day 3 — lab checklist, deliverables, and end-of-day review

Everything below was run against the live index on 2026-08-18 (471 chunks, 349 distinct,
2 guideline PDFs). Commands assume `uv run` from the repo root.

```bash
uv run clinic grounded "Who should be screened for type 2 diabetes?"
uv run clinic grounded "Do I have diabetes?"          # safety refusal
uv run clinic calibrate                                # lab step 3
uv run clinic review                                   # lab step 11
uv run clinic test --out docs/day3/results.md          # lab step 12
uv run --extra dev pytest backend/tests/               # grounded answer unit tests (48+)
```

Also available through the **production API / UI** (same `answer_question` pipeline):

```bash
uv run clinic-api
# Frontend: cd frontend && npm run dev  → http://localhost:8080/
```

## The 14 lab steps (slide 29)

| # | step | status | where |
|---|---|---|---|
| 1 | Confirm Day 2 retrieval output is ready | done | corpus restored to `data/raw_guidelines/`, index rebuilt, `clinic query` verified working |
| 2 | Select Top-K / chunk-size / overlap | done | Top-K **5** (`default_top_k`); chunk 1024/100 kept from Day 2 — see caveat below |
| 3 | Select an initial retrieval threshold | done | `clinic calibrate` → **0.015**, rationale in `grounded_run.DEFAULT_EVIDENCE_THRESHOLD` |
| 4 | Prepare citation-ready evidence | done | `grounding.build_grounded_context` emits document / chunk / section / page per block |
| 5 | Define strict grounding rules | done | `grounding.DAY3_SYSTEM_PROMPT` — the 8 rules from slide 13 |
| 6 | Define the structured answer format | done | `answer_schema.GroundedAnswer` (Pydantic, slide 14 shape) |
| 7 | Add insufficient-evidence behavior | done | threshold gate + rule 5 + fail-closed on invalid JSON — `grounded_run` |
| 8 | Add patient-specific safety behavior | done | `safety.check_patient_specific`, fires **before** retrieval; Stage 5 medication guardrails run first |
| 9 | Generate using retrieved evidence only | done | `LLMClient.generate_structured` |
| 10 | Connect each claim to a citation | done | `supporting_evidence[].citations[]` + `validate_citations` |
| 11 | **Verify each citation manually** | done (seeded + tool) | `clinic review` + `docs/day3/citation_review.csv` (lexical seed on screening Q; re-judge with `clinic review` as needed) |
| 12 | Test supported / unsupported / unsafe | done | `clinic test` → 10/10, `docs/day3/results.md` |
| 13 | Record at least one generation failure | done | two real ones, logged below |
| 14 | Explain how the failure was fixed | done | logged below |

**Caveat on step 2.** Chunk size/overlap (1024/100) is inherited from Day 2 and was **not**
re-validated. The Day 2 bake-off used Precision@k to compare chunk *sizes*, which cannot
work: a larger chunk is both more likely to contain the answer and more likely to be judged
relevant, so the configs are not the same unit. Keep the setting; do not cite that
comparison as evidence for it.

## The 11 deliverables (slide 30)

| deliverable | status |
|---|---|
| A working grounded answer layer | `clinic grounded` **and** `POST /query` / frontend workspace |
| Strict grounding rules | 8 rules, `DAY3_SYSTEM_PROMPT` |
| A structured answer format | `GroundedAnswer`, closed-set `status` and `confidence` |
| Citations with document, section, page, chunk ID | `SourceCitation` — all four fields |
| Citation coverage validation | `CitationReport.coverage`, claims-with-citations ÷ claims |
| Manual citation correctness review | seeded in `docs/day3/citation_review.csv`; refine via `clinic review` |
| Confidence labels | `final_confidence`, evidence-derived |
| Insufficient-evidence refusal | verified on 4 categories |
| Patient-specific safety refusal | verified on 3 categories |
| Results for supported / unsupported / unsafe | `docs/day3/results.md` |
| One documented generation failure + fix | two, below |

## Failure log (lab steps 13 and 14)

### Failure 1 — passage text pasted into the citation field

**Mode:** slide 30, *hallucinated citation*.
**Symptom:** with citations as free-text strings, the model copied the entire ~1000-char
evidence passage into `citations` instead of the short label. All 4 citations registered
as invented and the answer was refused — a correct refusal, but of a correct answer.
**Detected by:** `validate_citations` (automatic), which reported `invented 4`.
**Fix:** citations became **typed objects** (`document` / `chunk` / `section` / `page`),
taking the notebook's design over the slide's copied-string design. A field that must be a
document name cannot absorb a paragraph.
**Re-verified:** `Who should be screened for type 2 diabetes?` → 5/5 claims cited, 0
invented, confidence High.

### Failure 2 — evidence entries returned as JSON strings

**Mode:** slide 30, *schema violation* (rule 8 family).
**Symptom:** roughly 1 run in 3, `gpt-oss-120b` returned some `supporting_evidence`
elements as JSON-encoded **strings** — `'{"claim": ...}'` — and occasionally as empty
strings. Pydantic rejected the response, the retry produced the same shape, and the flow
failed closed to `insufficient_evidence`. Non-deterministic, so it would have appeared
during a live demo roughly one time in three.
**Detected by:** schema validation, visible in `StructuredResult.errors`.
**Fix:** a repair layer (`_repair_object_list`) decodes string elements that already encode
an object, and drops blank entries. Decoding a JSON string into the object it encodes
invents nothing; anything that does not decode is still rejected.
**Re-verified:** 5 consecutive runs, all `answered`, 1 attempt each, 0 invented.

## The required demonstration — answer → claim → citation → evidence

```bash
uv run clinic grounded "Who should be screened for type 2 diabetes?"
```

1. Read one claim, e.g. *"Adults aged 40 years or older should be screened for type 2 diabetes."*
2. Read its citation: `Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf … Chunk: CH-0079`
3. The output prints the trace line:
   `data/index/chunks.json -> Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf::79`
4. Open that id in `chunks.json` and read the literal retrieved text.

Trace by **chunk ID**, not page — see the known gap below.

## Step 11 — manual citation correctness review

Slide 22: coverage is mechanical, correctness is human. `clinic review` does everything
except the judging — it pairs each claim with the exact retrieved text, records your
verdict, and is resume-safe, so you can stop and continue later.

```bash
uv run clinic review                       # walk every answerable question in the matrix
uv run clinic review "Who should be screened for type 2 diabetes?"   # one question
uv run clinic review --report              # correctness summary
```

For each pair it prints the claim, the citation, a `chunks.json` trace line, and the full
retrieved text, then asks `1` supported / `0` not / `s` skip / `q` quit. Answer `0` and it
asks which of slide 21's binding failures applies:

| | mode | what it looks like |
|---|---|---|
| 1 | unrelated | cited chunk is real but discusses something else entirely |
| 2 | not-supporting | related topic, does not support this specific claim |
| 3 | shared-citation | one citation covering several claims, supporting only one |
| 4 | invented | reference was never in the retrieved evidence |
| 5 | too-general | evidence is real but too general for this narrower claim |
| 6 | meaning-changed | claim exaggerates, drops a condition, or changes clinical meaning |

Verdicts land in `docs/day3/citation_review.csv`, one row per claim-citation pair, written
immediately so quitting never loses finished work. `--report` gives the **citation
correctness** rate — the number coverage cannot give you, and the answer to end-of-day
question 4.

Judge strictly. Every one of those six modes survives a careless review precisely because
the citation still *looks* right.

## The 9 end-of-day questions (slide 31)

| # | question | answer |
|---|---|---|
| 1 | Only retrieved evidence? | Yes — rule 1, and every claim carries a validated citation |
| 2 | Unsupported claims removed? | Yes — an answer failing coverage is refused, not trimmed |
| 3 | Every important claim cited? | Yes — 100% coverage on both supported categories |
| 4 | Citations support the exact claims? | Seeded review: 4/4 supported on screening Q (`citation_review.csv`); refine with `clinic review` |
| 5 | Refuses weak evidence? | Yes — 4 categories return `insufficient_evidence` |
| 6 | Refuses patient-specific requests? | Yes — 3 categories, refused before retrieval |
| 7 | Confidence from evidence quality? | Yes — `final_confidence`; the model may lower it, never raise it |
| 8 | Trace to exact source text? | Yes — by chunk ID, per the demo above |
| 9 | Can explain one failure and its fix? | Yes — two, logged above |

## Known gaps — residual risks

1. **Page numbers improved after re-ingest (buffer_page fix).** Overlap flushes now advance
   `buffer_page` to the continuing page. Re-run `clinic ingest` after chunking changes.
   Trace identity remains document + chunk ID; pages are advisory and still PDF-extraction
   dependent.
2. **The retrieval threshold cannot filter by topic.** `clinic calibrate` shows supported
   and out-of-scope questions overlap on the fused score — off-topic *"treatment for
   melanoma"* scored 0.105, above on-topic *"HbA1c threshold"* at 0.103. The score is a
   fused rank value, not a similarity, so slide 26's example numbers do not transfer. The
   threshold only trims the weakest tail; grounding rule 5 does the topic filtering. This
   is defense in depth, and it is why the out-of-scope categories still refuse correctly.
3. **One supported question cannot be answered at all.** *"What HbA1c threshold is used to
   diagnose diabetes?"* — the diagnostic-criteria table exists in the corpus (8 copies) but
   never appears in the top 20 for that phrasing, with or without query rewriting. The
   chunk opens with boilerplate and the table is flattened into word-soup, so "diagnose"
   has nothing to match. The layer correctly refuses rather than reaching for the adjacent
   *A1C targets* table, which would confuse a treatment target with a diagnostic cutoff.
   Retrieval and PDF extraction, not the answer layer.

## Production wiring (post Day-3 lab)

- `POST /query` and `GET /health` use the **grounded** pipeline (`answer_question`), not the
  older free-text `run_query` path.
- Frontend workspace calls that API and renders recommendation → claim → citation chips
  (document · page · section).
- Stage 5 guardrails live in `backend/app/pipeline/guardrails.py` (medication / prescribing /
  jailbreak) and run **before** patient-specific safety and again on draft answers.
- API response schemas live in `backend/app/models/schemas.py` (`QueryResponse` keeps the UI
  contract; `guardrail.passed` / `conflict.detected` / `query` / `answer` are computed aliases).
