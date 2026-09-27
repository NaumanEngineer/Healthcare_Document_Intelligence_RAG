"""Corrective false-premise validation for evidence-set reasoning.

This module supports grounded corrective answers when a user's question assumes
a document relationship that the supplied evidence does not establish.

Example:

User premise:
"Which policy takes precedence in the conflict between DOC-003 and DOC-011?"

If the Active evidence does not establish a CONFLICT relationship, the system
may support a corrective statement such as:

"The available evidence does not establish that DOC-003 and DOC-011 conflict."

This module does not prove that no conflict could ever exist. It only evaluates
whether the supplied evidence establishes the alleged relationship.
"""

from __future__ import annotations

from typing import Any

from src.governance.evidence_set_relationship import (
    RELATIONSHIP_NOT_ESTABLISHED,
    RELATIONSHIP_SUPPORTED,
    REVIEW_REQUIRED,
    validate_evidence_set_relationship,
)


CORRECTION_SUPPORTED = "CORRECTION_SUPPORTED"
CORRECTION_NOT_SUPPORTED = "CORRECTION_NOT_SUPPORTED"


def validate_corrective_false_premise(
    alleged_relationship: str,
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate whether a corrective relationship statement is justified.

    A correction is supported only when:

    - at least two relevant documents are supplied;
    - lifecycle checks pass;
    - the alleged relationship is NOT established by the supplied evidence.

    A correction is not supported when the alleged relationship is explicitly
    established.

    Ambiguous or lifecycle-risk evidence remains REVIEW_REQUIRED.
    """

    if not isinstance(
        alleged_relationship,
        str,
    ):
        raise TypeError(
            "alleged_relationship must be a string"
        )

    if not alleged_relationship.strip():
        raise ValueError(
            "alleged_relationship must not be blank"
        )

    if not isinstance(
        evidence_items,
        list,
    ):
        raise TypeError(
            "evidence_items must be a list"
        )

    relationship_result = (
        validate_evidence_set_relationship(
            alleged_relationship,
            evidence_items,
        )
    )

    relationship_decision = (
        relationship_result[
            "decision"
        ]
    )

    if (
        relationship_decision
        == RELATIONSHIP_NOT_ESTABLISHED
    ):
        return {
            "decision": CORRECTION_SUPPORTED,
            "alleged_relationship": (
                alleged_relationship
                .strip()
                .upper()
            ),
            "document_ids": (
                relationship_result[
                    "document_ids"
                ]
            ),
            "relationship_decision": (
                relationship_decision
            ),
            "may_return_correction": True,
            "requires_human_review": False,
            "reason": (
                "The supplied Active evidence does not "
                "establish the alleged relationship. "
                "A carefully worded corrective statement "
                "is therefore supported."
            ),
        }

    if (
        relationship_decision
        == RELATIONSHIP_SUPPORTED
    ):
        return {
            "decision": CORRECTION_NOT_SUPPORTED,
            "alleged_relationship": (
                alleged_relationship
                .strip()
                .upper()
            ),
            "document_ids": (
                relationship_result[
                    "document_ids"
                ]
            ),
            "relationship_decision": (
                relationship_decision
            ),
            "may_return_correction": False,
            "requires_human_review": False,
            "reason": (
                "The supplied evidence explicitly establishes "
                "the alleged relationship, so a statement saying "
                "that the relationship is not established would "
                "not be supported."
            ),
        }

    if (
        relationship_decision
        == REVIEW_REQUIRED
    ):
        return {
            "decision": REVIEW_REQUIRED,
            "alleged_relationship": (
                alleged_relationship
                .strip()
                .upper()
            ),
            "document_ids": (
                relationship_result[
                    "document_ids"
                ]
            ),
            "relationship_decision": (
                relationship_decision
            ),
            "may_return_correction": False,
            "requires_human_review": True,
            "reason": (
                "The evidence set cannot safely establish "
                "whether the alleged relationship exists. "
                "Human review is required."
            ),
        }

    return {
        "decision": REVIEW_REQUIRED,
        "alleged_relationship": (
            alleged_relationship
            .strip()
            .upper()
        ),
        "document_ids": (
            relationship_result.get(
                "document_ids",
                [],
            )
        ),
        "relationship_decision": (
            relationship_decision
        ),
        "may_return_correction": False,
        "requires_human_review": True,
        "reason": (
            "Unexpected relationship-validation outcome. "
            "Human review is required."
        ),
    }