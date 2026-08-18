"""FastAPI endpoints for Instant Clinic Chatbot.

Wraps backend.app.pipeline.run (build_index / run_query) — the pipeline that
actually exists in this repo (rewrite -> retrieve -> generate -> guardrails
-> conflict detection -> evidence), backed by the numpy VectorStore.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.pipeline.chunking import chunk_units, infer_section_title
from backend.app.pipeline.embeddings import embed_texts
from backend.app.pipeline.ingestion import ingest_file
from backend.app.pipeline.run import build_index, run_query
from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore

app = FastAPI(title="Instant Clinic Chatbot")

SUPPORTED_SUFFIXES = {".pdf", ".txt"}


# ── Pydantic models ─────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    top_k: int | None = None


class CitationResponse(BaseModel):
    source: str
    excerpt: str
    score: float
    chunk_index: int
    page: int | None = None
    section_number: str | None = None
    section_title: str | None = None


class AnswerResponse(BaseModel):
    answer: str
    original_query: str
    rewritten_query: str
    citations: list[CitationResponse]
    blocked: bool
    guardrail_reason: str | None = None
    has_conflict: bool = False
    conflict_summary: str | None = None


class IngestResponse(BaseModel):
    documents: int
    chunks: int
    index_size: int


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_added: int
    index_size: int


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    settings = get_settings()
    store = VectorStore(settings.vector_index_dir)
    return {"status": "Instant Clinic Chatbot API is running", "index_size": store.size}


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Ingests a single new guideline file into the existing index (no rebuild)."""
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only PDF and TXT guidelines are supported.",
        )

    settings = get_settings()
    settings.raw_guidelines_dir.mkdir(parents=True, exist_ok=True)
    dest_path = settings.raw_guidelines_dir / filename

    try:
        contents = await file.read()
        dest_path.write_bytes(contents)

        doc = ingest_file(dest_path)
        chunks = chunk_units(
            doc.units,
            source=doc.source,
            source_path=str(doc.source_path),
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        if not chunks:
            raise HTTPException(status_code=422, detail=f"No extractable text in '{filename}'.")

        client = LLMClient(settings)
        store = VectorStore(settings.vector_index_dir)

        for start in range(0, len(chunks), settings.embed_batch_size):
            batch = chunks[start : start + settings.embed_batch_size]
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

        return UploadResponse(
            message=f"'{filename}' uploaded and indexed successfully.",
            filename=filename,
            chunks_added=len(chunks),
            index_size=store.size,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/ingest", response_model=IngestResponse)
def rebuild_index(txt_only: bool = False, rebuild: bool = True):
    """Rebuilds (or appends to) the index from everything in data/raw_guidelines/."""
    try:
        stats = build_index(txt_only=txt_only, rebuild=rebuild)
        return IngestResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index build failed: {str(e)}")


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        result = run_query(request.question, top_k=request.top_k)
    except RuntimeError as e:
        # e.g. "Vector index is empty. Run: uv run clinic ingest"
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    citations = [
        CitationResponse(
            source=c.source,
            excerpt=c.excerpt,
            score=c.score,
            chunk_index=c.chunk_index,
            page=c.page,
            section_number=c.section_number,
            section_title=infer_section_title(c.excerpt, c.section_title),
        )
        for c in result.citations
    ]

    return AnswerResponse(
        answer=result.answer,
        original_query=result.original_query,
        rewritten_query=result.rewritten_query,
        citations=citations,
        blocked=result.blocked,
        guardrail_reason=result.guardrail.reason if result.guardrail else None,
        has_conflict=bool(result.conflict and result.conflict.has_conflict),
        conflict_summary=result.conflict.summary if result.conflict else None,
    )
