"""HTTP API: health + grounded Day-3/4 query pipeline."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.app.api.serialize import grounded_result_to_response
from backend.app.config import get_settings
from backend.app.models.schemas import HealthResponse, QueryRequest, QueryResponse
from backend.app.pipeline.grounded_run import answer_question
from backend.app.services.runtime import get_app_state

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = get_settings()
    state = getattr(request.app.state, "clinirag", None) or get_app_state()
    return HealthResponse(
        status="ok" if state.store.size > 0 else "empty_index",
        index_size=state.store.size,
        chunk_config=settings.active_chunk_config,
        pipeline="grounded",
        version="0.2.0",
    )


@router.post("/query", response_model=QueryResponse)
def query(body: QueryRequest, request: Request) -> QueryResponse:
    """Grounded pipeline: risk → safety → retrieve → cite → claim support → respond."""
    state = getattr(request.app.state, "clinirag", None) or get_app_state()
    try:
        result = answer_question(
            body.query,
            top_k=body.top_k,
            settings=state.settings,
            store=state.store,
            client=state.llm,
            section_focus=body.section_focus,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface LLM/infra failures
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc
    return grounded_result_to_response(result)
