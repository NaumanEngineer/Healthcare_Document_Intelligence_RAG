"""Evidence conflict, supersession and precedence assessment.

Week 22 Day 4.

This module performs conservative deterministic checks over a structured
evidence set.

It does not infer contradictions from semantic similarity.

Its responsibilities are limited to:

- lifecycle-risk detection;
- explicit relationship validation;
- safe-combination assessment;
- preservation of human-review requirements.

Existing governance remains authoritative.
"""

from __future__ import annotations

from itertools import combinations

from src.governance.evidence_set_relationship import (
    RELATIONSHIP_NOT_ESTABLISHED,
    RELATIONSHIP_SUPPORTED,
    REVIEW_REQUIRED,
    validate_evidence_set_relationship,
)


SAFE_TO_COMBINE = "SAFE_TO_COMBINE"
REVIEW_BEFORE_COMBINATION = "REVIEW_BEFORE_COMBINATION"
BLOCK_COMBINATION = "BLOCK_COMBINATION"


RISKY_LIFECYCLE_STATUSES = {
    "Draft",
    "Superseded",
    "Archived",
}


RELATIONSHIP_TYPES_TO_CHECK = (
    "CONFLICT",
    "REPLACES",
    "TAKES_PRECEDENCE",
)


def _validate_evidence_objects(
    evidence_objects: list[dict],
) -> None:
    """Validate the basic evidence-set contract."""

    if not isinstance(
        evidence_objects,
        list,
    ):
        raise TypeError(
            "evidence_objects must be a list"
        )

    for evidence in evidence_objects:
        if not isinstance(
            evidence,
            dict,
        ):
            raise TypeError(
                "each evidence item must be a dictionary"
            )

        for field in (
            "document_id",
            "status",
            "evidence_text",
        ):
            value = evidence.get(
                field
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"{field} must be a non-empty string"
                )


def _document_status_summary(
    evidence_objects: list[dict],
) -> dict:
    """Summarize lifecycle states by document."""

    document_statuses: dict[
        str,
        set[str],
    ] = {}

    for evidence in evidence_objects:
        document_id = evidence[
            "document_id"
        ]

        status = evidence[
            "status"
        ]

        document_statuses.setdefault(
            document_id,
            set(),
        ).add(
            status
        )

    risky_documents = sorted(
        document_id
        for document_id, statuses
        in document_statuses.items()
        if statuses
        & RISKY_LIFECYCLE_STATUSES
    )

    mixed_status_documents = sorted(
        document_id
        for document_id, statuses
        in document_statuses.items()
        if len(statuses) > 1
    )

    return {
        "document_statuses": {
            document_id: sorted(
                statuses
            )
            for document_id, statuses
            in sorted(
                document_statuses.items()
            )
        },
        "risky_documents": (
            risky_documents
        ),
        "mixed_status_documents": (
            mixed_status_documents
        ),
    }


def _distinct_document_ids(
    evidence_objects: list[dict],
) -> list[str]:
    """Return unique document IDs in first-seen order."""

    document_ids = []

    seen = set()

    for evidence in evidence_objects:
        document_id = evidence[
            "document_id"
        ]

        if document_id not in seen:
            seen.add(
                document_id
            )

            document_ids.append(
                document_id
            )

    return document_ids


def _to_relationship_evidence_item(
    evidence: dict,
) -> dict:
    """Adapt a Day 1 Evidence Object to the Week 21 validator contract.

    Structured Evidence Objects use `evidence_text`.

    The existing deterministic relationship validator operates on
    retrieval-style evidence where the source content is held in
    `text`.

    This adapter preserves the original Evidence Object and adds the
    legacy-compatible `text` field without changing the evidence
    content or relationship meaning.
    """

    return {
        **evidence,
        "text": evidence[
            "evidence_text"
        ],
    }


def _pair_evidence(
    evidence_objects: list[dict],
    first_document_id: str,
    second_document_id: str,
) -> list[dict]:
    """Return validator-compatible evidence for one document pair."""

    return [
        _to_relationship_evidence_item(
            evidence
        )
        for evidence in evidence_objects
        if evidence[
            "document_id"
        ]
        in {
            first_document_id,
            second_document_id,
        }
    ]


def _check_relationships(
    evidence_objects: list[dict],
) -> list[dict]:
    """Check explicit high-risk relationships for document pairs."""

    document_ids = (
        _distinct_document_ids(
            evidence_objects
        )
    )

    results = []

    for (
        first_document_id,
        second_document_id,
    ) in combinations(
        document_ids,
        2,
    ):
        pair = _pair_evidence(
            evidence_objects,
            first_document_id,
            second_document_id,
        )

        for relationship_type in (
            RELATIONSHIP_TYPES_TO_CHECK
        ):
            assessment = (
                validate_evidence_set_relationship(
                    relationship_type,
                    pair,
                )
            )

            results.append(
                {
                    "document_ids": [
                        first_document_id,
                        second_document_id,
                    ],
                    "relationship_type": (
                        relationship_type
                    ),
                    "decision": assessment.get(
                        "decision"
                    ),
                    "evidence_status": (
                        assessment.get(
                            "evidence_status"
                        )
                    ),
                    "matched_relationship_terms": (
                        assessment.get(
                            "matched_relationship_terms",
                            [],
                        )
                    ),
                    "reason": assessment.get(
                        "reason"
                    ),
                }
            )

    return results


