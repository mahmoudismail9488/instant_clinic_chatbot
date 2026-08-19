"""Tests for hybrid RRF merge and section-focus bias."""

from __future__ import annotations

from backend.app.pipeline.hybrid_search import rrf_hybrid_merge
from backend.app.pipeline.section_focus import apply_section_bias, section_match_bonus


def test_rrf_prefers_docs_in_both_lists():
    dense = [
        {"id": "a", "text": "alpha screening ages", "score": 0.9},
        {"id": "b", "text": "beta lifestyle tips", "score": 0.8},
    ]
    corpus = [
        {"id": "b", "text": "beta lifestyle tips"},
        {"id": "a", "text": "alpha screening ages"},
        {"id": "c", "text": "gamma unrelated"},
    ]
    merged = rrf_hybrid_merge(dense, corpus, query="screening ages", top_k=2)
    assert len(merged) == 2
    assert merged[0]["id"] == "a"


def test_section_bonus_prefers_title_match():
    assert section_match_bonus(
        section_title="Who to screen",
        text="Age ≥40 years",
        focus="screening",
    ) > section_match_bonus(
        section_title="Lifestyle education",
        text="Offer structured education",
        focus="screening",
    )


def test_apply_section_bias_reranks():
    hits = [
        {
            "id": "1",
            "text": "Offer structured education programmes.",
            "section_title": "Education",
            "score": 0.03,
        },
        {
            "id": "2",
            "text": "Age ≥40 years or high risk — screen every 3 years.",
            "section_title": "Who to screen",
            "score": 0.029,
        },
    ]
    ranked = apply_section_bias(hits, "screening")
    assert ranked[0]["id"] == "2"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_any_focus_is_noop():
    hits = [{"id": "1", "text": "x", "section_title": "Who to screen", "score": 0.02}]
    assert apply_section_bias(hits, "any") == hits
    assert apply_section_bias(hits, None) == hits
