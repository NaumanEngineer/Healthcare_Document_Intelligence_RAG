"""Deterministic evidence-set relationship validation.

This module checks whether a requested relationship between operational
documents is explicitly established by the supplied evidence.

Supported relationship types:

- CONFLICT
- COMPLEMENTS
- REPLACES
- TAKES_PRECEDENCE

Possible decisions:

- RELATIONSHIP_SUPPORTED
- RELATIONSHIP_NOT_ESTABLISHED
- REVIEW_REQUIRED

This module is intentionally conservative.

It does not perform general natural-language contradiction detection and does
not infer a conflict merely because two documents discuss the same topic.
"""

from __future__ import annotations

import re
from typing import Any


RELATIONSHIP_SUPPORTED = "RELATIONSHIP_SUPPORTED"
RELATIONSHIP_NOT_ESTABLISHED = "RELATIONSHIP_NOT_ESTABLISHED"
REVIEW_REQUIRED = "REVIEW_REQUIRED"


SUPPORTED_RELATIONSHIP_TYPES = {
    "CONFLICT",
    "COMPLEMENTS",
    "REPLACES",
    "TAKES_PRECEDENCE",
}


RELATIONSHIP_PATTERNS = {
    "COMPLEMENTS": (
        "complements",
        "complementary to",
        "works alongside",
        "supports alongside",
    ),
    "REPLACES": (
        "replaces",
        "supersedes",
        "replaces all",
        "replaces the",
    ),
    "TAKES_PRECEDENCE": (
        "takes precedence",
        "has precedence",
        "takes priority over",
        "overrides",
    ),
    "CONFLICT": (
        "conflicts with",
        "is in conflict with",
        "contradicts",
        "contradiction",
        "inconsistent with",
    ),
}


RISKY_STATUSES = {
    "draft",
    "superseded",
    "archived",
}


def _normalise(
    text: str,
) -> str:
    if not isinstance(text, str):
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def _get_document_ids(
    evidence_items: list[dict[str, Any]],
) -> list[str]:
    document_ids = []

    for item in evidence_items:
        document_id = item.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id
            and document_id not in document_ids
        ):
            document_ids.append(
                document_id
            )

    return document_ids


def _get_evidence_text(
    evidence_items: list[dict[str, Any]],
) -> str:
    parts = []

    for item in evidence_items:
        for field in (
            "title",
            "section",
            "text",
        ):
            value = item.get(field)

            if (
                isinstance(value, str)
                and value.strip()
            ):
                parts.append(
                    value.strip()
                )

    return " ".join(parts)


def _all_evidence_active(
    evidence_items: list[dict[str, Any]],
) -> bool:
    if not evidence_items:
        return False

    for item in evidence_items:
        status = item.get(
            "status"
        )

        if not isinstance(
            status,
            str,
        ):
            return False

        if _normalise(status) != "active":
            return False

    return True


def _has_lifecycle_risk(
    evidence_items: list[dict[str, Any]],
) -> bool:
    for item in evidence_items:
        status = item.get(
            "status"
        )

        if not isinstance(
            status,
            str,
        ):
            continue

        if (
            _normalise(status)
            in RISKY_STATUSES
        ):
            return True

    return False


def _find_relationship_terms(
    relationship_type: str,
    evidence_text: str,
) -> list[str]:
    patterns = (
        RELATIONSHIP_PATTERNS[
            relationship_type
        ]
    )

    normalised_evidence = (
        _normalise(
            evidence_text
        )
    )

    matched = []

    for pattern in patterns:
        normalised_pattern = (
            _normalise(
                pattern
            )
        )

        if (
            normalised_pattern
            in normalised_evidence
        ):
            matched.append(
                pattern
            )

    return matched


def validate_evidence_set_relationship(
    relationship_type: str,
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate an explicitly requested relationship across evidence.

    Parameters
    ----------
    relationship_type:
        One of:
        - CONFLICT
        - COMPLEMENTS
        - REPLACES
        - TAKES_PRECEDENCE

    evidence_items:
        Relevant retrieved evidence items.

    Returns
    -------
    Structured relationship decision.
    """

    if not isinstance(
        relationship_type,
        str,
    ):
        raise TypeError(
            "relationship_type must be a string"
        )

    relationship_type = (
        relationship_type
        .strip()
        .upper()
    )

    if (
        relationship_type
        not in SUPPORTED_RELATIONSHIP_TYPES
    ):
        raise ValueError(
            "Unsupported relationship_type: "
            f"{relationship_type}"
        )

    if not isinstance(
        evidence_items,
        list,
    ):
        raise TypeError(
            "evidence_items must be a list"
        )

    if any(
        not isinstance(
            item,
            dict,
        )
        for item in evidence_items
    ):
        raise TypeError(
            "each evidence item must be a dictionary"
        )

    document_ids = (
        _get_document_ids(
            evidence_items
        )
    )

    if len(document_ids) < 2:
        return {
            "relationship_type": relationship_type,
            "decision": REVIEW_REQUIRED,
            "document_ids": document_ids,
            "evidence_status": "INSUFFICIENT_DOCUMENT_SET",
            "matched_relationship_terms": [],
            "reason": (
                "At least two distinct documents are required "
                "for evidence-set relationship validation."
            ),
        }

    if _has_lifecycle_risk(
        evidence_items
    ):
        return {
            "relationship_type": relationship_type,
            "decision": REVIEW_REQUIRED,
            "document_ids": document_ids,
            "evidence_status": "LIFECYCLE_RISK",
            "matched_relationship_terms": [],
            "reason": (
                "The supplied evidence includes Draft, "
                "Superseded, or Archived material."
            ),
        }

    if not _all_evidence_active(
        evidence_items
    ):
        return {
            "relationship_type": relationship_type,
            "decision": REVIEW_REQUIRED,
            "document_ids": document_ids,
            "evidence_status": "NOT_CONFIRMED_ACTIVE",
            "matched_relationship_terms": [],
            "reason": (
                "All documents must be confirmed Active before "
                "an authoritative relationship can be established."
            ),
        }

    evidence_text = (
        _get_evidence_text(
            evidence_items
        )
    )

    matched_terms = (
        _find_relationship_terms(
            relationship_type,
            evidence_text,
        )
    )

    if matched_terms:
        return {
            "relationship_type": relationship_type,
            "decision": RELATIONSHIP_SUPPORTED,
            "document_ids": document_ids,
            "evidence_status": "ACTIVE_ONLY",
            "matched_relationship_terms": matched_terms,
            "reason": (
                "The supplied Active evidence explicitly "
                f"contains language supporting the requested "
                f"{relationship_type} relationship."
            ),
        }

    return {
        "relationship_type": relationship_type,
        "decision": RELATIONSHIP_NOT_ESTABLISHED,
        "document_ids": document_ids,
        "evidence_status": "ACTIVE_ONLY",
        "matched_relationship_terms": [],
        "reason": (
            "No explicit evidence establishing the requested "
            f"{relationship_type} relationship was found in "
            "the supplied Active evidence."
        ),
    }