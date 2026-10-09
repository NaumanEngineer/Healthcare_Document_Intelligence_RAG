from src.evidence.provenance import (
    TRACEABILITY_MISMATCH,
    TRACEABILITY_UNREGISTERED,
    TRACEABILITY_VERIFIED,
    build_provenance_record,
    build_provenance_records,
)


def _evidence(
    *,
    document_id="DOC-008",
    title="Ambulance Handover Escalation Guidance",
    document_type="Operational Guidance",
    source_type="Synthetic",
    source_location=(
        "data/raw/"
        "DOC-008_ambulance_handover_"
        "escalation_guidance.pdf"
    ),
    source_file=(
        "DOC-008_ambulance_handover_"
        "escalation_guidance.pdf"
    ),
    version="1.0",
    effective_date="2026-01-01",
    status="Active",
):
    return {
        "evidence_id": (
            "EVIDENCE::DOC-008-V1.0-P001-C001"
        ),
        "document_id": document_id,
        "chunk_id": "DOC-008-V1.0-P001-C001",
        "title": title,
        "document_type": document_type,
        "source_type": source_type,
        "source_location": source_location,
        "source_file": source_file,
        "version": version,
        "effective_date": effective_date,
        "status": status,
        "page": 1,
        "chunk_number": 1,
        "ingestion_batch_id": "batch-008",
        "retrieval_route": "RETURN_INITIAL",
        "evidence_role": "supporting",
    }


def test_registered_matching_evidence_is_verified():
    record = build_provenance_record(
        _evidence()
    )

    assert record[
        "traceability"
    ][
        "traceability_status"
    ] == TRACEABILITY_VERIFIED

    assert record[
        "traceability"
    ][
        "canonical_document_registered"
    ] is True

    assert record[
        "traceability"
    ][
        "canonical_metadata_match"
    ] is True

    assert record[
        "traceability"
    ][
        "metadata_mismatches"
    ] == []


def test_version_mismatch_is_detected():
    record = build_provenance_record(
        _evidence(
            version="9.9",
        )
    )

    assert record[
        "traceability"
    ][
        "traceability_status"
    ] == TRACEABILITY_MISMATCH

    assert "version" in record[
        "traceability"
    ][
        "metadata_mismatches"
    ]


def test_status_mismatch_is_detected():
    record = build_provenance_record(
        _evidence(
            status="Draft",
        )
    )

    assert record[
        "traceability"
    ][
        "traceability_status"
    ] == TRACEABILITY_MISMATCH

    assert "status" in record[
        "traceability"
    ][
        "metadata_mismatches"
    ]


def test_source_file_mismatch_is_detected():
    record = build_provenance_record(
        _evidence(
            source_file="wrong_file.pdf",
        )
    )

    assert record[
        "traceability"
    ][
        "traceability_status"
    ] == TRACEABILITY_MISMATCH

    assert "source_file" in record[
        "traceability"
    ][
        "metadata_mismatches"
    ]


def test_unregistered_document_is_reported():
    record = build_provenance_record(
        _evidence(
            document_id="DOC-999",
        )
    )

    assert record[
        "traceability"
    ][
        "traceability_status"
    ] == TRACEABILITY_UNREGISTERED

    assert record[
        "traceability"
    ][
        "canonical_document_registered"
    ] is False

    assert record[
        "traceability"
    ][
        "canonical_metadata_match"
    ] is False


def test_page_and_chunk_location_are_preserved():
    evidence = _evidence()

    evidence["page"] = 2
    evidence["chunk_number"] = 3

    record = build_provenance_record(
        evidence
    )

    assert record["location"] == {
        "page": 2,
        "chunk_number": 3,
    }


def test_ingestion_and_retrieval_lineage_are_preserved():
    record = build_provenance_record(
        _evidence()
    )

    assert record[
        "lineage"
    ][
        "ingestion_batch_id"
    ] == "batch-008"

    assert record[
        "lineage"
    ][
        "retrieval_route"
    ] == "RETURN_INITIAL"

    assert record[
        "lineage"
    ][
        "evidence_role"
    ] == "supporting"


def test_missing_required_provenance_fails_closed():
    evidence = _evidence()

    del evidence[
        "ingestion_batch_id"
    ]

    try:
        build_provenance_record(
            evidence
        )

    except ValueError as error:
        assert "ingestion_batch_id" in str(
            error
        )

    else:
        raise AssertionError(
            "Expected missing provenance to fail"
        )


def test_invalid_page_fails_closed():
    evidence = _evidence()

    evidence["page"] = 0

    try:
        build_provenance_record(
            evidence
        )

    except ValueError as error:
        assert "page" in str(error)

    else:
        raise AssertionError(
            "Expected invalid page to fail"
        )


def test_multiple_provenance_records_are_built():
    evidence_objects = [
        _evidence(),
        {
            **_evidence(),
            "evidence_id": (
                "EVIDENCE::DOC-009-V1.0-P002-C001"
            ),
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-V1.0-P002-C001",
            "title": "Severe Weather Operational Plan",
            "document_type": "Operational Plan",
            "source_location": (
                "data/raw/"
                "DOC-009_severe_weather_operational_plan.pdf"
            ),
            "source_file": (
                "DOC-009_severe_weather_operational_plan.pdf"
            ),
            "ingestion_batch_id": "batch-009",
        },
    ]

    records = build_provenance_records(
        evidence_objects
    )

    assert len(records) == 2

    assert records[0][
        "document_id"
    ] == "DOC-008"

    assert records[1][
        "document_id"
    ] == "DOC-009"

    assert all(
        record[
            "traceability"
        ][
            "traceability_status"
        ]
        == TRACEABILITY_VERIFIED
        for record in records
    )