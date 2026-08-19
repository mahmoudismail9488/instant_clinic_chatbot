"""Stage 5 — safety / scope guardrails on query and draft answer."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str | None = None


# Refusal message for direct medication requests
MEDICATION_REFUSAL_MESSAGE = (
    "I cannot provide specific medication recommendations, prescriptions, or dosages. "
    "Please consult your doctor or a qualified healthcare provider for personalized treatment."
)

# Medication & prescription request patterns
DISALLOWED_QUERY_PHRASES = (
    "ignore previous instructions",
    "controlled substance",
    "how to overdose",
    "prescribe me",
    "write a prescription",
    "what medicine should i take",
    "what medication should i take",
    "what drug should i take",
    "what pills should i take",
    "give me medicine",
    "recommend me a drug",
    "prescribe",
    "dosage for me",
    "how many mg should i take",
    "can i take metformin",
    "can i take insulin",
)

# Regex pattern to catch conversational medication questions
MEDICATION_INTENT_PATTERN = re.compile(
    r"\b(prescribe|give me|what (medicine|medication|drug|pill) (should|can) i take|dosage for me)\b",
    re.IGNORECASE,
)

DISALLOWED_ANSWER_PHRASES = (
    "as a licensed physician i prescribe",
    "take this exact dose without consulting",
    "you should start taking",
    "take this medication",
)


def check_query(query: str) -> GuardrailResult:
    lowered = query.lower().strip()
    if not lowered:
        return GuardrailResult(allowed=False, reason="Empty query")
    
    # Check keyword list
    for phrase in DISALLOWED_QUERY_PHRASES:
        if phrase in lowered:
            return GuardrailResult(
                allowed=False,
                reason=MEDICATION_REFUSAL_MESSAGE
            )
            
    # Check regex pattern
    if MEDICATION_INTENT_PATTERN.search(lowered):
        return GuardrailResult(
            allowed=False,
            reason=MEDICATION_REFUSAL_MESSAGE
        )

    return GuardrailResult(allowed=True)


def check_answer(answer: str) -> GuardrailResult:
    lowered = answer.lower().strip()
    if not lowered:
        return GuardrailResult(allowed=False, reason="Empty answer")
    for phrase in DISALLOWED_ANSWER_PHRASES:
        if phrase in lowered:
            return GuardrailResult(
                allowed=False,
                reason="Direct prescribing detected in answer. Please consult a physician."
            )
    return GuardrailResult(allowed=True)