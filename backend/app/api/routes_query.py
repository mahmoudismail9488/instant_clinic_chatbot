"""HTTP API: health + grounded Day-3 query pipeline."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.api.serialize import grounded_result_to_response
from backend.app.config import get_settings
from backend.app.models.schemas import HealthResponse, QueryRequest, QueryResponse
from backend.app.pipeline.grounded_run import answer_question
from backend.app.services.vector_store import VectorStore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    store = VectorStore(settings.vector_index_dir)
    return HealthResponse(
        status="ok" if store.size > 0 else "empty_index",
        index_size=store.size,
        chunk_config=settings.active_chunk_config,
        pipeline="grounded",
    )


@router.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    """Run the Day 3 grounded pipeline (safety → retrieve → structured cite → validate)."""
    try:
        result = answer_question(body.query, top_k=body.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface LLM/infra failures
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc
    return grounded_result_to_response(result)
