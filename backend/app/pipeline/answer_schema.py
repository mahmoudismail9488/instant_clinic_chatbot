"""Day 3 — the structured answer contract, and the checks that verify it.

Shape follows slides 13/14 (status / recommendation / supporting_evidence / confidence /
missing_information / safety_note). Citations follow the Day 3 notebook's design: typed
objects rather than copied strings.

That citation choice is deliberate. With free-text citations the model pasted whole
passages into the citation field and every one registered as invented; with typed fields
`document` and `chunk` are checked independently and the failure cannot recur.

Three layers of checking live here and downstream, catching different things:

    schema      (Pydantic, this file)  is the response the right *shape*?
    validation  (validate_citations)   do the citations *exist* in what we retrieved?
    manual      (lab step 11)          does the cited text actually *support* the claim?
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.pipeline.retrieval import RetrievedChunk

SAFETY_NOTE = "Educational information only; not a diagnosis or medical advice."


class AnswerStatus(str, Enum):
    """Closed set — code branches on these, so free-text refusals are not allowed."""

    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    SAFETY_REFUSAL = "safety_refusal"


class ConfidenceLevel(str, Enum):
    """Evidence quality, not model certainty, and never a percentage (slide 27)."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INSUFFICIENT = "Insufficient Evidence"


_CONFIDENCE_ORDER = (
    ConfidenceLevel.INSUFFICIENT,
    ConfidenceLevel.LOW,
    ConfidenceLevel.MEDIUM,
    ConfidenceLevel.HIGH,
)


def weakest(*levels: ConfidenceLevel) -> ConfidenceLevel:
    """Least confident of the given levels. Confidence may fall, never rise."""
    return min(levels, key=_CONFIDENCE_ORDER.index)


def chunk_ref(chunk: RetrievedChunk) -> str:
    """Stable short chunk id, e.g. `CH-0079`.

    With the document name this is exact: the pair maps to `{source}::{chunk_index}` in
    `data/index/chunks.json`, which is what a reviewer opens when tracing a claim.
    """
    return f"CH-{chunk.chunk_index:04d}"


def store_id(chunk: RetrievedChunk) -> str:
    """The literal key in `data/index/chunks.json`, for manual review."""
    return f"{chunk.source}::{chunk.chunk_index}"


class SourceCitation(BaseModel):
    """Slide 18's citation fields, as typed values the model cannot fill with prose."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    document: str = Field(min_length=1)
    chunk: str = Field(min_length=1, description="e.g. CH-0079")
    section: str | None = None
    page: int | None = None

    def key(self) -> tuple[str, str]:
        """Identity used for the allow-list check: document + chunk only.

        Section and page are descriptive; page in particular is known-unreliable in the
        current index, so validating on it would reject correct citations.
        """
        return (self.document.strip().lower(), self.chunk.strip().upper())

    def render(self) -> str:
        section = self.section or "—"
        page = f"Page {self.page}" if self.page is not None else "Page n/a"
        return f"[{self.document} | Section: {section} | {page} | Chunk: {self.chunk}]"


def _repair_object_list(value: Any) -> Any:
    """Repair list elements the model encoded as JSON *strings* instead of objects.

    Observed in practice with `gpt-oss-120b`: roughly one run in three returns some
    `supporting_evidence` entries as `'{"claim": ...}'` strings, plus the occasional
    empty string. Decoding a JSON string into the object it already encodes invents
    nothing, so this is repair, not leniency — anything that does not decode to an
    object is left alone and fails validation normally.
    """
    if not isinstance(value, list):
        return value
    repaired: list[Any] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if not text:
                continue  # a blank entry carries no claim; drop it
            try:
                decoded = json.loads(text)
            except (ValueError, TypeError):
                repaired.append(item)  # let validation reject it
                continue
            if isinstance(decoded, dict):
                repaired.append(decoded)
            elif isinstance(decoded, list):
                repaired.extend(decoded)
            else:
                repaired.append(item)
        else:
            repaired.append(item)
    return repaired


class SupportingEvidence(BaseModel):
    """One atomic claim plus the citations supporting *that* claim (slide 20)."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    claim: str = Field(min_length=1)
    citations: list[SourceCitation] = Field(default_factory=list)

    @field_validator("citations", mode="before")
    @classmethod
    def _repair_citations(cls, value: Any) -> Any:
        return _repair_object_list(value)


class GroundedAnswer(BaseModel):
    """The structure slide 14 requires the model to return."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    status: AnswerStatus
    recommendation: str = Field(min_length=1)
    supporting_evidence: list[SupportingEvidence] = Field(default_factory=list)
    confidence: ConfidenceLevel
    missing_information: list[str] = Field(default_factory=list)
    safety_note: str = SAFETY_NOTE

    @field_validator("supporting_evidence", mode="before")
    @classmethod
    def _repair_evidence(cls, value: Any) -> Any:
        return _repair_object_list(value)

    @model_validator(mode="after")
    def _refusals_carry_no_evidence(self) -> GroundedAnswer:
        """Slides 16/17: refusals carry no evidence, by design.

        Coerced rather than rejected: emptying a refusal can only remove content, so it
        cannot introduce an unsupported claim, and it keeps a well-formed refusal out of
        a pointless retry loop.
        """
        if self.status is not AnswerStatus.ANSWERED:
            self.supporting_evidence = []
            self.confidence = ConfidenceLevel.INSUFFICIENT
        return self

    @model_validator(mode="after")
    def _answered_needs_evidence(self) -> GroundedAnswer:
        """The notebook's checkpoint 2: high confidence with no evidence is rejected."""
        if self.status is AnswerStatus.ANSWERED and not self.supporting_evidence:
            raise ValueError(
                "status 'answered' requires at least one supporting_evidence entry"
            )
        return self

    @model_validator(mode="after")
    def _safety_note_always_present(self) -> GroundedAnswer:
        if not self.safety_note.strip():
            self.safety_note = SAFETY_NOTE
        return self


