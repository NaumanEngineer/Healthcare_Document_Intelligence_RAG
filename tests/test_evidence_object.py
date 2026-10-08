from src.evidence.evidence_object import (
    build_evidence_object,
    build_evidence_objects,
)


def _chunk():
    return {
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "document_type": "Policy",
        "source_type": "Synthetic",
        "source_location": (
            "data/raw/"
            "DOC-001_operational_escalation_policy.pdf"
        ),
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "source_file": (
            "DOC-001_operational_escalation_policy.pdf"
        ),
        "page": 2,
        "chunk_id": "DOC-001-V1.0-P002-C001",
        "chunk_number": 1,
        "text": (
            "Escalation triggers may include sustained "
            "bed occupancy pressure."
        ),
        "extraction_status": "success",
        "ingestion_batch_id": "batch-123",
    }


def test_build_evidence_object_preserves_provenance():
    chunk = _chunk()

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RETURN_INITIAL",
    )

    assert evidence["evidence_id"] == (
        "EVIDENCE::DOC-001-V1.0-P002-C001"
    )

    assert evidence["document_id"] == "DOC-001"
    assert evidence["chunk_id"] == (
        "DOC-001-V1.0-P002-C001"
    )
    assert evidence["title"] == (
        "Operational Escalation Policy"
    )
    assert evidence["version"] == "1.0"
    assert evidence["status"] == "Active"
    assert evidence["page"] == 2
    assert evidence["chunk_number"] == 1
    assert evidence["ingestion_batch_id"] == (
        "batch-123"
    )
    assert evidence["retrieval_route"] == (
        "RETURN_INITIAL"
    )
    assert evidence["evidence_role"] == (
        "supporting"
    )


def test_evidence_text_is_preserved_exactly():
    chunk = _chunk()

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RETURN_INITIAL",
    )

    assert evidence["evidence_text"] == (
        chunk["text"]
    )


def test_missing_required_field_fails_closed():
    chunk = _chunk()

    del chunk["source_file"]

    try:
        build_evidence_object(
            chunk,
            retrieval_route="RETURN_INITIAL",
        )

    except ValueError as error:
        assert "source_file" in str(error)

    else:
        raise AssertionError(
            "Expected missing provenance to fail closed"
        )


def test_empty_evidence_text_fails_closed():
    chunk = _chunk()

    chunk["text"] = "   "

    try:
        build_evidence_object(
            chunk,
            retrieval_route="RETURN_INITIAL",
        )

    except ValueError as error:
        assert "text" in str(error)

    else:
        raise AssertionError(
            "Expected empty evidence text to fail closed"
        )


def test_scores_are_preserved_when_present():
    chunk = _chunk()

    chunk["similarity_score"] = 0.82
    chunk["rrf_score"] = 0.031

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RETURN_INITIAL",
    )

    assert evidence[
        "retrieval_scores"
    ] == {
        "similarity_score": 0.82,
        "rrf_score": 0.031,
    }


def test_scores_are_not_invented():
    chunk = _chunk()

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RETURN_INITIAL",
    )

    assert evidence[
        "retrieval_scores"
    ] == {}


def test_boolean_is_not_accepted_as_score():
    chunk = _chunk()

    chunk["similarity_score"] = True

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RETURN_INITIAL",
    )

    assert evidence[
        "retrieval_scores"
    ] == {}


def test_custom_evidence_role_is_preserved():
    chunk = _chunk()

    evidence = build_evidence_object(
        chunk,
        retrieval_route="RELATIONSHIP_AWARE",
        evidence_role="relationship_evidence",
    )

    assert evidence["evidence_role"] == (
        "relationship_evidence"
    )


def test_unsupported_evidence_role_fails():
    chunk = _chunk()

    try:
        build_evidence_object(
            chunk,
            retrieval_route="RETURN_INITIAL",
            evidence_role="invented_role",
        )

    except ValueError as error:
        assert "Unsupported evidence_role" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected unsupported role to fail"
        )


def test_build_multiple_evidence_objects():
    chunks = [
        _chunk(),
        {
            **_chunk(),
            "document_id": "DOC-002",
            "chunk_id": "DOC-002-V1.0-P001-C001",
            "title": "Winter Pressure Plan",
            "source_file": (
                "DOC-002_winter_pressure_plan.pdf"
            ),
        },
    ]

    evidence = build_evidence_objects(
        chunks,
        retrieval_route="HYBRID_RESCUE",
    )

    assert len(evidence) == 2

    assert evidence[0]["document_id"] == (
        "DOC-001"
    )

    assert evidence[1]["document_id"] == (
        "DOC-002"
    )

    assert all(
        item["retrieval_route"]
        == "HYBRID_RESCUE"
        for item in evidence
    )