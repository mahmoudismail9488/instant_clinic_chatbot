"""Soft section bias for hybrid retrieval (Screening / Diagnosis / Monitoring / …)."""

from __future__ import annotations

from typing import Any, Literal

SectionFocus = Literal[
    "any",
    "screening",
    "diagnosis",
    "monitoring",
    "targets",
    "education",
]

SECTION_FOCUS_OPTIONS: tuple[SectionFocus, ...] = (
    "any",
    "screening",
    "diagnosis",
    "monitoring",
    "targets",
    "education",
)

# Keywords matched against section_title (strong) and chunk text (weak).
_FOCUS_KEYWORDS: dict[str, tuple[str, ...]] = {
    "screening": (
        "screen",
        "who to screen",
        "how to screen",
        "case finding",
        "risk factor",
        "prediabetes",
    ),
    "diagnosis": (
        "diagnos",
        "diagnostic",
        "criteria",
        "confirm",
        "definition",
    ),
    "monitoring": (
        "monitor",
        "follow-up",
        "follow up",
        "surveillance",
        "review",
        "measurement",
    ),
    "targets": (
        "target",
        "hba1c",
        "glycemic",
        "glycaemic",
        "blood pressure",
        "lipid",
    ),
    "education": (
        "education",
        "self-management",
        "self management",
        "lifestyle",
        "structured education",
    ),
}

_TITLE_BONUS = 0.02
_BODY_BONUS = 0.008


def normalize_section_focus(value: str | None) -> SectionFocus | None:
    if value is None:
        return None
    key = value.strip().lower()
    if not key or key == "any":
        return None
    if key in _FOCUS_KEYWORDS:
        return key  # type: ignore[return-value]
    return None


def section_match_bonus(
    *,
    section_title: str | None,
    text: str,
    focus: str | None,
) -> float:
    """Return a score bump when the chunk aligns with the chosen section focus."""
    normalized = normalize_section_focus(focus)
    if normalized is None:
        return 0.0
    keywords = _FOCUS_KEYWORDS[normalized]
    title = (section_title or "").lower()
    body = (text or "").lower()
    if any(k in title for k in keywords):
        return _TITLE_BONUS
    if any(k in body for k in keywords):
        return _BODY_BONUS
    return 0.0


def apply_section_bias(
    hits: list[dict[str, Any]],
    focus: str | None,
) -> list[dict[str, Any]]:
    """Re-rank hybrid/dense hits with a soft section bonus (never hard-filters)."""
    if normalize_section_focus(focus) is None or not hits:
        return hits

    boosted: list[dict[str, Any]] = []
    for hit in hits:
        meta = hit.get("metadata") or {}
        title = hit.get("section_title") or meta.get("section_title")
        text = str(hit.get("text", ""))
        bonus = section_match_bonus(
            section_title=str(title) if title else None,
            text=text,
            focus=focus,
        )
        row = dict(hit)
        row["score"] = float(hit.get("score", 0.0)) + bonus
        row["section_bonus"] = bonus
        boosted.append(row)

    boosted.sort(key=lambda h: float(h.get("score", 0.0)), reverse=True)
    return boosted
