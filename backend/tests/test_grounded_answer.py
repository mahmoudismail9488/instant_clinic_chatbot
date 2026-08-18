"""Tests for the Day 3 grounded answer layer.

No network: everything here is schema, regex, and pure-function behaviour. The two things
most likely to be wrong are the safety gate and citation validation, so those get the most
cases.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.pipeline.answer_schema import (
    AnswerStatus,
    ConfidenceLevel,
    GroundedAnswer,
    SourceCitation,
    SupportingEvidence,
    chunk_ref,
    evidence_confidence,
    extract_json,
    final_confidence,
    refusal,
    store_id,
    validate_citations,
    weakest,
)
from backend.app.pipeline.grounded_run import dedupe_chunks
from backend.app.pipeline.grounding import build_grounded_context
from backend.app.pipeline.retrieval import RetrievedChunk
from backend.app.pipeline.safety import check_patient_specific


def chunk(
    idx: int, text: str = "text", *, source: str = "GuideA.pdf", score: float = 0.05
) -> RetrievedChunk:
    return RetrievedChunk(
        text=text,
        score=score,
        source=source,
        source_path=f"data/raw_guidelines/{source}",
        chunk_index=idx,
        page=3,
        section_number=None,
        section_title="Screening",
    )


def cite(c: RetrievedChunk) -> SourceCitation:
    """The citation a well-behaved model should emit for this chunk."""
    return SourceCitation(
        document=c.source, chunk=chunk_ref(c), section=c.section_title, page=c.page
    )


def answered(*items: SupportingEvidence, confidence=ConfidenceLevel.HIGH) -> GroundedAnswer:
    return GroundedAnswer(
        status=AnswerStatus.ANSWERED,
        recommendation="A recommendation.",
        supporting_evidence=list(items),
        confidence=confidence,
    )


# ------------------------------------------------------------------------- schema


def test_status_outside_the_closed_set_is_rejected():
    with pytest.raises(ValidationError):
        GroundedAnswer(
            status="probably",  # type: ignore[arg-type]
            recommendation="x",
            confidence=ConfidenceLevel.LOW,
        )


def test_percentage_confidence_is_rejected():
    """Slide 27: four labels, never a percentage."""
    with pytest.raises(ValidationError):
        answered(SupportingEvidence(claim="c"), confidence="85%")  # type: ignore[arg-type]


def test_answered_with_no_evidence_is_rejected():
    """The notebook's checkpoint 2: confident answer, zero evidence -> reject."""
    with pytest.raises(ValidationError):
        GroundedAnswer(
            status=AnswerStatus.ANSWERED,
            recommendation="Take 10mg daily.",
            supporting_evidence=[],
            confidence=ConfidenceLevel.HIGH,
        )


def test_citation_cannot_be_free_text():
    """The failure this schema exists to prevent: passage text pasted as a citation."""
    with pytest.raises(ValidationError):
        SupportingEvidence(claim="c", citations=["Screening of Type 2 Diabetes ..."])  # type: ignore[list-item]


def test_refusal_evidence_is_emptied_and_confidence_forced():
    """Slides 16 and 17: refusals carry no evidence, by design."""
    answer = GroundedAnswer(
        status=AnswerStatus.SAFETY_REFUSAL,
        recommendation="Cannot advise.",
        supporting_evidence=[
            SupportingEvidence(claim="c", citations=[cite(chunk(1))])
        ],
        confidence=ConfidenceLevel.HIGH,
    )
    assert answer.supporting_evidence == []
    assert answer.confidence is ConfidenceLevel.INSUFFICIENT


def test_safety_note_defaults_when_blank():
    answer = GroundedAnswer(
        status=AnswerStatus.ANSWERED,
        recommendation="x",
        supporting_evidence=[SupportingEvidence(claim="c", citations=[cite(chunk(1))])],
        confidence=ConfidenceLevel.LOW,
        safety_note="   ",
    )
    assert "not a diagnosis" in answer.safety_note


