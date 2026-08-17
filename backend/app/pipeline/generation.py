"""Stage 6 — generate an answer grounded in retrieved context."""

from backend.app.pipeline.evidence import format_location
from backend.app.pipeline.retrieval import RetrievedChunk
from backend.app.services.llm_client import LLMClient


def generate_answer(
    query: str,
    contexts: list[RetrievedChunk],
    client: LLMClient | None = None,
) -> str:
    llm = client or LLMClient()
    if not contexts:
        return "I could not find supporting guideline evidence for that question."

    blocks: list[str] = []
    for i, chunk in enumerate(contexts, start=1):
        loc = format_location(chunk.page, chunk.section_number, chunk.section_title)
        sec = chunk.section_title or "—"
        loc_bit = f", {loc}" if loc else ""
        blocks.append(
            f"[{i}] source={chunk.source} (chunk {chunk.chunk_index}, "
            f"score={chunk.score:.3f}{loc_bit}, section_title={sec})\n"
            f"{chunk.text}"
        )
    context_block = "\n\n".join(blocks)
    return llm.generate(query=query, context=context_block)
