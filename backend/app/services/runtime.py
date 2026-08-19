"""Shared runtime resources for scalable API workers.

VectorStore loads the numpy index once per process; LLMClient reuses the process-global
embedder. Inject these into request handlers instead of reconstructing per call.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.config import Settings, get_settings
from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore


@dataclass
class AppState:
    settings: Settings
    store: VectorStore
    llm: LLMClient


_state: AppState | None = None


def init_app_state(settings: Settings | None = None) -> AppState:
    global _state
    cfg = settings or get_settings()
    _state = AppState(
        settings=cfg,
        store=VectorStore(cfg.vector_index_dir),
        llm=LLMClient(cfg),
    )
    return _state


def get_app_state() -> AppState:
    global _state
    if _state is None:
        return init_app_state()
    return _state


def reset_app_state() -> None:
    """Test helper — drop the singleton."""
    global _state
    _state = None
