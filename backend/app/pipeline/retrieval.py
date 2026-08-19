"""Stage 4 — retrieve top-k chunks using hybrid search (Dense + BM25 RRF)."""

from dataclasses import dataclass

from backend.app.pipeline.chunking import infer_section_title
from backend.app.pipeline.hybrid_search import rrf_hybrid_merge
from backend.app.pipeline.section_focus import apply_section_bias
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
    use_hybrid: bool = True,
    section_focus: str | None = None,
) -> list[RetrievedChunk]:
    llm = client or LLMClient()
    vector_store = store or VectorStore()

    # Over-fetch so section bias / hybrid fusion can re-rank before the cut.
    pool = max(top_k * 4, 12)
    query_embedding = llm.embed([query])[0]
    dense_hits = vector_store.similarity_search(query_embedding, top_k=pool)

    if use_hybrid:
        bm25, all_docs = vector_store.get_bm25()
        hits = rrf_hybrid_merge(
            dense_hits,
            all_docs,
            query=query,
            top_k=pool,
            n_candidates=pool,
            bm25=bm25,
        )
    else:
        hits = dense_hits

    hits = apply_section_bias(hits, section_focus)[:top_k]

    results: list[RetrievedChunk] = []
    for hit in hits:
        meta = hit.get("metadata") or {}
        page = hit.get("page", meta.get("page"))
        section_number = hit.get("section_number", meta.get("section_number"))
        section_title = hit.get("section_title", meta.get("section_title"))
        text = str(hit["text"])
        results.append(
            RetrievedChunk(
                text=text,
                score=float(hit["score"]),
                source=str(hit.get("source", meta.get("source", ""))),
                source_path=str(hit.get("source_path", meta.get("source_path", ""))),
                chunk_index=int(hit.get("chunk_index", meta.get("chunk_index", 0))),
                page=int(page) if page is not None else None,
                section_number=str(section_number) if section_number else None,
                section_title=infer_section_title(
                    text, str(section_title) if section_title else None
                ),
            )
        )
    return results