def assess_evidence_precedence(
    evidence_objects: list[dict],
) -> dict:
    """Assess whether an evidence set may be safely combined.

    Decision hierarchy:

    1. Lifecycle-risk evidence requires review.
    2. Explicit CONFLICT blocks automatic combination.
    3. Explicit REPLACES or TAKES_PRECEDENCE requires review so the
       correct authority can be selected.
    4. Ambiguous relationship validation requires review.
    5. Otherwise the evidence set is safe to combine at this layer.

    SAFE_TO_COMBINE does not mean the system may answer.
    Downstream governance remains authoritative.
    """

    _validate_evidence_objects(
        evidence_objects
    )

    lifecycle = (
        _document_status_summary(
            evidence_objects
        )
    )

    document_ids = (
        _distinct_document_ids(
            evidence_objects
        )
    )

    if not evidence_objects:
        return {
            "decision": (
                REVIEW_BEFORE_COMBINATION
            ),
            "document_ids": [],
            "lifecycle": lifecycle,
            "relationship_checks": [],
            "blocking_relationships": [],
            "review_relationships": [],
            "reason": (
                "No evidence is available for "
                "combination assessment."
            ),
        }

    if lifecycle[
        "risky_documents"
    ]:
        return {
            "decision": (
                REVIEW_BEFORE_COMBINATION
            ),
            "document_ids": document_ids,
            "lifecycle": lifecycle,
            "relationship_checks": [],
            "blocking_relationships": [],
            "review_relationships": [],
            "reason": (
                "The evidence set contains Draft, "
                "Superseded or Archived material."
            ),
        }

    if lifecycle[
        "mixed_status_documents"
    ]:
        return {
            "decision": (
                REVIEW_BEFORE_COMBINATION
            ),
            "document_ids": document_ids,
            "lifecycle": lifecycle,
            "relationship_checks": [],
            "blocking_relationships": [],
            "review_relationships": [],
            "reason": (
                "At least one document appears with "
                "multiple lifecycle states."
            ),
        }

    if len(
        document_ids
    ) < 2:
        return {
            "decision": SAFE_TO_COMBINE,
            "document_ids": document_ids,
            "lifecycle": lifecycle,
            "relationship_checks": [],
            "blocking_relationships": [],
            "review_relationships": [],
            "reason": (
                "Only one distinct Active document is "
                "present; cross-document precedence "
                "assessment is not required."
            ),
        }

    relationship_checks = (
        _check_relationships(
            evidence_objects
        )
    )

    blocking_relationships = [
        item
        for item in relationship_checks
        if (
            item[
                "relationship_type"
            ]
            == "CONFLICT"
            and item[
                "decision"
            ]
            == RELATIONSHIP_SUPPORTED
        )
    ]

    if blocking_relationships:
        return {
            "decision": BLOCK_COMBINATION,
            "document_ids": document_ids,
            "lifecycle": lifecycle,
            "relationship_checks": (
                relationship_checks
            ),
            "blocking_relationships": (
                blocking_relationships
            ),
            "review_relationships": [],
            "reason": (
                "An explicit conflict relationship is "
                "supported by the supplied Active evidence."
            ),
        }

    review_relationships = [
        item
        for item in relationship_checks
        if (
            item[
                "relationship_type"
            ]
            in {
                "REPLACES",
                "TAKES_PRECEDENCE",
            }
            and item[
                "decision"
            ]
            == RELATIONSHIP_SUPPORTED
        )
    ]

    ambiguous_relationships = [
        item
        for item in relationship_checks
        if item[
            "decision"
        ]
        == REVIEW_REQUIRED
    ]

    if (
        review_relationships
        or ambiguous_relationships
    ):
        return {
            "decision": (
                REVIEW_BEFORE_COMBINATION
            ),
            "document_ids": document_ids,
            "lifecycle": lifecycle,
            "relationship_checks": (
                relationship_checks
            ),
            "blocking_relationships": [],
            "review_relationships": (
                review_relationships
                + ambiguous_relationships
            ),
            "reason": (
                "The evidence set contains an explicit "
                "precedence/replacement relationship or "
                "an ambiguous relationship assessment "
                "that requires human review."
            ),
        }

    unsupported_relationships = [
        item
        for item in relationship_checks
        if item[
            "decision"
        ]
        == RELATIONSHIP_NOT_ESTABLISHED
    ]

    return {
        "decision": SAFE_TO_COMBINE,
        "document_ids": document_ids,
        "lifecycle": lifecycle,
        "relationship_checks": (
            relationship_checks
        ),
        "blocking_relationships": [],
        "review_relationships": [],
        "unsupported_relationship_count": len(
            unsupported_relationships
        ),
        "reason": (
            "No explicit conflict, replacement or "
            "precedence relationship was established "
            "by the supplied Active evidence."
        ),
    }