"""Week 26 version and temporal assurance.

This module evaluates evidence version relationships and temporal validity.

It complements, rather than replaces, existing lifecycle protection.

Core principles:

- recency is not the same as authority;
- superseded evidence may be historically valid but cannot automatically
  support a current operational claim;
- future-effective evidence is not current;
- unknown temporal state must fail closed;
- explicit replacement relationships are stronger than date comparison alone.
"""

from __future__ import annotations

from datetime import date
from typing import Any


TEMPORALLY_VALID = "TEMPORALLY_VALID"
TEMPORALLY_HISTORICAL = "TEMPORALLY_HISTORICAL"
TEMPORALLY_EXPIRED = "TEMPORALLY_EXPIRED"
FUTURE_EFFECTIVE = "FUTURE_EFFECTIVE"
TEMPORALLY_UNKNOWN = "TEMPORALLY_UNKNOWN"


CURRENT_VERSION = "CURRENT_VERSION"
PREVIOUS_VERSION = "PREVIOUS_VERSION"
EXPLICIT_REPLACEMENT = "EXPLICIT_REPLACEMENT"
POSSIBLE_REPLACEMENT = "POSSIBLE_REPLACEMENT"
PARALLEL_ACTIVE = "PARALLEL_ACTIVE"
HISTORICAL_ONLY = "HISTORICAL_ONLY"
VERSION_RELATIONSHIP_UNKNOWN = "VERSION_RELATIONSHIP_UNKNOWN"


SAFE_FOR_CURRENT_USE = "SAFE_FOR_CURRENT_USE"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
NOT_SAFE_FOR_CURRENT_USE = "NOT_SAFE_FOR_CURRENT_USE"


def _parse_date(
    value: Any,
) -> date | None:
    """Parse YYYY-MM-DD values conservatively."""

    if value in {
        None,
        "",
    }:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            "Date values must be strings or None."
        )

    try:
        return date.fromisoformat(
            value
        )

    except ValueError as exc:
        raise ValueError(
            f"Invalid ISO date: {value}"
        ) from exc


def _normalise_status(
    value: Any,
) -> str:
    """Normalise lifecycle status."""

    if not isinstance(
        value,
        str,
    ):
        return ""

    return value.strip().lower()


def assess_temporal_validity(
    evidence: dict[str, Any],
    *,
    query_date: str,
) -> dict[str, Any]:
    """Assess whether evidence is temporally valid for the query date."""

    query = _parse_date(
        query_date
    )

    if query is None:
        raise ValueError(
            "query_date is required."
        )

    effective = _parse_date(
        evidence.get(
            "effective_date"
        )
    )

    superseded = _parse_date(
        evidence.get(
            "superseded_date"
        )
    )

    status = _normalise_status(
        evidence.get(
            "status"
        )
    )

    if effective is None:
        temporal_state = (
            TEMPORALLY_UNKNOWN
        )

        reason = (
            "Evidence has no usable effective date."
        )

    elif effective > query:
        temporal_state = (
            FUTURE_EFFECTIVE
        )

        reason = (
            "Evidence becomes effective after the query date."
        )

    elif (
        superseded is not None
        and superseded <= query
    ):
        temporal_state = (
            TEMPORALLY_EXPIRED
        )

        reason = (
            "Evidence was superseded on or before the query date."
        )

    elif status in {
        "superseded",
        "archived",
    }:
        temporal_state = (
            TEMPORALLY_HISTORICAL
        )

        reason = (
            "Evidence is historical rather than current."
        )

    elif status == "active":
        temporal_state = (
            TEMPORALLY_VALID
        )

        reason = (
            "Evidence is active and effective on the query date."
        )

    else:
        temporal_state = (
            TEMPORALLY_UNKNOWN
        )

        reason = (
            "Evidence temporal state cannot be established safely."
        )

    return {
        "evidence_id": evidence.get(
            "evidence_id"
        ),
        "temporal_state": (
            temporal_state
        ),
        "query_date": query.isoformat(),
        "effective_date": (
            effective.isoformat()
            if effective is not None
            else None
        ),
        "superseded_date": (
            superseded.isoformat()
            if superseded is not None
            else None
        ),
        "status": status,
        "reason": reason,
    }


