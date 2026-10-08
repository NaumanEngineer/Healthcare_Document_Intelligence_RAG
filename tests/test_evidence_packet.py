from src.evidence.evidence_packet import (
    build_evidence_packet,
)


def _chunk(
    *,
    document_id="DOC-008",
    chunk_id="DOC-008-V1.0-P001-C001",
    status="Active",
):
    return {
        "document_id": document_id,
        "title": "Ambulance Handover Escalation Guidance",
        "document_type": "Operational Guidance",
        "source_type": "Synthetic",
        "source_location": (
            "data/raw/"
            "DOC-008_ambulance_handover_escalation_guidance.pdf"
        ),
        "source_file": (
            "DOC-008_ambulance_handover_escalation_guidance.pdf"
        ),
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "page": 1,
        "chunk_id": chunk_id,
        "chunk_number": 1,
        "text": (
            "Ambulance handover delays should be monitored "
            "as part of the wider urgent and emergency care "
            "pressure picture."
        ),
        "extraction_status": "success",
        "ingestion_batch_id": "batch-008",
        "similarity_score": 0.90,
    }


def _sufficient_output():
    return {
        "results": [
            _chunk(),
        ],
        "audit": {
            "scope": {
                "allowed": True,
                "reason": "In scope.",
            },
            "selected_route": "RETURN_INITIAL",
            "stop_reason": (
                "INITIAL_EVIDENCE_SUFFICIENT"
            ),
            "initial_retrieval_call_count": 1,
            "total_hybrid_retrieval_calls": 1,
            "routing_decision": {
                "missing_topics": [],
            },
            "final_evidence": {
                "sufficient": True,
                "decision": "SUFFICIENT",
                "reason": (
                    "Retrieved evidence covers required topics."
                ),
                "matched_query_terms": [
                    "ambulance_handover",
                ],
                "evidence_terms": [
                    "ambulance_handover",
                ],
                "result_count": 1,
                "topic_sufficient": True,
                "claim_sufficient": True,
                "claim_requirements": [],
                "unsupported_claims": [],
            },
        },
    }


def test_builds_packet_from_sufficient_retrieval():
    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        _sufficient_output(),
    )

    assert packet["question"] == (
        "How should ambulance handover delays be managed?"
    )

    assert packet["retrieval"]["route"] == (
        "RETURN_INITIAL"
    )

    assert packet["evidence_count"] == 1

    assert packet["document_ids"] == [
        "DOC-008",
    ]

    assert len(
        packet["evidence"]["supporting"]
    ) == 1


def test_packet_id_is_deterministic():
    question = (
        "How should ambulance handover delays be managed?"
    )

    packet_1 = build_evidence_packet(
        question,
        _sufficient_output(),
    )

    packet_2 = build_evidence_packet(
        question,
        _sufficient_output(),
    )

    assert (
        packet_1["packet_id"]
        == packet_2["packet_id"]
    )


def test_document_ids_are_deduplicated():
    output = _sufficient_output()

    output["results"] = [
        _chunk(
            chunk_id="DOC-008-V1.0-P001-C001",
        ),
        _chunk(
            chunk_id="DOC-008-V1.0-P002-C001",
        ),
    ]

    output["audit"][
        "final_evidence"
    ][
        "result_count"
    ] = 2

    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        output,
    )

    assert packet["document_ids"] == [
        "DOC-008",
    ]

    assert packet["evidence_count"] == 2


def test_lifecycle_summary_reports_all_active():
    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        _sufficient_output(),
    )

    assert packet[
        "lifecycle_summary"
    ][
        "status_counts"
    ] == {
        "Active": 1,
    }

    assert packet[
        "lifecycle_summary"
    ][
        "all_active"
    ] is True


def test_insufficient_evidence_produces_empty_evidence_set():
    output = _sufficient_output()

    output["results"] = []

    output["audit"][
        "selected_route"
    ] = "STOP_INSUFFICIENT"

    output["audit"][
        "stop_reason"
    ] = "NO_SAFE_RETRIEVAL_EXPANSION"

    output["audit"][
        "final_evidence"
    ] = {
        "sufficient": False,
        "decision": "INSUFFICIENT",
        "reason": "Required evidence is missing.",
        "matched_query_terms": [],
        "evidence_terms": [],
        "result_count": 0,
        "topic_sufficient": False,
        "claim_sufficient": False,
        "claim_requirements": [],
        "unsupported_claims": [],
    }

    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        output,
    )

    assert packet["evidence_count"] == 0
    assert packet["document_ids"] == []

    assert packet[
        "governance"
    ][
        "decision"
    ] == "ABSTAIN"


def test_out_of_scope_packet_contains_no_evidence():
    output = {
        "results": [],
        "audit": {
            "scope": {
                "allowed": False,
                "reason": "Question is outside approved scope.",
            },
            "selected_route": "STOP_OUT_OF_SCOPE",
            "stop_reason": "ORIGINAL_QUERY_OUT_OF_SCOPE",
            "initial_retrieval_call_count": 0,
            "total_hybrid_retrieval_calls": 0,
            "routing_decision": {},
            "final_evidence": None,
        },
    }

    packet = build_evidence_packet(
        "Who won the football match?",
        output,
    )

    assert packet["evidence_count"] == 0
    assert packet["document_ids"] == []

    assert packet[
        "governance"
    ][
        "decision"
    ] == "ABSTAIN"


def test_initial_missing_topic_is_recorded_but_not_final_when_recovered():
    output = _sufficient_output()

    output["audit"][
        "routing_decision"
    ][
        "missing_topics"
    ] = [
        "severe_weather",
    ]

    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        output,
    )

    assert packet[
        "missing_evidence"
    ][
        "initial_missing_topics"
    ] == [
        "severe_weather",
    ]

    assert packet[
        "missing_evidence"
    ][
        "final_missing_topics"
    ] == []


def test_unsupported_claims_are_preserved():
    output = _sufficient_output()

    output["audit"][
        "final_evidence"
    ][
        "unsupported_claims"
    ] = [
        "contradiction_or_precedence_claim",
    ]

    packet = build_evidence_packet(
        "How should ambulance handover delays be managed?",
        output,
    )

    assert packet[
        "missing_evidence"
    ][
        "unsupported_claims"
    ] == [
        "contradiction_or_precedence_claim",
    ]


def test_blank_question_fails_closed():
    try:
        build_evidence_packet(
            "   ",
            _sufficient_output(),
        )

    except ValueError as error:
        assert "question" in str(error)

    else:
        raise AssertionError(
            "Expected blank question to fail closed"
        )