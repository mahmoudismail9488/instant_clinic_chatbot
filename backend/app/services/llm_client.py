"""LLM + embedding client — Groq chat, local embeddings (Groq has no embed models)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from openai import OpenAI

from backend.app.config import Settings, get_settings

if TYPE_CHECKING:  # pragma: no cover - import only for type checkers
    from backend.app.pipeline.answer_schema import GroundedAnswer

_embedder = None

# Day 3 structured generation. Applied per-request, so the free-text `chat()` path and its
# three existing callers keep exactly the behaviour they had.
STRUCTURED_TIMEOUT_SECONDS = 60.0
STRUCTURED_MAX_TOKENS = 1600


@dataclass(frozen=True)
class StructuredResult:
    """Outcome of one structured generation, including what went wrong."""

    answer: GroundedAnswer | None
    attempts: int
    raw_responses: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.answer is not None


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

    def chat(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self.settings.groq_ai_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content
        if content and content.strip():
            return content.strip()
        # Some Groq reasoning models may leave content empty; fall back if present.
        reasoning = getattr(response.choices[0].message, "reasoning", None)
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning.strip()
        return ""

    def generate_structured(
        self,
        *,
        system: str,
        user: str,
        max_attempts: int = 2,
    ) -> StructuredResult:
        """Day 3 — ask for a `GroundedAnswer` and return it only if it validates.

        Kept separate from `chat()` because the contract differs: this path fails closed.
        An unparseable or schema-invalid response never becomes an answer, it becomes a
        refusal decided by the caller.

        Failure handling, in order (rule 8 exists because models fence JSON by default):
            1. repair  strip Markdown fences / surrounding prose, re-parse
            2. retry   once, echoing the validation error back to the model
            3. refuse  give up and report why
        """
        # Imported here, not at module scope: `pipeline.retrieval` imports this module,
        # so a top-level import would be circular.
        from pydantic import ValidationError

        from backend.app.pipeline.answer_schema import GroundedAnswer, extract_json

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        raws: list[str] = []
        errors: list[str] = []

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.settings.groq_ai_model,
                    temperature=0.0,
                    max_tokens=STRUCTURED_MAX_TOKENS,
                    response_format={"type": "json_object"},
                    messages=messages,
                    timeout=STRUCTURED_TIMEOUT_SECONDS,
                )
            except Exception as exc:  # noqa: BLE001 - API failure must fail closed
                errors.append(f"attempt {attempt}: API call failed: {exc}")
                break

            message = response.choices[0].message
            raw = message.content or ""
            if not raw.strip():
                reasoning = getattr(message, "reasoning", None)
                raw = reasoning if isinstance(reasoning, str) else ""
            raws.append(raw)

            if not raw.strip():
                errors.append(f"attempt {attempt}: empty response")
            else:
                try:
                    answer = GroundedAnswer.model_validate_json(extract_json(raw))
                except (ValidationError, ValueError) as exc:
                    errors.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
                else:
                    return StructuredResult(
                        answer=answer,
                        attempts=attempt,
                        raw_responses=tuple(raws),
                        errors=tuple(errors),
                    )

            if attempt < max_attempts:
                # Echo the failure back, so the retry is informed rather than identical.
                messages = messages[:2] + [
                    {"role": "assistant", "content": raw[:2000]},
                    {
                        "role": "user",
                        "content": (
                            "That response was not valid against the required schema:\n"
                            f"{errors[-1]}\n\n"
                            "Return ONLY the JSON object described in the system "
                            "message. No Markdown fences, no commentary."
                        ),
                    },
                ]

        return StructuredResult(
            answer=None,
            attempts=len(raws) or max_attempts,
            raw_responses=tuple(raws),
            errors=tuple(errors),
        )

    def generate(self, *, query: str, context: str) -> str:
        system = (
            "You are GlucoRAG, a clinical decision-support assistant. "
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
        return self.chat(system=system, user=user, temperature=0.2)
