"""Day 3 lab step 11 — manual citation correctness review (resume-safe).

Coverage is mechanical and already automated in `answer_schema.validate_citations`.
**Correctness is not.** Slide 22: an answer can score 100% coverage and still be full of
wrong citations, because a citation can exist, be well-formed, point at a real retrieved
chunk — and still not support the claim attached to it.

This module does not judge anything. It only puts the claim and the exact retrieved text
in front of a human and records the verdict, following slide 23's six steps:

    1. read the generated claim
    2. open the cited chunk
    3. read the exact retrieved text
    4. decide whether it supports the claim
    5. mark the pair supported or unsupported
    6. record the failure reason, if any

Keyed on (question, claim, document, chunk), so a session can be quit and resumed.
Modelled on `eval/label_relevance.py`, which does the same job for retrieval relevance.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from backend.app.pipeline.answer_schema import chunk_ref, store_id
from backend.app.pipeline.grounded_run import GroundedResult
from backend.app.pipeline.retrieval import RetrievedChunk

REVIEW_PATH = Path("docs/day3/citation_review.csv")

FIELDNAMES = (
    "question",
    "claim",
    "document",
    "chunk",
    "store_id",
    "supported",
    "failure_mode",
    "notes",
)

# Slide 21 — the five ways claim-to-evidence binding breaks. Each survives a careless
# review because the citation still *looks* correct.
FAILURE_MODES: tuple[tuple[str, str, str], ...] = (
    ("1", "unrelated", "Cited chunk is real but discusses something else entirely."),
    ("2", "not-supporting", "Related topic, but does not support this specific claim."),
    ("3", "shared-citation", "One citation covering several claims, supporting only one."),
    ("4", "invented", "Reference was never in the retrieved evidence."),
    ("5", "too-general", "Evidence is real but too general for this narrower claim."),
    ("6", "meaning-changed", "Claim exaggerates, drops a condition, or changes meaning."),
)


@dataclass(frozen=True)
class ReviewPair:
    """One claim-citation pair awaiting human judgement."""

    question: str
    claim: str
    document: str
    chunk: str
    store_id: str
    evidence_text: str

    def key(self) -> tuple[str, str, str, str]:
        return (self.question, self.claim, self.document, self.chunk)


def pairs_from_result(result: GroundedResult) -> list[ReviewPair]:
    """Expand an answered result into one row per claim-citation pair."""
    by_ref: dict[str, RetrievedChunk] = {chunk_ref(c): c for c in result.used}
    pairs: list[ReviewPair] = []
    for item in result.answer.supporting_evidence:
        for citation in item.citations:
            chunk = by_ref.get(citation.chunk.strip().upper())
            pairs.append(
                ReviewPair(
                    question=result.question,
                    claim=item.claim,
                    document=citation.document,
                    chunk=citation.chunk,
                    store_id=store_id(chunk) if chunk else "",
                    evidence_text=chunk.text if chunk else "(chunk not in retrieved evidence)",
                )
            )
    return pairs


def load_reviews(path: Path = REVIEW_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def reviewed_keys(rows: list[dict[str, str]]) -> set[tuple[str, str, str, str]]:
    return {
        (r.get("question", ""), r.get("claim", ""), r.get("document", ""), r.get("chunk", ""))
        for r in rows
    }


def append_review(row: dict[str, str], path: Path = REVIEW_PATH) -> None:
    """Write one verdict immediately, so quitting never loses completed work."""
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(FIELDNAMES))
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    """Citation correctness — the metric coverage cannot give you."""
    total = len(rows)
    supported = sum(1 for r in rows if str(r.get("supported", "")).strip() == "1")
    modes: dict[str, int] = {}
    for r in rows:
        mode = (r.get("failure_mode") or "").strip()
        if mode:
            modes[mode] = modes.get(mode, 0) + 1
    return {
        "total_pairs": total,
        "supported": supported,
        "unsupported": total - supported,
        "correctness": (supported / total) if total else 0.0,
        "failure_modes": modes,
    }
