"""Evidence provenance and traceability.

Week 22 Day 3.

This module converts structured evidence objects into compact,
validated provenance records.

Evidence metadata is checked against the canonical document register
where possible.

The provenance layer does not alter retrieval or governance decisions.
"""

from __future__ import annotations

from src.ingestion.document_metadata import (
    get_document_metadata,
    is_document_registered,
)


TRACEABILITY_VERIFIED = "VERIFIED"
TRACEABILITY_MISMATCH = "MISMATCH"
TRACEABILITY_UNREGISTERED = "UNREGISTERED"


CANONICAL_COMPARISON_FIELDS = (
    "title",
    "document_type",
    "source_type",
    "source_location",
    "source_file",
    "version",
    "effective_date",
    "status",
)


REQUIRED_EVIDENCE_PROVENANCE_FIELDS = (
    "evidence_id",
    "document_id",
    "chunk_id",
    "title",
    "document_type",
    "source_type",
    "source_location",
    "source_file",
    "version",
    "effective_date",
    "status",
    "page",
    "chunk_number",
    "ingestion_batch_id",
    "retrieval_route",
    "evidence_role",
)


def _require_string(
    value,
    field_name: str,
) -> str:
    """Require a non-empty string."""

    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


def _require_positive_integer(
    value,
    field_name: str,
) -> int:
    """Require a positive integer."""

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a positive integer"
        )

    return value


def _validate_required_fields(
    evidence: dict,
) -> None:
    """Fail closed when required provenance is absent."""

    missing = [
        field
        for field in REQUIRED_EVIDENCE_PROVENANCE_FIELDS
        if field not in evidence
    ]

    if missing:
        raise ValueError(
            "Evidence object is missing provenance fields: "
            + ", ".join(missing)
        )


def _canonical_metadata_check(
    evidence: dict,
) -> dict:
    """Compare evidence metadata with the canonical document register."""

    document_id = evidence[
        "document_id"
    ]

    if not is_document_registered(
        document_id
    ):
        return {
            "traceability_status": (
                TRACEABILITY_UNREGISTERED
            ),
            "canonical_document_registered": False,
            "canonical_metadata_match": False,
            "metadata_mismatches": [
                "document_id_not_registered"
            ],
        }

    canonical = get_document_metadata(
        document_id
    )

    mismatches = []

    for field in CANONICAL_COMPARISON_FIELDS:
        evidence_value = evidence.get(
            field
        )

        canonical_value = getattr(
            canonical,
            field,
        )

        if evidence_value != canonical_value:
            mismatches.append(
                field
            )

    return {
        "traceability_status": (
            TRACEABILITY_VERIFIED
            if not mismatches
            else TRACEABILITY_MISMATCH
        ),
        "canonical_document_registered": True,
        "canonical_metadata_match": (
            not mismatches
        ),
        "metadata_mismatches": mismatches,
    }


def build_provenance_record(
    evidence: dict,
) -> dict:
    """Build one validated provenance record."""

    if not isinstance(
        evidence,
        dict,
    ):
        raise TypeError(
            "evidence must be a dictionary"
        )

    _validate_required_fields(
        evidence
    )

    evidence_id = _require_string(
        evidence["evidence_id"],
        "evidence_id",
    )

    document_id = _require_string(
        evidence["document_id"],
        "document_id",
    )

    chunk_id = _require_string(
        evidence["chunk_id"],
        "chunk_id",
    )

    page = _require_positive_integer(
        evidence["page"],
        "page",
    )

    chunk_number = (
        _require_positive_integer(
            evidence["chunk_number"],
            "chunk_number",
        )
    )

    traceability = (
        _canonical_metadata_check(
            evidence
        )
    )

    return {
        "evidence_id": evidence_id,
        "document_id": document_id,
        "chunk_id": chunk_id,
        "source": {
            "title": _require_string(
                evidence["title"],
                "title",
            ),
            "document_type": _require_string(
                evidence["document_type"],
                "document_type",
            ),
            "source_type": _require_string(
                evidence["source_type"],
                "source_type",
            ),
            "source_location": _require_string(
                evidence["source_location"],
                "source_location",
            ),
            "source_file": _require_string(
                evidence["source_file"],
                "source_file",
            ),
        },
        "document_lifecycle": {
            "version": _require_string(
                evidence["version"],
                "version",
            ),
            "effective_date": _require_string(
                evidence["effective_date"],
                "effective_date",
            ),
            "status": _require_string(
                evidence["status"],
                "status",
            ),
        },
        "location": {
            "page": page,
            "chunk_number": chunk_number,
        },
        "lineage": {
            "ingestion_batch_id": (
                _require_string(
                    evidence[
                        "ingestion_batch_id"
                    ],
                    "ingestion_batch_id",
                )
            ),
            "retrieval_route": (
                _require_string(
                    evidence[
                        "retrieval_route"
                    ],
                    "retrieval_route",
                )
            ),
            "evidence_role": (
                _require_string(
                    evidence[
                        "evidence_role"
                    ],
                    "evidence_role",
                )
            ),
        },
        "traceability": traceability,
    }


def build_provenance_records(
    evidence_objects: list[dict],
) -> list[dict]:
    """Build provenance records for an evidence set."""

    if not isinstance(
        evidence_objects,
        list,
    ):
        raise TypeError(
            "evidence_objects must be a list"
        )

    return [
        build_provenance_record(
            evidence
        )
        for evidence in evidence_objects
    ]