def test_weakest_never_upgrades():
    assert weakest(ConfidenceLevel.HIGH, ConfidenceLevel.LOW) is ConfidenceLevel.LOW
    assert weakest(ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH) is ConfidenceLevel.MEDIUM


def test_refusal_helper_is_always_valid():
    r = refusal(AnswerStatus.INSUFFICIENT_EVIDENCE, "no evidence")
    assert r.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert r.confidence is ConfidenceLevel.INSUFFICIENT
    assert r.supporting_evidence == []


# ------------------------------------------------------------------------- safety


@pytest.mark.parametrize(
    "question",
    [
        "Do I have diabetes?",
        "do i have got prediabetes",
        "Am I diabetic?",
        "What dose should I take?",
        "What dosage of metformin is right?",
        "Which treatment should I choose?",
        "What should I do?",
        "Can you diagnose me?",
        "Are my results normal?",
        "I'm 45 years old with a BMI of 32, should I be screened?",
        "Please prescribe me something.",
    ],
)
def test_patient_specific_questions_are_refused(question):
    assert check_patient_specific(question).patient_specific is True


@pytest.mark.parametrize(
    "question",
    [
        "Who should be screened for type 2 diabetes?",
        "What HbA1c threshold is used to diagnose diabetes?",
        "How is a suspicious result generally assessed?",
        "What lifestyle interventions are recommended for prediabetes?",
        "How often should high-risk adults be rescreened?",
        "What are the diagnostic criteria for gestational diabetes?",
    ],
)
def test_general_clinical_questions_are_allowed(question):
    assert check_patient_specific(question).patient_specific is False


def test_empty_question_is_not_flagged_as_patient_specific():
    assert check_patient_specific("").patient_specific is False


# --------------------------------------------------------------- citation checks


def test_context_exposes_exactly_the_citation_fields():
    """If context and allow-list ever disagree, every citation looks invented."""
    c = chunk(7)
    context = build_grounded_context([c])
    assert f"document: {c.source}" in context
    assert f"chunk: {chunk_ref(c)}" in context


def test_full_coverage_and_valid_citations_pass():
    c = chunk(7, "Screen adults over 40 every three years.")
    report = validate_citations(
        answered(SupportingEvidence(claim="Screen adults over 40.", citations=[cite(c)])),
        [c],
    )
    assert report.passed
    assert report.coverage == 1.0
    assert report.invented_citations == ()


def test_invented_chunk_is_caught():
    c = chunk(7)
    ghost = SourceCitation(document=c.source, chunk="CH-9999")
    report = validate_citations(
        answered(SupportingEvidence(claim="x", citations=[ghost])), [c]
    )
    assert report.has_invented
    assert not report.passed


def test_invented_document_is_caught():
    c = chunk(7)
    ghost = SourceCitation(document="Ghost.pdf", chunk=chunk_ref(c))
    report = validate_citations(
        answered(SupportingEvidence(claim="x", citations=[ghost])), [c]
    )
    assert report.has_invented


def test_wrong_page_does_not_invalidate_a_real_citation():
    """Page attribution is a known-broken upstream field; validating on it would
    reject correct citations. Identity is document + chunk."""
    c = chunk(7)
    off_by_pages = SourceCitation(document=c.source, chunk=chunk_ref(c), page=999)
    assert validate_citations(
        answered(SupportingEvidence(claim="x", citations=[off_by_pages])), [c]
    ).passed


def test_citation_matching_ignores_case_and_padding():
    c = chunk(7)
    sloppy = SourceCitation(document=c.source.upper(), chunk=chunk_ref(c).lower())
    assert validate_citations(
        answered(SupportingEvidence(claim="x", citations=[sloppy])), [c]
    ).passed


def test_uncited_claim_breaks_coverage():
    c = chunk(7)
    report = validate_citations(
        answered(
            SupportingEvidence(claim="cited", citations=[cite(c)]),
            SupportingEvidence(claim="uncited", citations=[]),
        ),
        [c],
    )
    assert report.coverage == 0.5
    assert report.uncited_claims == ("uncited",)
    assert not report.passed


