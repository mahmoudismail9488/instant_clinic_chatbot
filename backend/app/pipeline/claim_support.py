"""Day 4 — unsupported-claim detector (second safety net).

Heuristic word-overlap check from the Day 4 notebook. Not a substitute for citation
validation; catches obvious generation drift a prompt alone can miss.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def extract_claims(text: str) -> list[str]:
    """Split recommendation text into rough clinical claims."""
    sentences = _SENTENCE_SPLIT.split((text or "").strip())
    return [s.strip() for s in sentences if len(s.split()) > 3]


def is_claim_supported(claim: str, evidence_text: str, *, min_overlap: float = 0.35) -> bool:
    """Word-overlap proxy for support (notebook Checkpoint 2)."""
    claim_words = {w.lower().strip(".,;:()") for w in claim.split() if len(w) > 3}
    evidence_words = {
        w.lower().strip(".,;:()") for w in evidence_text.split() if len(w) > 3
    }
    if not claim_words:
        return True
    overlap = len(claim_words & evidence_words) / len(claim_words)
    return overlap >= min_overlap


@dataclass(frozen=True)
class ClaimSupportReport:
    claims: tuple[str, ...]
    unsupported: tuple[str, ...]

    @property
    def total_claims(self) -> int:
        return len(self.claims)

    @property
    def unsupported_claim_rate(self) -> float:
        if not self.claims:
            return 0.0
        return len(self.unsupported) / len(self.claims)

    @property
    def faithfulness(self) -> float:
        """Supported claims ÷ total claims (higher is better)."""
        if not self.claims:
            return 1.0
        return 1.0 - self.unsupported_claim_rate

    @property
    def passed(self) -> bool:
        return not self.unsupported


def check_unsupported_claims(
    recommendation: str,
    evidence_text: str,
    *,
    min_overlap: float = 0.35,
) -> ClaimSupportReport:
    claims = extract_claims(recommendation)
    unsupported = tuple(
        c for c in claims if not is_claim_supported(c, evidence_text, min_overlap=min_overlap)
    )
    return ClaimSupportReport(claims=tuple(claims), unsupported=unsupported)