def assess_version_relationship(
    older: dict[str, Any],
    newer: dict[str, Any],
) -> dict[str, Any]:
    """Assess explicit version relationship between two evidence items."""

    older_document_id = older.get(
        "document_id"
    )

    newer_document_id = newer.get(
        "document_id"
    )

    older_replaced_by = older.get(
        "replaced_by_document_id"
    )

    newer_replaces = newer.get(
        "replaces_document_id"
    )

    older_status = _normalise_status(
        older.get(
            "status"
        )
    )

    newer_status = _normalise_status(
        newer.get(
            "status"
        )
    )

    if (
        older_replaced_by
        and older_replaced_by
        == newer_document_id
    ) or (
        newer_replaces
        and newer_replaces
        == older_document_id
    ):
        relationship = (
            EXPLICIT_REPLACEMENT
        )

        reason = (
            "Explicit replacement metadata links "
            "the two document versions."
        )

    elif (
        older_document_id
        == newer_document_id
        and older.get(
            "version"
        )
        != newer.get(
            "version"
        )
    ):
        relationship = (
            POSSIBLE_REPLACEMENT
        )

        reason = (
            "Same document identity has different version metadata."
        )

    elif (
        older_status == "active"
        and newer_status == "active"
    ):
        relationship = (
            PARALLEL_ACTIVE
        )

        reason = (
            "Both evidence items are active and no replacement "
            "relationship is explicit."
        )

    elif older_status in {
        "superseded",
        "archived",
    }:
        relationship = (
            PREVIOUS_VERSION
        )

        reason = (
            "Older evidence has historical lifecycle status."
        )

    else:
        relationship = (
            VERSION_RELATIONSHIP_UNKNOWN
        )

        reason = (
            "Version relationship cannot be established safely."
        )

    return {
        "older_evidence_id": older.get(
            "evidence_id"
        ),
        "newer_evidence_id": newer.get(
            "evidence_id"
        ),
        "relationship": (
            relationship
        ),
        "reason": reason,
    }


def assess_version_temporal_assurance(
    *,
    evidence_items: list[dict[str, Any]],
    query_date: str,
) -> dict[str, Any]:
    """Assess evidence set for current operational use."""

    if not isinstance(
        evidence_items,
        list,
    ):
        raise TypeError(
            "evidence_items must be a list."
        )

    if not evidence_items:
        return {
            "decision": (
                NOT_SAFE_FOR_CURRENT_USE
            ),
            "temporal_results": [],
            "version_results": [],
            "current_evidence_ids": [],
            "historical_evidence_ids": [],
            "reason": (
                "No evidence was supplied."
            ),
        }

    temporal_results = [
        assess_temporal_validity(
            evidence,
            query_date=query_date,
        )
        for evidence
        in evidence_items
    ]

    current_ids = [
        result[
            "evidence_id"
        ]
        for result
        in temporal_results
        if result[
            "temporal_state"
        ]
        == TEMPORALLY_VALID
    ]

    historical_ids = [
        result[
            "evidence_id"
        ]
        for result
        in temporal_results
        if result[
            "temporal_state"
        ]
        in {
            TEMPORALLY_HISTORICAL,
            TEMPORALLY_EXPIRED,
        }
    ]

    unsafe_temporal = [
        result
        for result
        in temporal_results
        if result[
            "temporal_state"
        ]
        in {
            TEMPORALLY_EXPIRED,
            FUTURE_EFFECTIVE,
            TEMPORALLY_UNKNOWN,
        }
    ]

    version_results = []

    for index, older in enumerate(
        evidence_items
    ):
        for newer in evidence_items[
            index + 1:
        ]:
            version_results.append(
                assess_version_relationship(
                    older,
                    newer,
                )
            )

    explicit_replacement = any(
        result[
            "relationship"
        ]
        == EXPLICIT_REPLACEMENT
        for result
        in version_results
    )

    if unsafe_temporal:
        decision = (
            NOT_SAFE_FOR_CURRENT_USE
        )

        reason = (
            "At least one evidence item is expired, "
            "future-effective or temporally unknown."
        )

    elif (
        historical_ids
        and current_ids
    ):
        decision = (
            REVIEW_REQUIRED
        )

        reason = (
            "Historical and current evidence are both present."
        )

    elif explicit_replacement:
        decision = (
            REVIEW_REQUIRED
        )

        reason = (
            "Explicit version succession requires current-version "
            "selection before operational use."
        )

    elif current_ids:
        decision = (
            SAFE_FOR_CURRENT_USE
        )

        reason = (
            "All relevant evidence is temporally valid "
            "for the query date."
        )

    else:
        decision = (
            REVIEW_REQUIRED
        )

        reason = (
            "Current authoritative evidence could not be "
            "established safely."
        )

    return {
        "decision": decision,
        "temporal_results": (
            temporal_results
        ),
        "version_results": (
            version_results
        ),
        "current_evidence_ids": (
            current_ids
        ),
        "historical_evidence_ids": (
            historical_ids
        ),
        "explicit_replacement_detected": (
            explicit_replacement
        ),
        "reason": reason,
    }