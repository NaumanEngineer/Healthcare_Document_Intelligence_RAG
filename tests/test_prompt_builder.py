import pytest

from src.generation.prompt_builder import (
    DEFAULT_SYSTEM_INSTRUCTIONS,
    INSUFFICIENT_EVIDENCE_RESPONSE,
    validate_user_question,
    validate_evidence_packet,
    build_grounded_prompt,
)


def build_valid_packet() -> dict:
    return {
        "has_evidence": True,
        "evidence_count": 1,
        "formatted_context": (
            "[EVIDENCE 1]\n"
            "Document ID: DOC-001\n"
            "Title: Operational Escalation Policy\n"
            "Version: 1.0\n"
            "Status: Active\n"
            "Page: 3\n"
            "Chunk ID: DOC-001-V1.0-P003-C002\n"
            "Text:\n"
            "Operational leadership should review escalation conditions.\n"
            "[/EVIDENCE 1]"
        ),
        "citations": [
            {
                "chunk_id": "DOC-001-V1.0-P003-C002",
                "document_id": "DOC-001",
                "title": "Operational Escalation Policy",
                "version": "1.0",
                "page": 3,
            }
        ],
    }


def build_empty_packet() -> dict:
    return {
        "has_evidence": False,
        "evidence_count": 0,
        "formatted_context": "",
        "citations": [],
    }


def test_validate_user_question_accepts_valid_question():
    validate_user_question(
        "What should operational leadership do?"
    )


def test_validate_user_question_rejects_blank_question():
    with pytest.raises(
        ValueError,
        match="question must be a non-empty string",
    ):
        validate_user_question(
            "   "
        )


def test_validate_evidence_packet_accepts_valid_packet():
    validate_evidence_packet(
        build_valid_packet()
    )


def test_validate_evidence_packet_rejects_missing_field():
    packet = build_valid_packet()

    del packet["citations"]

    with pytest.raises(
        ValueError,
        match="Missing evidence packet field",
    ):
        validate_evidence_packet(
            packet
        )


def test_validate_evidence_packet_rejects_inconsistent_count():
    packet = build_valid_packet()

    packet["evidence_count"] = 2

    with pytest.raises(
        ValueError,
        match="citation count must match evidence_count",
    ):
        validate_evidence_packet(
            packet
        )


def test_build_grounded_prompt_generates_with_evidence():
    result = build_grounded_prompt(
        question=(
            "What should operational leadership do?"
        ),
        evidence_packet=build_valid_packet(),
    )

    assert result["should_generate"] is True
    assert result["fallback_response"] is None
    assert "USER QUESTION:" in result["user_prompt"]
    assert "APPROVED EVIDENCE:" in result["user_prompt"]
    assert "DOC-001-V1.0-P003-C002" in result["user_prompt"]
    assert len(result["citations"]) == 1


def test_build_grounded_prompt_abstains_without_evidence():
    result = build_grounded_prompt(
        question=(
            "What medication should be prescribed?"
        ),
        evidence_packet=build_empty_packet(),
    )

    assert result["should_generate"] is False
    assert result["user_prompt"] == ""
    assert result["citations"] == []
    assert (
        result["fallback_response"]
        == INSUFFICIENT_EVIDENCE_RESPONSE
    )


def test_system_prompt_contains_evidence_restriction():
    assert (
        "answer only from the evidence"
        in DEFAULT_SYSTEM_INSTRUCTIONS.lower()
    )


def test_system_prompt_contains_prompt_injection_rule():
    assert (
        "not as instructions"
        in DEFAULT_SYSTEM_INSTRUCTIONS.lower()
    )
