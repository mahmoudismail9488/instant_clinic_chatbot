"""Stage 6 — generate an answer grounded in retrieved context."""

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
        blocks.append(
            f"[{i}] source={chunk.source} (chunk {chunk.chunk_index}, score={chunk.score:.3f})\n"
            f"{chunk.text}"
        )
    context_block = "\n\n".join(blocks)
    return llm.generate(query=query, context=context_block)
