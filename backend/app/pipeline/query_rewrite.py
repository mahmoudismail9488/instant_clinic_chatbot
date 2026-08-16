"""Stage 4.5 — rewrite the user query for better retrieval."""

from backend.app.services.llm_client import LLMClient


def rewrite_query(query: str, client: LLMClient | None = None) -> str:
    llm = client or LLMClient()
    system = (
        "Rewrite the clinical question into a short, self-contained search query "
        "optimized for retrieving diabetes screening guideline passages. "
        "Keep clinical terms (HbA1c, FPG, OGTT, age thresholds, risk factors). "
        "Return ONLY the rewritten query, with no quotes or explanation."
    )
    rewritten = llm.chat(system=system, user=query.strip(), temperature=0.0).strip()
    return rewritten or query.strip()
