"""Stage 5 — safety / scope guardrails on query and draft answer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str | None = None


# Intentional demo blocks — not a full clinical safety system.
DISALLOWED_QUERY_PHRASES = (
    "ignore previous instructions",
    "prescribe me",
    "write a prescription",
    "controlled substance",
    "how to overdose",
)

DISALLOWED_ANSWER_PHRASES = (
    "as a licensed physician i prescribe",
    "take this exact dose without consulting",
)


def check_query(query: str) -> GuardrailResult:
    lowered = query.lower().strip()
    if not lowered:
        return GuardrailResult(allowed=False, reason="Empty query")
    for phrase in DISALLOWED_QUERY_PHRASES:
        if phrase in lowered:
            return GuardrailResult(allowed=False, reason=f"Blocked query pattern: {phrase}")
    return GuardrailResult(allowed=True)


def check_answer(answer: str) -> GuardrailResult:
    lowered = answer.lower().strip()
    if not lowered:
        return GuardrailResult(allowed=False, reason="Empty answer")
    for phrase in DISALLOWED_ANSWER_PHRASES:
        if phrase in lowered:
            return GuardrailResult(allowed=False, reason=f"Blocked answer pattern: {phrase}")
    return GuardrailResult(allowed=True)