def refusal(
    status: AnswerStatus,
    recommendation: str,
    *,
    missing_information: list[str] | None = None,
) -> GroundedAnswer:
    """Build a refusal locally, without asking the model."""
    return GroundedAnswer(
        status=status,
        recommendation=recommendation,
        supporting_evidence=[],
        confidence=ConfidenceLevel.INSUFFICIENT,
        missing_information=missing_information or [],
        safety_note=SAFETY_NOTE,
    )


# --------------------------------------------------------------------------------------
# Citation validation (slide 23) and confidence (slide 27)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CitationReport:
    total_claims: int
    claims_with_citations: int
    invented_citations: tuple[str, ...] = ()
    uncited_claims: tuple[str, ...] = ()
    unused_evidence: tuple[str, ...] = ()

    @property
    def coverage(self) -> float:
        """Slide 22: claims with citations / total important claims."""
        if self.total_claims == 0:
            return 0.0
        return self.claims_with_citations / self.total_claims

    @property
    def has_invented(self) -> bool:
        return bool(self.invented_citations)

    @property
    def passed(self) -> bool:
        """Full coverage, nothing invented. Says nothing about correctness."""
        return (
            self.total_claims > 0
            and not self.invented_citations
            and not self.uncited_claims
        )

    def failure_summary(self) -> str:
        parts: list[str] = []
        if self.total_claims == 0:
            parts.append("the answer made no citable claims")
        if self.invented_citations:
            parts.append(f"{len(self.invented_citations)} invented citation(s)")
        if self.uncited_claims:
            parts.append(f"{len(self.uncited_claims)} claim(s) with no citation")
        return "; ".join(parts)


def allowed_keys(chunks: list[RetrievedChunk]) -> set[tuple[str, str]]:
    """Allow-list built from the chunks actually placed in the model's context."""
    return {(c.source.strip().lower(), chunk_ref(c).upper()) for c in chunks}


def validate_citations(
    answer: GroundedAnswer,
    chunks: list[RetrievedChunk],
) -> CitationReport:
    """Slide 23's automatic checks: does every citation exist, does every claim have one."""
    allowed = allowed_keys(chunks)
    used: set[tuple[str, str]] = set()

    total = 0
    with_citations = 0
    invented: list[str] = []
    uncited: list[str] = []

    for item in answer.supporting_evidence:
        total += 1
        if item.citations:
            with_citations += 1
        else:
            uncited.append(item.claim)

        for citation in item.citations:
            if citation.key() in allowed:
                used.add(citation.key())
            else:
                # Slide 23: a citation absent from the retrieved evidence is invented.
                invented.append(citation.render())

    unused = tuple(
        sorted(f"{doc} {ch}" for doc, ch in (allowed - used))
    )
    return CitationReport(
        total_claims=total,
        claims_with_citations=with_citations,
        invented_citations=tuple(invented),
        uncited_claims=tuple(uncited),
        unused_evidence=unused,
    )


def evidence_confidence(
    chunks: list[RetrievedChunk],
    report: CitationReport,
    *,
    threshold: float,
) -> ConfidenceLevel:
    """Derive confidence from evidence quality alone (slide 27's inputs)."""
    if not chunks or report.total_claims == 0:
        return ConfidenceLevel.INSUFFICIENT
    if report.has_invented or report.uncited_claims:
        return ConfidenceLevel.LOW

    top = max(c.score for c in chunks)
    above = [c for c in chunks if c.score >= threshold]
    # Distinct *documents*, so one source repeated is never counted as corroboration.
    distinct_sources = {c.source for c in above}

    strong_retrieval = top >= threshold * 2 and len(above) >= 2
    complete = report.coverage >= 1.0

    if strong_retrieval and complete and len(distinct_sources) >= 2:
        return ConfidenceLevel.HIGH
    if complete and above:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def final_confidence(
    model_reported: ConfidenceLevel,
    chunks: list[RetrievedChunk],
    report: CitationReport,
    *,
    threshold: float,
) -> ConfidenceLevel:
    """Weakest of the model's claim and the evidence-derived level.

    The model may lower confidence — it sees nuance scores cannot — but may never raise
    it above what the evidence supports (slide 27).
    """
    return weakest(
        model_reported,
        evidence_confidence(chunks, report, threshold=threshold),
    )


_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def extract_json(raw: str) -> str:
    """Recover a JSON object from a fenced or padded response (grounding rule 8)."""
    text = (raw or "").strip()
    if not text:
        return ""
    text = _FENCE.sub("", text).strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text
