import pytest

from src.generation.evidence_formatter import (
    validate_evidence_record,
    build_citation_metadata,
    format_evidence_record,
    format_evidence_context,
    build_evidence_packet,
)


def build_valid_evidence() -> dict:
    return {
        "chunk_id": "DOC-001-V1.0-P003-C002",
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "version": "1.0",
        "status": "Active",
        "page": 3,
        "text": (
            "Operational leadership should review "
            "the current escalation conditions."
        ),
        "source_file": "operational_escalation_policy.pdf",
    }


def test_validate_evidence_record_accepts_valid_record():
    evidence = build_valid_evidence()

    validate_evidence_record(
        evidence
    )


def test_validate_evidence_record_rejects_missing_field():
    evidence = build_valid_evidence()

    del evidence["title"]

    with pytest.raises(
        ValueError,
        match="Missing required evidence field",
    ):
        validate_evidence_record(
            evidence
        )


def test_validate_evidence_record_rejects_superseded():
    evidence = build_valid_evidence()

    evidence["status"] = "Superseded"

    with pytest.raises(
        ValueError,
        match="Only Active evidence",
    ):
        validate_evidence_record(
            evidence
        )


def test_build_citation_metadata_preserves_source():
    evidence = build_valid_evidence()

    citation = build_citation_metadata(
        evidence
    )

    assert citation["document_id"] == "DOC-001"
    assert citation["page"] == 3
    assert citation["chunk_id"] == (
        "DOC-001-V1.0-P003-C002"
    )


def test_format_evidence_record_contains_citation_fields():
    evidence = build_valid_evidence()

    formatted = format_evidence_record(
        evidence=evidence,
        evidence_number=1,
    )

    assert "[EVIDENCE 1]" in formatted
    assert "DOC-001" in formatted
    assert "Page: 3" in formatted
    assert (
        "DOC-001-V1.0-P003-C002"
        in formatted
    )


def test_format_evidence_context_formats_multiple_records():
    evidence_one = build_valid_evidence()

    evidence_two = build_valid_evidence()
    evidence_two["chunk_id"] = (
        "DOC-001-V1.0-P004-C001"
    )
    evidence_two["page"] = 4

    context = format_evidence_context(
        [
            evidence_one,
            evidence_two,
        ]
    )

    assert "[EVIDENCE 1]" in context
    assert "[EVIDENCE 2]" in context


def test_format_evidence_context_empty_returns_empty_string():
    assert format_evidence_context(
        []
    ) == ""


def test_build_evidence_packet_with_evidence():
    evidence = build_valid_evidence()

    packet = build_evidence_packet(
        [evidence]
    )

    assert packet["has_evidence"] is True
    assert packet["evidence_count"] == 1
    assert len(packet["citations"]) == 1
    assert packet["formatted_context"]


def test_build_evidence_packet_without_evidence():
    packet = build_evidence_packet(
        []
    )

    assert packet["has_evidence"] is False
    assert packet["evidence_count"] == 0
    assert packet["citations"] == []
    assert packet["formatted_context"] == ""
