"""Tests for Week 26 fail-closed assurance boundary."""

from __future__ import annotations

from src.evaluation.week26_fail_closed_assurance import (
    FAIL_CLOSED,
    NORMAL_ASSURANCE,
    safe_audit_collection,
    safe_audit_system_safety,
)


def _valid_record():
    return {
        "case_id": "W26-ROBUST-001",
        "upstream_decision": "PASS",
        "final_decision": "REVIEW_REQUIRED",
        "signals": {
            "prompt_injection_detected": True,
        },
    }


def test_valid_record_uses_normal_assurance():
    result = safe_audit_system_safety(
        _valid_record()
    )

    assert (
        result[
            "boundary_status"
        ]
        == NORMAL_ASSURANCE
    )

    assert result[
        "assurance_completed"
    ] is True

    assert result[
        "final_decision"
    ] == "REVIEW_REQUIRED"


def test_non_dictionary_record_fails_closed():
    result = safe_audit_system_safety(
        "not-a-record"
    )

    assert (
        result[
            "boundary_status"
        ]
        == FAIL_CLOSED
    )

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_missing_case_id_fails_closed():
    record = _valid_record()

    del record[
        "case_id"
    ]

    result = safe_audit_system_safety(
        record
    )

    assert (
        result[
            "boundary_status"
        ]
        == FAIL_CLOSED
    )

    assert result[
        "error_type"
    ] == "INVALID_CASE_ID"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_missing_upstream_decision_fails_closed():
    record = _valid_record()

    del record[
        "upstream_decision"
    ]

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "error_type"
    ] == "MISSING_UPSTREAM_DECISION"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_missing_final_decision_fails_closed():
    record = _valid_record()

    del record[
        "final_decision"
    ]

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "error_type"
    ] == "MISSING_FINAL_DECISION"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_missing_signals_fail_closed():
    record = _valid_record()

    del record[
        "signals"
    ]

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "error_type"
    ] == "MISSING_SIGNALS"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_unknown_upstream_decision_fails_closed():
    record = _valid_record()

    record[
        "upstream_decision"
    ] = "AUTO_MAGIC"

    result = safe_audit_system_safety(
        record
    )

    assert (
        result[
            "boundary_status"
        ]
        == FAIL_CLOSED
    )

    assert result[
        "error_type"
    ] == "UNKNOWN_UPSTREAM_DECISION"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_unknown_final_decision_fails_closed():
    record = _valid_record()

    record[
        "final_decision"
    ] = "SAFE_ENOUGH"

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "error_type"
    ] == "UNKNOWN_FINAL_DECISION"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_malformed_signals_fail_closed():
    record = _valid_record()

    record[
        "signals"
    ] = [
        "prompt_injection_detected"
    ]

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "error_type"
    ] == "INVALID_SIGNALS_TYPE"

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_fail_closed_result_never_claims_authority_increase():
    record = _valid_record()

    record[
        "upstream_decision"
    ] = None

    result = safe_audit_system_safety(
        record
    )

    assert result[
        "authority_increased"
    ] is False

    assert result[
        "final_decision"
    ] == "ABSTAIN"


def test_collection_preserves_valid_and_invalid_records():
    valid = _valid_record()

    invalid = {
        "case_id": "W26-ROBUST-002",
        "upstream_decision": "UNKNOWN",
        "final_decision": "PASS",
        "signals": {},
    }

    report = safe_audit_collection(
        [
            valid,
            invalid,
        ]
    )

    assert report[
        "record_count"
    ] == 2

    assert report[
        "normal_assurance_count"
    ] == 1

    assert report[
        "fail_closed_count"
    ] == 1

    assert report[
        "abstain_decision_count"
    ] == 1


def test_invalid_collection_type_fails_closed():
    report = safe_audit_collection(
        {
            "not": "a list"
        }
    )

    assert report[
        "overall_status"
    ] == FAIL_CLOSED

    assert report[
        "fail_closed_count"
    ] == 1

    assert report[
        "abstain_decision_count"
    ] == 1


def test_clean_collection_has_normal_status():
    report = safe_audit_collection(
        [
            _valid_record()
        ]
    )

    assert (
        report[
            "overall_status"
        ]
        == NORMAL_ASSURANCE
    )

    assert report[
        "fail_closed_count"
    ] == 0