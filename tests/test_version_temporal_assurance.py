"""Tests for Week 26 version and temporal assurance."""

from __future__ import annotations

from src.evaluation.version_temporal_assurance import (
    EXPLICIT_REPLACEMENT,
    FUTURE_EFFECTIVE,
    NOT_SAFE_FOR_CURRENT_USE,
    REVIEW_REQUIRED,
    SAFE_FOR_CURRENT_USE,
    TEMPORALLY_EXPIRED,
    TEMPORALLY_VALID,
    assess_temporal_validity,
    assess_version_relationship,
    assess_version_temporal_assurance,
)


def _evidence(
    *,
    evidence_id: str,
    document_id: str,
    status: str,
    effective_date: str,
    superseded_date=None,
    replaces_document_id=None,
    replaced_by_document_id=None,
    version="1",
):
    return {
        "evidence_id": evidence_id,
        "document_id": document_id,
        "status": status,
        "effective_date": effective_date,
        "superseded_date": superseded_date,
        "replaces_document_id": replaces_document_id,
        "replaced_by_document_id": replaced_by_document_id,
        "version": version,
    }


def test_active_effective_evidence_is_temporally_valid():
    evidence = _evidence(
        evidence_id="E1",
        document_id="DOC-1",
        status="active",
        effective_date="2026-01-01",
    )

    result = assess_temporal_validity(
        evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "temporal_state"
        ]
        == TEMPORALLY_VALID
    )


def test_future_evidence_is_not_current():
    evidence = _evidence(
        evidence_id="E1",
        document_id="DOC-1",
        status="active",
        effective_date="2026-06-01",
    )

    result = assess_temporal_validity(
        evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "temporal_state"
        ]
        == FUTURE_EFFECTIVE
    )


def test_superseded_date_before_query_is_expired():
    evidence = _evidence(
        evidence_id="E1",
        document_id="DOC-1",
        status="superseded",
        effective_date="2025-01-01",
        superseded_date="2026-03-01",
    )

    result = assess_temporal_validity(
        evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "temporal_state"
        ]
        == TEMPORALLY_EXPIRED
    )


def test_explicit_replacement_relationship_is_detected():
    old = _evidence(
        evidence_id="E1",
        document_id="DOC-OLD",
        status="superseded",
        effective_date="2025-01-01",
        replaced_by_document_id="DOC-NEW",
    )

    new = _evidence(
        evidence_id="E2",
        document_id="DOC-NEW",
        status="active",
        effective_date="2026-01-01",
        replaces_document_id="DOC-OLD",
    )

    result = assess_version_relationship(
        old,
        new,
    )

    assert (
        result[
            "relationship"
        ]
        == EXPLICIT_REPLACEMENT
    )


def test_current_evidence_set_can_be_safe():
    evidence = [
        _evidence(
            evidence_id="E1",
            document_id="DOC-1",
            status="active",
            effective_date="2026-01-01",
        )
    ]

    result = assess_version_temporal_assurance(
        evidence_items=evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "decision"
        ]
        == SAFE_FOR_CURRENT_USE
    )


def test_expired_evidence_set_is_not_safe():
    evidence = [
        _evidence(
            evidence_id="E1",
            document_id="DOC-1",
            status="superseded",
            effective_date="2025-01-01",
            superseded_date="2026-01-01",
        )
    ]

    result = assess_version_temporal_assurance(
        evidence_items=evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "decision"
        ]
        == NOT_SAFE_FOR_CURRENT_USE
    )


def test_mixed_current_and_historical_requires_review():
    evidence = [
        _evidence(
            evidence_id="E1",
            document_id="DOC-OLD",
            status="superseded",
            effective_date="2025-01-01",
        ),
        _evidence(
            evidence_id="E2",
            document_id="DOC-NEW",
            status="active",
            effective_date="2026-01-01",
        ),
    ]

    result = assess_version_temporal_assurance(
        evidence_items=evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "decision"
        ]
        == REVIEW_REQUIRED
    )


def test_version_temporal_layer_never_treats_expired_as_safe():
    evidence = [
        _evidence(
            evidence_id="E1",
            document_id="DOC-OLD",
            status="superseded",
            effective_date="2025-01-01",
            superseded_date="2026-03-01",
        ),
        _evidence(
            evidence_id="E2",
            document_id="DOC-NEW",
            status="active",
            effective_date="2026-03-01",
        ),
    ]

    result = assess_version_temporal_assurance(
        evidence_items=evidence,
        query_date="2026-04-15",
    )

    assert (
        result[
            "decision"
        ]
        != SAFE_FOR_CURRENT_USE
    )