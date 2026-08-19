"""Day 4 — input risk classification (slide 7 decision table).

Runs before retrieval/generation. Categories map to whether generation continues,
clarification is needed, or a hard refusal is required.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    IN_SCOPE = "in_scope"
    AMBIGUOUS = "ambiguous"
    PATIENT_SPECIFIC = "patient_specific"
    DIAGNOSIS_REQUEST = "diagnosis_request"
    MEDICATION_DOSAGE = "medication_dosage"
    EMERGENCY = "emergency"
    OUT_OF_DOMAIN = "out_of_domain"
    ADVERSARIAL = "adversarial"


class RiskAction(str, Enum):
    CONTINUE = "continue"
    CLARIFY = "clarify"
    REFUSE = "refuse"
    EMERGENCY_REDIRECT = "emergency_redirect"


@dataclass(frozen=True)
class RiskVerdict:
    category: RiskCategory
    level: RiskLevel
    action: RiskAction
    continue_generation: bool
    reason: str
    matched: str | None = None


_EMERGENCY = re.compile(
    r"\b(?:crushing\s+chest\s+pain|can'?t\s+breathe|not\s+breathing|"
    r"unconscious|overdose|suicid|bleeding\s+(?:a\s+lot|heavily|now)|"
    r"stroke\s+symptoms?|call\s+911|right\s+now.{0,40}(?:dose|help|dying))\b",
    re.IGNORECASE,
)

_ADVERSARIAL = re.compile(
    r"\bignore\s+(?:previous|prior|the)\s+(?:instructions?|evidence|guidelines?|context)\b|"
    r"\bdisregard\s+(?:the\s+)?(?:retrieved|evidence|guidelines?)\b|"
    r"\buse\s+your\s+own\s+knowledge\b|"
    r"\bdo\s+not\s+cite\b|"
    r"\bjailbreak\b",
    re.IGNORECASE,
)

_MEDICATION = re.compile(
    r"\b(?:what\s+(?:dose|dosage|medicine|medication|drug|pills?)\b|"
    r"how\s+(?:much|many)\s+(?:mg|should\s+i\s+take)|"
    r"prescribe(?:\s+me)?|"
    r"can\s+i\s+take\s+\w+|"
    r"dosage\s+for\s+me)\b",
    re.IGNORECASE,
)

_DIAGNOSIS = re.compile(
    r"\b(?:do|have)\s+i\s+(?:have|got)\b|"
    r"\bam\s+i\s+(?:diabetic|prediabetic|at\s+risk)\b|"
    r"\bdiagnose\s+me\b|"
    r"\bdo\s+i\s+have\s+(?:diabetes|melanoma|cancer|hypertension)\b",
    re.IGNORECASE,
)

_PATIENT_SPECIFIC = re.compile(
    r"\b(?:should\s+i\s+(?:biopsy|start|stop|take|choose)|"
    r"which\s+treatment\s+should\s+i|"
    r"what\s+should\s+i\s+(?:do|take)|"
    r"treat\s+me|"
    r"my\s+(?:results?|labs?|a1c|hba1c|doctor)|"
    r"i(?:'m|\s+am)\s+(?:a\s+)?\d{1,3}\s*(?:years?\s*old|yo))\b",
    re.IGNORECASE,
)

_OUT_OF_DOMAIN = re.compile(
    r"\b(?:weather|stock\s+price|recipe|movie|football|crypto|"
    r"write\s+(?:me\s+)?(?:a\s+)?poem|tell\s+me\s+a\s+joke)\b",
    re.IGNORECASE,
)

_AMBIGUOUS = re.compile(
    r"^(?:what\s+should\s+be\s+checked\??|is\s+this\s+(?:bad|ok|serious)\??|"
    r"what\s+do\s+i\s+do\??|help\??|advise\s+me\??)$",
    re.IGNORECASE,
)

# Ordered: first match wins (critical → refuse categories before soft ones).
_RULES: tuple[tuple[re.Pattern[str], RiskCategory, RiskLevel, RiskAction, str], ...] = (
    (_EMERGENCY, RiskCategory.EMERGENCY, RiskLevel.CRITICAL, RiskAction.EMERGENCY_REDIRECT,
     "Emergency-like wording — seek immediate care"),
    (_ADVERSARIAL, RiskCategory.ADVERSARIAL, RiskLevel.CRITICAL, RiskAction.REFUSE,
     "Adversarial / injection attempt — stay grounded, do not override evidence"),
    (_MEDICATION, RiskCategory.MEDICATION_DOSAGE, RiskLevel.HIGH, RiskAction.REFUSE,
     "Medication or dosage request — requires a clinician"),
    (_DIAGNOSIS, RiskCategory.DIAGNOSIS_REQUEST, RiskLevel.HIGH, RiskAction.REFUSE,
     "Personal diagnosis request — not a diagnostic system"),
    (_PATIENT_SPECIFIC, RiskCategory.PATIENT_SPECIFIC, RiskLevel.HIGH, RiskAction.REFUSE,
     "Patient-specific treatment request — redirect to a clinician"),
    (_OUT_OF_DOMAIN, RiskCategory.OUT_OF_DOMAIN, RiskLevel.MEDIUM, RiskAction.REFUSE,
     "Out-of-domain — outside guideline scope"),
    (_AMBIGUOUS, RiskCategory.AMBIGUOUS, RiskLevel.MEDIUM, RiskAction.CLARIFY,
     "Ambiguous question — ask for a clearer guideline-focused question"),
)


EMERGENCY_MESSAGE = (
    "This sounds like a possible medical emergency. Call emergency services immediately "
    "(112 / 911 / local equivalent). This system cannot provide acute care advice."
)

CLARIFY_MESSAGE = (
    "Your question is too broad to answer safely from guidelines. "
    "Please ask about a specific screening, diagnosis criterion, or population-level recommendation."
)

ADVERSARIAL_MESSAGE = (
    "I cannot ignore retrieved guideline evidence or follow instructions that bypass grounding. "
    "Please ask a clinical guideline question."
)

OUT_OF_DOMAIN_MESSAGE = (
    "That question is outside the indexed clinical guideline corpus. "
    "Ask about diabetes screening or related guideline recommendations."
)


def classify_input_risk(question: str) -> RiskVerdict:
    """Classify one user question. Deterministic and reviewable."""
    text = (question or "").strip()
    if not text:
        return RiskVerdict(
            category=RiskCategory.AMBIGUOUS,
            level=RiskLevel.MEDIUM,
            action=RiskAction.CLARIFY,
            continue_generation=False,
            reason="Empty query",
        )

    for pattern, category, level, action, reason in _RULES:
        found = pattern.search(text)
        if found:
            return RiskVerdict(
                category=category,
                level=level,
                action=action,
                continue_generation=action is RiskAction.CONTINUE,
                reason=reason,
                matched=found.group(0).strip(),
            )

    return RiskVerdict(
        category=RiskCategory.IN_SCOPE,
        level=RiskLevel.LOW,
        action=RiskAction.CONTINUE,
        continue_generation=True,
        reason="In-scope guideline question",
    )


def refusal_text_for(verdict: RiskVerdict) -> str:
    if verdict.action is RiskAction.EMERGENCY_REDIRECT:
        return EMERGENCY_MESSAGE
    if verdict.action is RiskAction.CLARIFY:
        return CLARIFY_MESSAGE
    if verdict.category is RiskCategory.ADVERSARIAL:
        return ADVERSARIAL_MESSAGE
    if verdict.category is RiskCategory.OUT_OF_DOMAIN:
        return OUT_OF_DOMAIN_MESSAGE
    if verdict.category in {
        RiskCategory.MEDICATION_DOSAGE,
        RiskCategory.DIAGNOSIS_REQUEST,
        RiskCategory.PATIENT_SPECIFIC,
    }:
        return (
            "I cannot provide a patient-specific diagnosis, prescription, dosage, or treatment "
            "selection. Please consult a qualified clinician."
        )
    return verdict.reason
