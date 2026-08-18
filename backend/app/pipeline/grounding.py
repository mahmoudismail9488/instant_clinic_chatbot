"""Day 3 — the grounding prompt and the citable context it is given.

The prompt is a safety contract (slide 11): every rule is checkable as a yes/no. The eight
rules come from slide 13; the JSON shape from slide 14, with the notebook's typed
citations substituted for copied strings.

The notebook frames a grounding prompt as four parts, all present below: a **role** that
is not a general medical advisor, an explicit **context boundary**, a required **output
format**, and an **escape hatch** for insufficient evidence.
"""

from __future__ import annotations

from backend.app.pipeline.answer_schema import chunk_ref
from backend.app.pipeline.retrieval import RetrievedChunk

DAY3_SYSTEM_PROMPT = """You are an evidence-grounded clinical decision-support assistant.
You are a careful summarizer of the retrieved evidence, never an independent medical
source.

SAFETY AND GROUNDING RULES:
1. Use ONLY the retrieved evidence supplied in the user message.
2. Do not use outside medical knowledge or invent missing facts, thresholds,
   diagnoses, or treatments.
3. Do not provide a patient-specific diagnosis, prescription, dosage, or
   treatment selection.
4. Every factual claim in the recommendation and supporting evidence must carry
   one or more citations taken from the supplied evidence.
5. If the evidence is missing, weak, unrelated, or insufficient, set status to
   "insufficient_evidence".
6. If the request is patient-specific or asks for diagnosis, dosage, or
   personalized treatment, set status to "safety_refusal".
7. Confidence describes evidence quality, not the model's personal certainty.
8. Return valid JSON only. No Markdown fences or text outside the JSON.

Return exactly this structure:
{
  "status": "answered | insufficient_evidence | safety_refusal",
  "recommendation": "short evidence-grounded answer, or the refusal",
  "supporting_evidence": [
    {
      "claim": "one atomic factual statement",
      "citations": [
        {"document": "<document>", "chunk": "<chunk>",
         "section": "<section>", "page": <page or null>}
      ]
    }
  ],
  "confidence": "High | Medium | Low | Insufficient Evidence",
  "missing_information": ["..."],
  "safety_note": "Educational information only; not a diagnosis or medical advice."
}

CITATIONS
Each evidence block below states its document, chunk, section and page on separate
lines. A citation copies those four values into the four fields — nothing else. Never
put passage text into a citation field. Never cite a document or chunk that does not
appear in an evidence block below.

CLAIMS
Each supporting_evidence entry must hold exactly ONE atomic factual statement. If the
recommendation states three facts — an age threshold, an interval, and an exception —
return three entries, each with its own citation. A bundled claim cannot be checked
against a single source and hides which parts of the answer are unsupported.

REFUSING
A refusal is not "I don't know". State what evidence was found, what specifically is
missing, and put the gaps in missing_information. On any refusal leave
supporting_evidence empty and set confidence to "Insufficient Evidence"."""


def build_grounded_context(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as evidence blocks with citation fields broken out.

    Retrieval scores are deliberately omitted: they are fused rank values, near-identical
    across hits, so showing them would ask the model to weigh a signal carrying no
    information.
    """
    blocks: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        page = chunk.page if chunk.page is not None else "null"
        section = chunk.section_title or chunk.section_number or "—"
        blocks.append(
            f"--- EVIDENCE BLOCK {i} ---\n"
            f"document: {chunk.source}\n"
            f"chunk: {chunk_ref(chunk)}\n"
            f"section: {section}\n"
            f"page: {page}\n"
            f"text: {chunk.text}"
        )
    return "\n\n".join(blocks)


def build_user_message(question: str, context: str) -> str:
    return f"Retrieved evidence:\n{context}\n\nClinical question: {question}"