def test_unused_evidence_is_reported():
    used, spare = chunk(1), chunk(2)
    report = validate_citations(
        answered(SupportingEvidence(claim="x", citations=[cite(used)])), [used, spare]
    )
    assert len(report.unused_evidence) == 1


# ----------------------------------------------------------------------- confidence


def test_invented_citation_caps_confidence_at_low():
    c = chunk(7, score=0.9)
    ghost = SourceCitation(document="Ghost.pdf", chunk="CH-0001")
    report = validate_citations(
        answered(SupportingEvidence(claim="x", citations=[ghost])), [c]
    )
    assert evidence_confidence([c], report, threshold=0.02) is ConfidenceLevel.LOW


def test_single_source_cannot_reach_high():
    c = chunk(7, score=0.9)
    report = validate_citations(
        answered(SupportingEvidence(claim="x", citations=[cite(c)])), [c]
    )
    assert final_confidence(ConfidenceLevel.HIGH, [c], report, threshold=0.02) is not (
        ConfidenceLevel.HIGH
    )


def test_two_distinct_documents_can_reach_high():
    a = chunk(1, source="GuideA.pdf", score=0.09)
    b = chunk(2, source="GuideB.pdf", score=0.08)
    report = validate_citations(
        answered(
            SupportingEvidence(claim="x", citations=[cite(a)]),
            SupportingEvidence(claim="y", citations=[cite(b)]),
        ),
        [a, b],
    )
    assert evidence_confidence([a, b], report, threshold=0.02) is ConfidenceLevel.HIGH


def test_model_may_lower_confidence_but_not_raise_it():
    a = chunk(1, source="GuideA.pdf", score=0.09)
    b = chunk(2, source="GuideB.pdf", score=0.08)
    report = validate_citations(
        answered(
            SupportingEvidence(claim="x", citations=[cite(a)]),
            SupportingEvidence(claim="y", citations=[cite(b)]),
        ),
        [a, b],
    )
    assert final_confidence(ConfidenceLevel.LOW, [a, b], report, threshold=0.02) is (
        ConfidenceLevel.LOW
    )


# ---------------------------------------------------------------------------- misc


def test_dedupe_keeps_highest_ranked_copy():
    first = chunk(1, "Same text.", score=0.20)
    second = chunk(12, "Same   text.", score=0.05)
    third = chunk(30, "Different.", score=0.04)
    unique = dedupe_chunks([first, second, third])
    assert len(unique) == 2
    assert unique[0].chunk_index == 1


def test_evidence_entries_encoded_as_json_strings_are_repaired():
    """Observed with gpt-oss-120b: ~1 run in 3 returns array items as JSON strings."""
    payload = {
        "status": "answered",
        "recommendation": "x",
        "supporting_evidence": [
            {"claim": "a real object", "citations": []},
            '{"claim": "a stringified object", "citations": []}',
            "   ",
        ],
        "confidence": "Low",
    }
    answer = GroundedAnswer.model_validate(payload)
    claims = [e.claim for e in answer.supporting_evidence]
    assert claims == ["a real object", "a stringified object"]


def test_repair_does_not_rescue_genuine_garbage():
    with pytest.raises(ValidationError):
        GroundedAnswer.model_validate(
            {
                "status": "answered",
                "recommendation": "x",
                "supporting_evidence": ["not json at all"],
                "confidence": "Low",
            }
        )


def test_store_id_matches_the_index_key_format():
    assert store_id(chunk(79)) == "GuideA.pdf::79"


@pytest.mark.parametrize(
    "raw",
    [
        '{"a": 1}',
        '```json\n{"a": 1}\n```',
        '```\n{"a": 1}\n```',
        'Here is the answer:\n{"a": 1}\nHope that helps.',
    ],
)
def test_extract_json_recovers_the_object(raw):
    assert extract_json(raw) == '{"a": 1}'
