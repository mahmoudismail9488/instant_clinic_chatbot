"""Stage 4 — retrieve top-k chunks from the vector store."""

from dataclasses import dataclass

from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    score: float
    source: str
    source_path: str
    chunk_index: int
    page: int | None = None
    section_number: str | None = None
    section_title: str | None = None


def retrieve(
    query: str,
    *,
    top_k: int = 5,
    store: VectorStore | None = None,
    client: LLMClient | None = None,
) -> list[RetrievedChunk]:
    llm = client or LLMClient()
    vector_store = store or VectorStore()
    query_embedding = llm.embed([query])[0]
    hits = vector_store.similarity_search(query_embedding, top_k=top_k)
    results: list[RetrievedChunk] = []
    for hit in hits:
        meta = hit.get("metadata") or {}
        page = hit.get("page", meta.get("page"))
        section_number = hit.get("section_number", meta.get("section_number"))
        section_title = hit.get("section_title", meta.get("section_title"))
        results.append(
            RetrievedChunk(
                text=hit["text"],
                score=float(hit["score"]),
                source=str(hit["source"]),
                source_path=str(hit.get("source_path", "")),
                chunk_index=int(hit.get("chunk_index", 0)),
                page=int(page) if page is not None else None,
                section_number=str(section_number) if section_number else None,
                section_title=str(section_title) if section_title else None,
            )
        )
    return results
