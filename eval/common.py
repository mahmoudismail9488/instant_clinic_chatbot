"""Shared helpers for the GlucoRAG retrieval evaluation lab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.config import get_settings
from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore

EVAL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = EVAL_DIR / "outputs"
QUESTIONS_PATH = EVAL_DIR / "questions.json"

# All three configs are evaluated on the same corpus via isolated Qdrant collections.
CHUNK_CONFIGS = {
    "old": {
        "label": "Old config (pre-lab defaults)",
        "chunk_size": 1200,
        "overlap": 200,
        "collection": "guidelines_old",
    },
    "cfgA": {
        "label": "Config A",
        "chunk_size": 512,
        "overlap": 50,
        "collection": "guidelines_cfgA",
    },
    "cfgB": {
        "label": "Config B (selected / new system)",
        "chunk_size": 1024,
        "overlap": 100,
        "collection": "guidelines_cfgB",
        "selected": True,
    },
}

EVAL_CONFIG_KEYS = ("old", "cfgA", "cfgB")

SELECTED_CHUNK_CONFIG = "cfgB"
QDRANT_PATH = Path(__file__).resolve().parents[1] / "data" / "qdrant_lab"


def load_questions() -> list[dict[str, str]]:
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def format_section(section_number: Any, section_title: Any) -> str:
    parts: list[str] = []
    if section_number not in (None, ""):
        parts.append(str(section_number))
    if section_title not in (None, ""):
        parts.append(str(section_title))
    return " | ".join(parts)


def snippet(text: str, n: int = 240) -> str:
    cleaned = " ".join((text or "").split())
    return cleaned if len(cleaned) <= n else cleaned[: n - 1] + "…"


def retrieve_rows_from_numpy_store(
    *,
    questions: list[dict[str, str]],
    store: VectorStore,
    client: LLMClient,
    top_k: int,
    config: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for q in questions:
        qid = q["question_id"]
        query = q["question"]
        emb = client.embed([query])[0]
        hits = store.similarity_search(emb, top_k=top_k)
        for rank, hit in enumerate(hits, start=1):
            meta = hit.get("metadata") or {}
            page = hit.get("page", meta.get("page"))
            section_number = hit.get("section_number", meta.get("section_number")) or ""
            section_title = hit.get("section_title", meta.get("section_title")) or ""
            rows.append(
                {
                    "question_id": qid,
                    "question": query,
                    "config": config,
                    "rank": rank,
                    "chunk_id": hit.get("id") or f"{hit.get('source')}::{hit.get('chunk_index')}",
                    "score": float(hit["score"]),
                    "document": hit.get("source") or meta.get("source"),
                    "page": page if page is not None else "",
                    "section_number": section_number,
                    "section_title": section_title,
                    "section": format_section(section_number, section_title),
                    "chunk_text_snippet": snippet(str(hit.get("text", ""))),
                    "chunk_text": hit.get("text", ""),
                }
            )
    return rows


def save_retrieval_csv(rows: list[dict[str, Any]], path: Path) -> pd.DataFrame:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    cols = [
        "question_id",
        "rank",
        "chunk_id",
        "score",
        "document",
        "page",
        "section_number",
        "section_title",
        "section",
        "chunk_text_snippet",
        "chunk_text",
        "config",
        "question",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    for col in ("page", "section_number", "section_title", "section", "document", "chunk_id"):
        df[col] = df[col].fillna("").astype(str).replace({"nan": "", "None": ""})
    df.to_csv(path, index=False)
    return df


def default_baseline_store() -> VectorStore:
    return VectorStore(get_settings().vector_index_dir)
