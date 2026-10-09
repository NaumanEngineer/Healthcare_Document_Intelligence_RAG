from src.evidence.evidence_packet import (
    _build_provenance_summary,
)
from src.evidence.provenance import (
    TRACEABILITY_MISMATCH,
    TRACEABILITY_UNREGISTERED,
    TRACEABILITY_VERIFIED,
)


def _record(
    evidence_id: str,
    status: str,
) -> dict:
    return {
        "evidence_id": evidence_id,
        "traceability": {
            "traceability_status": status,
        },
    }


def test_all_verified_summary():
    records = [
        _record(
            "EVIDENCE::A",
            TRACEABILITY_VERIFIED,
        ),
        _record(
            "EVIDENCE::B",
            TRACEABILITY_VERIFIED,
        ),
        _record(
            "EVIDENCE::C",
            TRACEABILITY_VERIFIED,
        ),
    ]

    summary = _build_provenance_summary(
        records
    )

    assert summary[
        "record_count"
    ] == 3

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_VERIFIED
    ] == 3

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_MISMATCH
    ] == 0

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_UNREGISTERED
    ] == 0

    assert summary[
        "all_verified"
    ] is True

    assert summary[
        "mismatch_evidence_ids"
    ] == []

    assert summary[
        "unregistered_evidence_ids"
    ] == []


def test_mismatch_is_visible_in_summary():
    records = [
        _record(
            "EVIDENCE::A",
            TRACEABILITY_VERIFIED,
        ),
        _record(
            "EVIDENCE::B",
            TRACEABILITY_MISMATCH,
        ),
    ]

    summary = _build_provenance_summary(
        records
    )

    assert summary[
        "record_count"
    ] == 2

    assert summary[
        "all_verified"
    ] is False

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_MISMATCH
    ] == 1

    assert summary[
        "mismatch_evidence_ids"
    ] == [
        "EVIDENCE::B",
    ]


def test_unregistered_is_visible_in_summary():
    records = [
        _record(
            "EVIDENCE::A",
            TRACEABILITY_UNREGISTERED,
        ),
    ]

    summary = _build_provenance_summary(
        records
    )

    assert summary[
        "record_count"
    ] == 1

    assert summary[
        "all_verified"
    ] is False

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_UNREGISTERED
    ] == 1

    assert summary[
        "unregistered_evidence_ids"
    ] == [
        "EVIDENCE::A",
    ]


def test_empty_provenance_is_not_all_verified():
    summary = _build_provenance_summary(
        []
    )

    assert summary[
        "record_count"
    ] == 0

    assert summary[
        "all_verified"
    ] is False

    assert summary[
        "status_counts"
    ][
        TRACEABILITY_VERIFIED
    ] == 0


def test_unknown_traceability_status_fails_closed():
    records = [
        _record(
            "EVIDENCE::A",
            "UNKNOWN_STATUS",
        ),
    ]

    try:
        _build_provenance_summary(
            records
        )

    except ValueError as error:
        assert (
            "Unsupported traceability status"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected unknown status to fail"
        )