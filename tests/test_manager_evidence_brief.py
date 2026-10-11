from src.evidence.manager_evidence_brief import (
    BRIEF_READY,
    BRIEF_REVIEW_REQUIRED,
    BRIEF_UNAVAILABLE,
    build_manager_evidence_brief,
)


def _base_packet():
    return {
        "packet_id": "EVIDENCE_PACKET::TEST1234",
        "question": "How should ambulance handover delays be managed?",
        "document_ids": [
            "DOC-008",
        ],
        "evidence_count": 1,
        "evidence_sufficiency": {
            "sufficient": True,
            "reason": "Retrieved evidence covers required topics.",
        },
        "missing_evidence": {
            "final_missing_topics": [],
            "unsupported_claims": [],
        },
        "provenance_summary": {
            "all_verified": True,
        },
        "lifecycle_summary": {
            "all_active": True,
        },
        "precedence_assessment": {
            "decision": "SAFE_TO_COMBINE",
            "reason": (
                "No explicit conflict, replacement or precedence "
                "relationship was established."
            ),
        },
        "governance": {
            "decision": "AUTO_ANSWER",
            "requires_human_review": False,
            "may_generate_answer": True,
            "reason": "Evidence is sufficient for the requested question.",
        },
    }


def test_builds_ready_manager_brief():
    packet = _base_packet()

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_READY

    assert brief[
        "document_summary"
    ][
        "document_count"
    ] == 1

    assert brief[
        "evidence_summary"
    ][
        "sufficient"
    ] is True

    assert brief[
        "assurance_summary"
    ][
        "provenance_verified"
    ] is True

    assert brief[
        "governance_summary"
    ][
        "may_generate_answer"
    ] is True


def test_review_required_when_governance_requires_human_review():
    packet = _base_packet()

    packet[
        "governance"
    ][
        "decision"
    ] = "REVIEW_REQUIRED"

    packet[
        "governance"
    ][
        "requires_human_review"
    ] = True

    packet[
        "governance"
    ][
        "may_generate_answer"
    ] = False

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_REVIEW_REQUIRED

    assert (
        brief[
            "governance_summary"
        ][
            "requires_human_review"
        ]
        is True
    )


def test_review_required_when_precedence_requires_review():
    packet = _base_packet()

    packet[
        "precedence_assessment"
    ][
        "decision"
    ] = "REVIEW_BEFORE_COMBINATION"

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_REVIEW_REQUIRED


def test_review_required_when_combination_is_blocked():
    packet = _base_packet()

    packet[
        "precedence_assessment"
    ][
        "decision"
    ] = "BLOCK_COMBINATION"

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_REVIEW_REQUIRED

    assert (
        "Do not combine"
        in brief[
            "manager_action"
        ]
    )


def test_unavailable_when_evidence_is_insufficient():
    packet = _base_packet()

    packet[
        "evidence_sufficiency"
    ][
        "sufficient"
    ] = False

    packet[
        "evidence_count"
    ] = 0

    packet[
        "governance"
    ][
        "decision"
    ] = "ABSTAIN"

    packet[
        "governance"
    ][
        "may_generate_answer"
    ] = False

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_UNAVAILABLE


def test_unavailable_when_no_evidence_objects_exist():
    packet = _base_packet()

    packet[
        "evidence_count"
    ] = 0

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "brief_status"
    ] == BRIEF_UNAVAILABLE


def test_document_ids_are_preserved():
    packet = _base_packet()

    packet[
        "document_ids"
    ] = [
        "DOC-008",
        "DOC-009",
    ]

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "document_summary"
    ][
        "document_ids"
    ] == [
        "DOC-008",
        "DOC-009",
    ]

    assert brief[
        "document_summary"
    ][
        "document_count"
    ] == 2


def test_missing_topics_are_preserved():
    packet = _base_packet()

    packet[
        "missing_evidence"
    ][
        "final_missing_topics"
    ] = [
        "severe_weather",
    ]

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "evidence_summary"
    ][
        "final_missing_topics"
    ] == [
        "severe_weather",
    ]


def test_unsupported_claims_are_preserved():
    packet = _base_packet()

    packet[
        "missing_evidence"
    ][
        "unsupported_claims"
    ] = [
        "contradiction_or_precedence_claim",
    ]

    brief = build_manager_evidence_brief(
        packet
    )

    assert brief[
        "evidence_summary"
    ][
        "unsupported_claims"
    ] == [
        "contradiction_or_precedence_claim",
    ]


def test_blank_packet_id_fails_closed():
    packet = _base_packet()

    packet[
        "packet_id"
    ] = "   "

    try:
        build_manager_evidence_brief(
            packet
        )

    except ValueError as error:
        assert "packet_id" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected blank packet_id to fail closed"
        )


def test_blank_question_fails_closed():
    packet = _base_packet()

    packet[
        "question"
    ] = "   "

    try:
        build_manager_evidence_brief(
            packet
        )

    except ValueError as error:
        assert "question" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected blank question to fail closed"
        )


def test_non_dictionary_packet_fails_closed():
    try:
        build_manager_evidence_brief(
            []
        )

    except TypeError as error:
        assert "packet" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected non-dictionary packet to fail closed"
        )