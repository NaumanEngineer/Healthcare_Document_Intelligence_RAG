from src.evidence.evidence_from_retrieval import (
    build_evidence_from_retrieval,
)


def _chunk():
    return {
        "document_id": "DOC-008",
        "title": (
            "Ambulance Handover Escalation Guidance"
        ),
        "document_type": "Guidance",
        "source_type": "Synthetic",
        "source_location": (
            "data/raw/"
            "DOC-008_ambulance_handover_"
            "escalation_guidance.pdf"
        ),
        "source_file": (
            "DOC-008_ambulance_handover_"
            "escalation_guidance.pdf"
        ),
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "page": 2,
        "chunk_id": "DOC-008-V1.0-P002-C001",
        "chunk_number": 1,
        "text": (
            "Persistent ambulance handover delay "
            "requires operational escalation."
        ),
        "extraction_status": "success",
        "ingestion_batch_id": "batch-008",
    }


def test_builds_evidence_from_sufficient_retrieval():
    retrieval_output = {
        "results": [
            _chunk(),
        ],
        "audit": {
            "selected_route": (
                "RETURN_INITIAL"
            ),
            "final_evidence": {
                "sufficient": True,
            },
        },
    }

    evidence = (
        build_evidence_from_retrieval(
            retrieval_output
        )
    )

    assert len(evidence) == 1

    assert evidence[0][
        "document_id"
    ] == "DOC-008"

    assert evidence[0][
        "retrieval_route"
    ] == "RETURN_INITIAL"


def test_insufficient_retrieval_returns_no_evidence():
    retrieval_output = {
        "results": [
            _chunk(),
        ],
        "audit": {
            "selected_route": (
                "STOP_INSUFFICIENT"
            ),
            "final_evidence": {
                "sufficient": False,
            },
        },
    }

    evidence = (
        build_evidence_from_retrieval(
            retrieval_output
        )
    )

    assert evidence == []


def test_missing_results_fails_closed():
    retrieval_output = {
        "audit": {
            "selected_route": (
                "RETURN_INITIAL"
            ),
            "final_evidence": {
                "sufficient": True,
            },
        },
    }

    try:
        build_evidence_from_retrieval(
            retrieval_output
        )

    except ValueError as error:
        assert "results" in str(error)

    else:
        raise AssertionError(
            "Expected missing results to fail"
        )


def test_missing_route_fails_closed():
    retrieval_output = {
        "results": [
            _chunk(),
        ],
        "audit": {
            "final_evidence": {
                "sufficient": True,
            },
        },
    }

    try:
        build_evidence_from_retrieval(
            retrieval_output
        )

    except ValueError as error:
        assert "selected_route" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected missing route to fail"
        )


def test_missing_final_evidence_fails_closed():
    retrieval_output = {
        "results": [
            _chunk(),
        ],
        "audit": {
            "selected_route": (
                "RETURN_INITIAL"
            ),
        },
    }

    try:
        build_evidence_from_retrieval(
            retrieval_output
        )

    except ValueError as error:
        assert "final_evidence" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected missing final evidence to fail"
        )