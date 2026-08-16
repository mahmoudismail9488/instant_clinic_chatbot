"""Stage 6.5 — detect conflicting guidance across retrieved sources."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.pipeline.retrieval import RetrievedChunk
from backend.app.services.llm_client import LLMClient


@dataclass(frozen=True)
class ConflictReport:
    has_conflict: bool
    summary: str | None = None
    sources: tuple[str, ...] = ()


def detect_conflicts(
    chunks: list[RetrievedChunk],
    *,
    client: LLMClient | None = None,
) -> ConflictReport:
    sources = tuple(sorted({c.source for c in chunks if c.source}))
    if len(sources) < 2 or len(chunks) < 2:
        return ConflictReport(has_conflict=False, sources=sources)

    llm = client or LLMClient()
    numbered = "\n\n".join(
        f"[{i}] source={c.source}\n{c.text[:500]}" for i, c in enumerate(chunks, start=1)
    )
    system = (
        "You compare clinical guideline excerpts for material conflicts "
        "(different screening ages, thresholds, tests, or recommendations). "
        "If no material conflict, reply exactly: NO_CONFLICT. "
        "If there is a conflict, reply with one short paragraph starting with CONFLICT: "
        "naming the disagreeing sources and the disagreement."
    )
    raw = llm.chat(system=system, user=numbered, temperature=0.0).strip()
    upper = raw.upper()
    if upper.startswith("NO_CONFLICT") or "NO_CONFLICT" == upper:
        return ConflictReport(has_conflict=False, sources=sources, summary=None)
    summary = raw.removeprefix("CONFLICT:").removeprefix("conflict:").strip() or raw
    return ConflictReport(has_conflict=True, summary=summary, sources=sources)
