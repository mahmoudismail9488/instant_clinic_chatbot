"""Orchestrate ingest + full query pipeline for the CLI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from backend.app.config import Settings, get_settings
from backend.app.pipeline.chunking import chunk_units
from backend.app.pipeline.conflict_detection import ConflictReport, detect_conflicts
from backend.app.pipeline.embeddings import embed_texts
from backend.app.pipeline.evidence import Citation, build_citations
from backend.app.pipeline.generation import generate_answer
from backend.app.pipeline.guardrails import GuardrailResult, check_answer, check_query
from backend.app.pipeline.ingestion import ingest_directory
from backend.app.pipeline.query_rewrite import rewrite_query
from backend.app.pipeline.retrieval import RetrievedChunk, retrieve
from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore


@dataclass(frozen=True)
class QueryResult:
    answer: str
    chunks: list[RetrievedChunk]
    original_query: str
    rewritten_query: str
    citations: list[Citation] = field(default_factory=list)
    conflict: ConflictReport | None = None
    guardrail: GuardrailResult | None = None
    blocked: bool = False


def build_index(
    *,
    guidelines_dir: Path | None = None,
    txt_only: bool = False,
    rebuild: bool = True,
    settings: Settings | None = None,
) -> dict[str, int]:
    cfg = settings or get_settings()
    directory = guidelines_dir or cfg.raw_guidelines_dir
    store = VectorStore(cfg.vector_index_dir)
    client = LLMClient(cfg)

    if rebuild:
        store.clear()

    docs = ingest_directory(directory, txt_only=txt_only)
    total_chunks = 0

    for doc in docs:
        chunks = chunk_units(
            doc.units,
            source=doc.source,
            source_path=str(doc.source_path),
            chunk_size=cfg.chunk_size,
            overlap=cfg.chunk_overlap,
        )
        if not chunks:
            print(f"  · {doc.source}: 0 chunks")
            continue

        print(f"  · {doc.source}: {len(chunks)} chunks — embedding…")
        for start in range(0, len(chunks), cfg.embed_batch_size):
            batch = chunks[start : start + cfg.embed_batch_size]
            embeddings = embed_texts([c.text for c in batch], client=client)
            store.upsert(
                ids=[f"{c.source}::{c.index}" for c in batch],
                embeddings=embeddings,
                documents=[c.text for c in batch],
                metadatas=[
                    {
                        "source": c.source,
                        "source_path": c.source_path,
                        "chunk_index": c.index,
                        "page": c.page,
                        "section_number": c.section_number,
                        "section_title": c.section_title,
                    }
                    for c in batch
                ],
            )
        total_chunks += len(chunks)

    return {"documents": len(docs), "chunks": total_chunks, "index_size": store.size}


def run_query(
    query: str,
    *,
    top_k: int | None = None,
    settings: Settings | None = None,
    progress: Callable[[str], None] | None = None,
) -> QueryResult:
    """
    Pipeline:
      guard(query) → rewrite → retrieve → generate → guard(answer)
      → conflict_detection → evidence
    """
    def _progress(message: str) -> None:
        if progress is not None:
            progress(message)

    cfg = settings or get_settings()
    original = query.strip()

    query_guard = check_query(original)
    if not query_guard.allowed:
        return QueryResult(
            answer=f"Request blocked by guardrails: {query_guard.reason}",
            chunks=[],
            original_query=original,
            rewritten_query=original,
            guardrail=query_guard,
            blocked=True,
        )

    store = VectorStore(cfg.vector_index_dir)
    if store.size == 0:
        raise RuntimeError("Vector index is empty. Run: uv run clinic ingest")

    client = LLMClient(cfg)
    k = top_k or cfg.default_top_k

    _progress("1/4 Rewriting query…")
    rewritten = rewrite_query(original, client=client)
    _progress("2/4 Retrieving guideline chunks…")
    chunks = retrieve(rewritten, top_k=k, store=store, client=client)
    _progress(f"3/4 Generating answer from {len(chunks)} chunks…")
    answer = generate_answer(original, chunks, client=client)

    answer_guard = check_answer(answer)
    if not answer_guard.allowed:
        return QueryResult(
            answer=f"Answer blocked by guardrails: {answer_guard.reason}",
            chunks=chunks,
            original_query=original,
            rewritten_query=rewritten,
            citations=build_citations(chunks),
            guardrail=answer_guard,
            blocked=True,
        )

    _progress("4/4 Checking for guideline conflicts…")
    conflict = detect_conflicts(chunks, client=client)
    if conflict.has_conflict and conflict.summary:
        answer = f"{answer}\n\n⚠ Guideline conflict note:\n{conflict.summary}"

    citations = build_citations(chunks)
    return QueryResult(
        answer=answer,
        chunks=chunks,
        original_query=original,
        rewritten_query=rewritten,
        citations=citations,
        conflict=conflict,
        guardrail=answer_guard,
        blocked=False,
    )
