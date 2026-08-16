"""Stage 3 — embed chunks via Google embeddings."""

from backend.app.services.llm_client import LLMClient


def embed_texts(texts: list[str], client: LLMClient | None = None) -> list[list[float]]:
    llm = client or LLMClient()
    return llm.embed(texts)
