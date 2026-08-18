"""Day 3 stage C — patient-specific safety refusal (slide 25).

Runs at flow step 2, *before retrieval*, and fires regardless of how good the evidence
is. A clinical education system does not answer "do I have this?" even when the guideline
is sitting right there.

The distinction is general-vs-personal, not topic-based:

    "What are the warning signs of type 2 diabetes?"  -> answer
    "How is a suspicious result generally assessed?"  -> answer
    "Do I have diabetes?"                             -> refuse
    "Which treatment should I choose?"                -> refuse
    "What dose should I take?"                        -> refuse

Deterministic on purpose. An LLM classifier would be more flexible, but this is a safety
gate: it must be reviewable, testable, and identical on every run. It is additive to
`guardrails.py`, which is left untouched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SAFETY_REFUSAL_TEXT = (
    "I cannot provide a patient-specific diagnosis, prescription, dosage, or treatment "
    "selection. Please consult a qualified clinician."
)


@dataclass(frozen=True)
class SafetyVerdict:
    patient_specific: bool
    reason: str | None = None
    matched: str | None = None


# Personal diagnosis: first person asking about their own condition.
_PERSONAL_DIAGNOSIS = re.compile(
    r"\b(?:do|have)\s+i\s+(?:have|got)\b"
    r"|\bam\s+i\s+(?:diabetic|prediabetic|at\s+risk|sick)\b"
    r"|\b(?:diagnose|assess|evaluate)\s+me\b"
    r"|\bmy\s+(?:results?|labs?|a1c|hba1c|glucose|blood\s+sugar|bmi|readings?)\b"
    r"|\bis\s+my\s+\w+\s+(?:normal|high|low|ok|okay|bad)\b",
    re.IGNORECASE,
)

# Dosage: asking how much of something to take.
_DOSAGE = re.compile(
    r"\bwhat\s+dose\b"
    r"|\bwhat\s+dosage\b"
    r"|\bhow\s+(?:much|many)\s+(?:should|do)\s+i\s+take\b"
    r"|\bhow\s+many\s+mg\b"
    r"|\b(?:prescribe|prescription)\s+(?:me|for\s+me)\b"
    r"|\bshould\s+i\s+(?:start|stop|take|increase|reduce)\s+\w+",
    re.IGNORECASE,
)

# Personalized treatment selection.
_PERSONAL_TREATMENT = re.compile(
    r"\bwhich\s+(?:treatment|medication|drug|therapy)\s+should\s+i\b"
    r"|\bwhat\s+should\s+i\s+(?:do|take)\b"
    r"|\bwhat\s+treatment\s+(?:is\s+best\s+)?for\s+me\b"
    r"|\btreat\s+me\b",
    re.IGNORECASE,
)

# Self-described personal clinical situation, e.g. "I'm 45 with a BMI of 32".
_PERSONAL_CONTEXT = re.compile(
    r"\bi(?:'m|\s+am)\s+(?:a\s+)?\d{1,3}\s*(?:years?\s*old|yo\b|y/o\b)"
    r"|\bmy\s+(?:doctor|gp|physician)\s+(?:said|told)\b"
    r"|\bi\s+(?:have|had|was\s+diagnosed\s+with)\s+(?:diabetes|prediabetes|type\s*[12])\b",
    re.IGNORECASE,
)

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (_PERSONAL_DIAGNOSIS, "personal diagnosis request"),
    (_DOSAGE, "dosage request"),
    (_PERSONAL_TREATMENT, "personalized treatment request"),
    (_PERSONAL_CONTEXT, "patient-specific clinical context"),
)


def check_patient_specific(question: str) -> SafetyVerdict:
    """Return a verdict for one question. Fires before retrieval."""
    text = (question or "").strip()
    if not text:
        return SafetyVerdict(patient_specific=False)

    for pattern, reason in _RULES:
        found = pattern.search(text)
        if found:
            return SafetyVerdict(
                patient_specific=True,
                reason=reason,
                matched=found.group(0).strip(),
            )
    return SafetyVerdict(patient_specific=False)
