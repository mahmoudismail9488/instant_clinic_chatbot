from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "ok"
    version: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    query: str
    top_k: Optional[int] = None
    session_id: Optional[str] = None


class ChunkOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    doc: Optional[str] = None
    source: Optional[str] = ""
    source_path: Optional[str] = ""
    document: Optional[str] = None
    chunk: Optional[str] = None
    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = 0
    text: Optional[str] = ""
    score: Optional[float] = 0.0
    page: Optional[int] = None
    section: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    used: Optional[bool] = True


class CitationOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    doc: Optional[str] = None
    source: Optional[str] = ""
    source_path: Optional[str] = ""
    document: Optional[str] = None
    chunk: Optional[str] = None
    chunk_id: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    quote: Optional[str] = None
    claim: Optional[str] = None
    excerpt: Optional[str] = None
    text: Optional[str] = None
    used: Optional[bool] = True


class ConflictOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    detected: bool = False
    details: Optional[str] = None


class GuardrailOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    passed: bool = True
    reason: Optional[str] = None


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    query_id: Optional[str] = None
    query: str = ""
    answer: str = ""
    recommendation: Optional[str] = None
    chunks: List[ChunkOut] = Field(default_factory=list)
    citations: List[CitationOut] = Field(default_factory=list)
    supporting_evidence: List[Any] = Field(default_factory=list)
    conflict: Optional[ConflictOut] = None
    guardrail: Optional[GuardrailOut] = None
    status: Optional[str] = None
    confidence: Optional[str] = None
    missing_information: List[str] = Field(default_factory=list)
    safety_note: Optional[str] = None