"""Pydantic schemas for the HTTP API (frontend + OpenAPI).

Keeps the Day-3 grounded response contract the UI expects (`kind`, `question`,
`recommendation`, claim evidence) while accepting optional session metadata from
newer clients.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, computed_field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    topic: str | None = None
    session_id: str | None = None
    # Soft retrieval bias: screening | diagnosis | monitoring | targets | education | any
    section_focus: str | None = Field(
        default=None,
        description="Optional section bias for hybrid retrieval (screening, diagnosis, …).",
    )


class ChunkOut(BaseModel):
    id: str
    doc: str
    page: int | None = None
    section: str = ""
    section_number: str | None = None
    section_title: str | None = None
    score: float
    excerpt: str
    text: str = ""
    used: bool = True
    # Optional aliases some clients send/read
    source: str | None = None
    source_path: str | None = None
    chunk_id: str | None = None
    chunk_index: int | None = None


class CitationOut(BaseModel):
    doc: str
    page: int | None = None
    section: str = ""
    chunk_id: str
    excerpt: str = ""
    score: float = 0.0
    claim: str | None = None
    quote: str | None = None


class ConflictOut(BaseModel):
    has_conflict: bool
    summary: str | None = None
    sources: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def detected(self) -> bool:
        """Alias used by the uploaded schema draft (`ConflictOut.detected`)."""
        return self.has_conflict


class GuardrailOut(BaseModel):
    allowed: bool
    reason: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def passed(self) -> bool:
        """Alias used by the uploaded schema draft (`GuardrailOut.passed`)."""
        return self.allowed


class QueryResponse(BaseModel):
    kind: str  # "answer" | "refusal"
    id: str
    question: str
    rewritten_query: str = ""
    recommendation: str = ""
    detail: str = ""
    reason: str | None = None
    caution: str | None = None
    confidence: str = "medium"
    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Evidence-derived score in [0, 1]; pair with confidence label",
    )
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    supporting_evidence: list[Any] = Field(default_factory=list)
    chunks: list[ChunkOut] = Field(default_factory=list)
    citations: list[CitationOut] = Field(default_factory=list)
    conflict: ConflictOut | None = None
    guardrail: GuardrailOut | None = None
    blocked: bool = False
    # Day 3 grounded extras
    status: str | None = None
    safety_note: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    decision_path: list[str] = Field(default_factory=list)
    risk: dict[str, Any] | None = None
    claim_support: dict[str, Any] | None = None
    next_action: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def query(self) -> str:
        """Alias for clients that expect `query` instead of `question`."""
        return self.question

    @computed_field  # type: ignore[prop-decorator]
    @property
    def answer(self) -> str:
        """Alias for clients that expect `answer` instead of recommendation/detail."""
        return self.recommendation or self.detail


class HealthResponse(BaseModel):
    status: str
    index_size: int
    chunk_config: str
    pipeline: str = "grounded"
    version: str | None = "0.1.0"
