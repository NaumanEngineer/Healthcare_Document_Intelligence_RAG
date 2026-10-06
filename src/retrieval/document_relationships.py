"""Explicit document-level relationship registry.

This module stores deterministic, source-backed relationships between
registered documents.

The registry exists to support relationship-aware retrieval.

It does NOT:
- infer relationships from semantic similarity;
- prove that a relationship is true;
- replace evidence-set relationship validation;
- override document lifecycle controls;
- make governance decisions.

Structured relationships may help retrieve related evidence, but the
existing governance layer remains responsible for establishing whether
a requested relationship is supported by the supplied Active evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.governance.evidence_set_relationship import (
    SUPPORTED_RELATIONSHIP_TYPES,
)
from src.ingestion.document_metadata import (
    get_document_metadata,
    is_document_registered,
    is_document_retrieval_eligible,
)


@dataclass(frozen=True)
class DocumentRelationship:
    """One explicit document-level relationship edge."""

    source_document_id: str
    relationship_type: str
    target_document_id: str
    evidence_document_id: str

    def __post_init__(self) -> None:
        source = _normalise_document_id(
            self.source_document_id,
            field_name="source_document_id",
        )

        target = _normalise_document_id(
            self.target_document_id,
            field_name="target_document_id",
        )

        evidence = _normalise_document_id(
            self.evidence_document_id,
            field_name="evidence_document_id",
        )

        relationship_type = (
            _normalise_relationship_type(
                self.relationship_type
            )
        )

        if source == target:
            raise ValueError(
                "relationship source and target "
                "must be different documents"
            )

        for document_id in (
            source,
            target,
            evidence,
        ):
            if not is_document_registered(
                document_id
            ):
                raise ValueError(
                    "relationship references "
                    "unregistered document_id: "
                    f"{document_id}"
                )

        object.__setattr__(
            self,
            "source_document_id",
            source,
        )

        object.__setattr__(
            self,
            "target_document_id",
            target,
        )

        object.__setattr__(
            self,
            "evidence_document_id",
            evidence,
        )

        object.__setattr__(
            self,
            "relationship_type",
            relationship_type,
        )

    def to_dict(self) -> dict:
        """Return a serialisable relationship record."""

        return {
            "source_document_id": (
                self.source_document_id
            ),
            "relationship_type": (
                self.relationship_type
            ),
            "target_document_id": (
                self.target_document_id
            ),
            "evidence_document_id": (
                self.evidence_document_id
            ),
        }


def _normalise_document_id(
    document_id: str,
    *,
    field_name: str,
) -> str:
    """Validate and normalise a document identifier."""

    if not isinstance(
        document_id,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string"
        )

    cleaned = (
        document_id
        .strip()
        .upper()
    )

    if not cleaned:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return cleaned


def _normalise_relationship_type(
    relationship_type: str,
) -> str:
    """Validate and normalise a relationship type."""

    if not isinstance(
        relationship_type,
        str,
    ):
        raise TypeError(
            "relationship_type must be a string"
        )

    cleaned = (
        relationship_type
        .strip()
        .upper()
    )

    if not cleaned:
        raise ValueError(
            "relationship_type must not be blank"
        )

    if (
        cleaned
        not in SUPPORTED_RELATIONSHIP_TYPES
    ):
        raise ValueError(
            "Unsupported relationship_type: "
            f"{cleaned}"
        )

    return cleaned


# ------------------------------------------------------------------
# EXPLICIT SOURCE-BACKED RELATIONSHIPS
# ------------------------------------------------------------------
#
# DOC-011 explicitly states that the Critical Staffing Contingency
# Procedure complements the Workforce Escalation Procedure.
#
# The edge is therefore stored as:
#
# DOC-011 --COMPLEMENTS--> DOC-003
#
# The registry helps retrieval locate the related document.
# The relationship itself must still be verified from Active evidence
# by the governance relationship validator.
# ------------------------------------------------------------------

DOCUMENT_RELATIONSHIPS: tuple[
    DocumentRelationship,
    ...,
] = (
    DocumentRelationship(
        source_document_id="DOC-011",
        relationship_type="COMPLEMENTS",
        target_document_id="DOC-003",
        evidence_document_id="DOC-011",
    ),
)


SYMMETRIC_RELATIONSHIP_TYPES = {
    "COMPLEMENTS",
    "CONFLICT",
}


def validate_relationship_registry(
    relationships: tuple[
        DocumentRelationship,
        ...,
    ] = DOCUMENT_RELATIONSHIPS,
) -> None:
    """Validate the complete relationship registry.

    Validation protects against:
    - invalid relationship objects;
    - duplicate directed edges;
    - unsupported relationship types;
    - unregistered documents;
    - self-relationships.

    Individual relationship construction already performs most of
    these checks. This function additionally protects against duplicate
    registry entries.
    """

    if not isinstance(
        relationships,
        tuple,
    ):
        raise TypeError(
            "relationships must be a tuple"
        )

    seen_edges: set[
        tuple[str, str, str]
    ] = set()

    for relationship in relationships:
        if not isinstance(
            relationship,
            DocumentRelationship,
        ):
            raise TypeError(
                "every registry item must be "
                "a DocumentRelationship"
            )

        edge = (
            relationship.source_document_id,
            relationship.relationship_type,
            relationship.target_document_id,
        )

        if edge in seen_edges:
            raise ValueError(
                "duplicate document relationship: "
                f"{edge}"
            )

        seen_edges.add(
            edge
        )


def list_document_relationships(
) -> list[dict]:
    """Return all configured relationships as dictionaries."""

    validate_relationship_registry()

    return [
        relationship.to_dict()
        for relationship
        in DOCUMENT_RELATIONSHIPS
    ]


def get_relationships_for_document(
    document_id: str,
    *,
    active_only: bool = True,
) -> list[dict]:
    """Return relationships relevant to one document.

    Directionality rules:

    COMPLEMENTS:
        traversable in both directions for retrieval.

    CONFLICT:
        traversable in both directions for retrieval.

    REPLACES:
        directional.

    TAKES_PRECEDENCE:
        directional.

    When ``active_only`` is True, both source and target documents must
    currently be retrieval eligible.

    This function returns relationship metadata only. It does not prove
    the relationship and does not retrieve chunks.
    """

    normalised_id = (
        _normalise_document_id(
            document_id,
            field_name="document_id",
        )
    )

    if not is_document_registered(
        normalised_id
    ):
        raise KeyError(
            "No registered document found for "
            f"{normalised_id!r}"
        )

    validate_relationship_registry()

    matches: list[dict] = []

    for relationship in DOCUMENT_RELATIONSHIPS:
        source = (
            relationship.source_document_id
        )

        target = (
            relationship.target_document_id
        )

        relationship_type = (
            relationship.relationship_type
        )

        if normalised_id == source:
            related_document_id = target
            direction = "OUTBOUND"

        elif (
            relationship_type
            in SYMMETRIC_RELATIONSHIP_TYPES
            and normalised_id == target
        ):
            related_document_id = source
            direction = "INBOUND_SYMMETRIC"

        else:
            continue

        if active_only:
            if not (
                is_document_retrieval_eligible(
                    source
                )
                and
                is_document_retrieval_eligible(
                    target
                )
            ):
                continue

        matches.append(
            {
                **relationship.to_dict(),
                "queried_document_id": (
                    normalised_id
                ),
                "related_document_id": (
                    related_document_id
                ),
                "retrieval_direction": (
                    direction
                ),
            }
        )

    return matches


def get_related_document_ids(
    document_id: str,
    *,
    relationship_type: str | None = None,
    active_only: bool = True,
) -> list[str]:
    """Return related document IDs for retrieval expansion."""

    relationships = (
        get_relationships_for_document(
            document_id,
            active_only=active_only,
        )
    )

    if relationship_type is not None:
        normalised_type = (
            _normalise_relationship_type(
                relationship_type
            )
        )

        relationships = [
            relationship
            for relationship
            in relationships
            if relationship[
                "relationship_type"
            ] == normalised_type
        ]

    related_ids = {
        relationship[
            "related_document_id"
        ]
        for relationship
        in relationships
    }

    return sorted(
        related_ids
    )


def get_relationship_evidence_document_ids(
    document_id: str,
    *,
    active_only: bool = True,
) -> list[str]:
    """Return documents containing relationship evidence.

    This is intentionally separate from related-document lookup.

    Example:

    DOC-011 COMPLEMENTS DOC-003

    The explicit relationship wording is currently stored in DOC-011,
    so DOC-011 is the evidence document.

    The returned IDs indicate where relationship evidence may be found;
    they do not establish the relationship by themselves.
    """

    relationships = (
        get_relationships_for_document(
            document_id,
            active_only=active_only,
        )
    )

    evidence_ids = {
        relationship[
            "evidence_document_id"
        ]
        for relationship
        in relationships
    }

    if active_only:
        evidence_ids = {
            document_id
            for document_id
            in evidence_ids
            if is_document_retrieval_eligible(
                document_id
            )
        }

    return sorted(
        evidence_ids
    )


# Validate the built-in registry at import time.
#
# A bad hard-coded edge should fail immediately during development
# rather than silently affecting retrieval behaviour later.
validate_relationship_registry()