"""Tests for PDF/section-aware chunking."""

from __future__ import annotations

from backend.app.pipeline.chunking import (
    _merge_broken_headings,
    _parse_heading,
    chunk_units,
)
from backend.app.pipeline.source_loader import PageUnit


def test_merge_broken_who_to_screen():
    merged = _merge_broken_headings(["Who", "to screen", "Age ≥40 years"])
    assert "Who to screen" in merged
    assert "Age ≥40 years" in merged


def test_parse_nice_dotted_section():
    sec = _parse_heading("1.5 HbA1c measurement and targets")
    assert sec is not None
    assert sec.number == "1.5"
    assert "HbA1c" in (sec.title or "")


def test_parse_known_screening_title():
    sec = _parse_heading("Screening of Type 2 Diabetes")
    assert sec is not None
    assert sec.title == "Screening of Type 2 Diabetes"


def test_parse_glued_how_to_screen():
    sec = _parse_heading("UPDATED FOR 2025 How to screen")
    assert sec is not None
    assert sec.title == "How to screen"


def test_chunk_units_attaches_section_titles():
    units = [
        PageUnit(
            text="\n".join(
                [
                    "Who",
                    "to screen",
                    "Age ≥40 years or high risk — screen every 3 years.",
                    "1.5 HbA1c measurement and targets",
                    "Measure HbA1c at 3–6 monthly intervals.",
                ]
            ),
            page=3,
        )
    ]
    chunks = chunk_units(
        units,
        source="Guide.pdf",
        source_path="Guide.pdf",
        chunk_size=200,
        overlap=20,
    )
    assert chunks
    titles = {c.section_title for c in chunks if c.section_title}
    assert "Who to screen" in titles or any(
        t and "screen" in t.lower() for t in titles
    )
    assert any(c.section_number == "1.5" for c in chunks) or any(
        t and "HbA1c" in t for t in titles
    )
