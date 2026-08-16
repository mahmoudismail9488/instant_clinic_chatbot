"""LLM + embedding client — Groq chat, local embeddings (Groq has no embed models)."""

from __future__ import annotations

from openai import OpenAI

from backend.app.config import Settings, get_settings

_embedder = None


def _get_embedder(model_name: str):
    global _embedder
    if _embedder is None:
        from fastembed import TextEmbedding

        _embedder = TextEmbedding(model_name=model_name)
    return _embedder


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if not self.settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is missing in backend/app/.env")

        groq_base = self.settings.groq_base_url.rstrip("/")
        if not groq_base.endswith("/openai/v1"):
            groq_base = f"{groq_base}/openai/v1"

        self._client = OpenAI(api_key=self.settings.groq_api_key, base_url=groq_base)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = _get_embedder(self.settings.embedding_model)
        payloads = [t[:8000] for t in texts]
        return [vec.tolist() for vec in model.embed(payloads)]

    def generate(self, *, query: str, context: str) -> str:
        system = (
            "You are Instant Clinic, a clinical decision-support assistant. "
            "Answer ONLY using the provided guideline excerpts. "
            "If the excerpts are insufficient, say you cannot find supporting guidance. "
            "Be concise, cite source filenames inline when possible, "
            "and do not invent dosages or recommendations absent from the excerpts."
        )
        user = (
            f"Question:\n{query}\n\n"
            f"Guideline excerpts:\n{context}\n\n"
            "Answer:"
        )
        response = self._client.chat.completions.create(
            model=self.settings.groq_ai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content
        return (content or "").strip()
