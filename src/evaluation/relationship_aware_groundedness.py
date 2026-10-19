"""Relationship-aware groundedness for Week 26 adversarial assurance.

This module evaluates whether multiple evidence items may legitimately
support one material claim.

It does not replace citation verification or evidence precedence.

It adds a new analytical layer that asks:

    Are these pieces of evidence actually related in a way that
    permits them to support this claim together?

Core safety principle:

    Multiple pieces of evidence do not automatically become one
    piece of evidence.

The evaluator is deliberately fail-closed.

It never increases answer authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


GROUNDED_SINGLE_SOURCE = "GROUNDED_SINGLE_SOURCE"
GROUNDED_MULTI_SOURCE = "GROUNDED_MULTI_SOURCE"
PARTIALLY_GROUNDED = "PARTIALLY_GROUNDED"
UNGROUNDED = "UNGROUNDED"
CONFLICT_BLOCKED = "CONFLICT_BLOCKED"
RELATIONSHIP_UNVERIFIED = "RELATIONSHIP_UNVERIFIED"
NOT_APPLICABLE = "NOT_APPLICABLE"


DIRECT_SUPPORT = "DIRECT_SUPPORT"
PARTIAL_SUPPORT = "PARTIAL_SUPPORT"
NO_SUPPORT = "NO_SUPPORT"
CONTRADICTS = "CONTRADICTS"
INVALID_SOURCE = "INVALID_SOURCE"


SAME_DOCUMENT_CONTEXT = "SAME_DOCUMENT_CONTEXT"
EXPLICIT_SUPPORT_CHAIN = "EXPLICIT_SUPPORT_CHAIN"
COMPLEMENTARY_EVIDENCE = "COMPLEMENTARY_EVIDENCE"
EXPLICIT_CONFLICT = "EXPLICIT_CONFLICT"
VERSION_SUCCESSION = "VERSION_SUCCESSION"
UNRELATED = "UNRELATED"
UNKNOWN_RELATIONSHIP = "UNKNOWN_RELATIONSHIP"
NOT_APPLICABLE_RELATIONSHIP = "NOT_APPLICABLE"


COMPOSITION_ALLOWED = "COMPOSITION_ALLOWED"
COMPOSITION_REVIEW_REQUIRED = "COMPOSITION_REVIEW_REQUIRED"
COMPOSITION_BLOCKED = "COMPOSITION_BLOCKED"
RELATIONSHIP_UNVERIFIED_RESULT = "RELATIONSHIP_UNVERIFIED"
NOT_APPLICABLE_RESULT = "NOT_APPLICABLE"


ALLOWED_LIFECYCLE_STATUSES = {
    "active",
}


@dataclass(frozen=True)
class SourceSupportResult:
    """One evidence item's support relationship to one claim."""

    evidence_id: str
    support_status: str
    lifecycle_valid: bool
    reason: str


def _normalise(
    value: str,
) -> str:
    """Normalise text for lightweight comparison."""

    return " ".join(
        value.lower().strip().split()
    )


def _material_terms(
    text: str,
) -> set[str]:
    """Return material lexical terms for conservative comparison."""

    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "because",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "should",
        "that",
        "the",
        "their",
        "this",
        "to",
        "was",
        "were",
        "with",
    }

    cleaned = []

    for character in _normalise(
        text
    ):
        if (
            character.isalnum()
            or character.isspace()
        ):
            cleaned.append(
                character
            )
        else:
            cleaned.append(
                " "
            )

    return {
        token
        for token
        in "".join(
            cleaned
        ).split()
        if (
            token
            and token
            not in stop_words
        )
    }


def _is_lifecycle_valid(
    evidence: dict[str, Any],
) -> bool:
    """Accept only active evidence for current operational support."""

    status = evidence.get(
        "status"
    )

    if not isinstance(
        status,
        str,
    ):
        return False

    return (
        _normalise(
            status
        )
        in ALLOWED_LIFECYCLE_STATUSES
    )


def _support_ratio(
    claim_text: str,
    evidence_text: str,
) -> float:
    """Return simple lexical material-term coverage."""

    claim_terms = _material_terms(
        claim_text
    )

    evidence_terms = _material_terms(
        evidence_text
    )

    if not claim_terms:
        return 0.0

    return (
        len(
            claim_terms
            & evidence_terms
        )
        / len(
            claim_terms
        )
    )


def assess_source_support(
    claim_text: str,
    evidence: dict[str, Any],
) -> SourceSupportResult:
    """Assess one evidence item against one claim.

    This is intentionally conservative and lightweight.

    It is not intended to replace the production citation verifier.
    It provides source-level relationship-aware input.
    """

    evidence_id = str(
        evidence.get(
            "evidence_id",
            "",
        )
    ).strip()

    if not evidence_id:
        raise ValueError(
            "Evidence must contain a non-blank evidence_id."
        )

    evidence_text = evidence.get(
        "text"
    )

    if not isinstance(
        evidence_text,
        str,
    ):
        evidence_text = evidence.get(
            "evidence_text"
        )

    if (
        not isinstance(
            evidence_text,
            str,
        )
        or not evidence_text.strip()
    ):
        return SourceSupportResult(
            evidence_id=evidence_id,
            support_status=INVALID_SOURCE,
            lifecycle_valid=False,
            reason=(
                "Evidence contains no usable text."
            ),
        )

    lifecycle_valid = (
        _is_lifecycle_valid(
            evidence
        )
    )

    if not lifecycle_valid:
        return SourceSupportResult(
            evidence_id=evidence_id,
            support_status=INVALID_SOURCE,
            lifecycle_valid=False,
            reason=(
                "Evidence is not lifecycle-valid "
                "for current operational support."
            ),
        )

    ratio = _support_ratio(
        claim_text,
        evidence_text,
    )

    if ratio >= 0.80:
        status = DIRECT_SUPPORT
        reason = (
            "Evidence contains strong direct lexical "
            "support for the claim."
        )

    elif ratio >= 0.35:
        status = PARTIAL_SUPPORT
        reason = (
            "Evidence contains partial lexical "
            "support for the claim."
        )

    else:
        status = NO_SUPPORT
        reason = (
            "Evidence does not contain enough material "
            "support for the claim."
        )

    return SourceSupportResult(
        evidence_id=evidence_id,
        support_status=status,
        lifecycle_valid=True,
        reason=reason,
    )


def _relationship_from_case_metadata(
    relationship: str | None,
) -> str:
    """Validate and normalise an explicit relationship state."""

    if relationship is None:
        return UNKNOWN_RELATIONSHIP

    allowed = {
        SAME_DOCUMENT_CONTEXT,
        EXPLICIT_SUPPORT_CHAIN,
        COMPLEMENTARY_EVIDENCE,
        EXPLICIT_CONFLICT,
        VERSION_SUCCESSION,
        UNRELATED,
        UNKNOWN_RELATIONSHIP,
        NOT_APPLICABLE_RELATIONSHIP,
    }

    if relationship not in allowed:
        raise ValueError(
            f"Unknown evidence relationship: {relationship}"
        )

    return relationship


def _composition_result(
    relationship: str,
) -> str:
    """Convert evidence relationship into composition permission."""

    if relationship in {
        SAME_DOCUMENT_CONTEXT,
        EXPLICIT_SUPPORT_CHAIN,
        COMPLEMENTARY_EVIDENCE,
    }:
        return COMPOSITION_ALLOWED

    if relationship in {
        EXPLICIT_CONFLICT,
    }:
        return COMPOSITION_BLOCKED

    if relationship in {
        VERSION_SUCCESSION,
        UNRELATED,
        UNKNOWN_RELATIONSHIP,
    }:
        return COMPOSITION_REVIEW_REQUIRED

    if relationship == NOT_APPLICABLE_RELATIONSHIP:
        return NOT_APPLICABLE_RESULT

    return RELATIONSHIP_UNVERIFIED_RESULT


def assess_relationship_aware_groundedness(
    *,
    claim_id: str,
    claim_text: str,
    evidence_items: list[dict[str, Any]],
    relationship: str | None,
    material: bool = True,
) -> dict[str, Any]:
    """Assess one claim using source support plus evidence relationship.

    Rules:

    - a single directly supporting source may ground a claim;
    - multiple sources require an explicit relationship;
    - unrelated or unknown relationships cannot create multi-source support;
    - explicit conflicts block composition;
    - lifecycle-invalid evidence cannot contribute current support;
    - additional evidence never increases authority by itself.
    """

    if (
        not isinstance(
            claim_id,
            str,
        )
        or not claim_id.strip()
    ):
        raise ValueError(
            "claim_id must be a non-blank string."
        )

    if (
        not isinstance(
            claim_text,
            str,
        )
        or not claim_text.strip()
    ):
        raise ValueError(
            "claim_text must be a non-blank string."
        )

    if not isinstance(
        evidence_items,
        list,
    ):
        raise TypeError(
            "evidence_items must be a list."
        )

    if not isinstance(
        material,
        bool,
    ):
        raise TypeError(
            "material must be a boolean."
        )

    if not material:
        return {
            "claim_id": claim_id,
            "groundedness_status": NOT_APPLICABLE,
            "material": False,
            "evidence_ids_considered": [],
            "source_level_results": [],
            "relationship_result": (
                NOT_APPLICABLE_RESULT
            ),
            "relationship": (
                NOT_APPLICABLE_RELATIONSHIP
            ),
            "supported_components": [],
            "unsupported_components": [],
            "contradictory_components": [],
            "lifecycle_valid": True,
            "composition_allowed": False,
            "final_reason": (
                "Claim is not material to the answer."
            ),
        }

    source_results = [
        assess_source_support(
            claim_text,
            evidence,
        )
        for evidence
        in evidence_items
    ]

    relationship_state = (
        _relationship_from_case_metadata(
            relationship
        )
    )

    composition = (
        _composition_result(
            relationship_state
        )
    )

    valid_results = [
        result
        for result
        in source_results
        if result.lifecycle_valid
    ]

    direct_support = [
        result
        for result
        in valid_results
        if result.support_status
        == DIRECT_SUPPORT
    ]

    partial_support = [
        result
        for result
        in valid_results
        if result.support_status
        == PARTIAL_SUPPORT
    ]

    unsupported = [
        result
        for result
        in valid_results
        if result.support_status
        == NO_SUPPORT
    ]

    invalid = [
        result
        for result
        in source_results
        if result.support_status
        == INVALID_SOURCE
    ]

    lifecycle_valid = (
        len(
            invalid
        )
        == 0
    )

    evidence_ids = [
        result.evidence_id
        for result
        in source_results
    ]

    if not evidence_items:
        groundedness = UNGROUNDED
        final_reason = (
            "No evidence was supplied for the material claim."
        )

    elif not lifecycle_valid:
        groundedness = UNGROUNDED
        final_reason = (
            "One or more evidence items are not lifecycle-valid."
        )

    elif relationship_state == EXPLICIT_CONFLICT:
        groundedness = CONFLICT_BLOCKED
        final_reason = (
            "Evidence contains an explicit conflict and may not "
            "be compressed into one operational conclusion."
        )

    elif len(
        evidence_items
    ) == 1:
        if direct_support:
            groundedness = GROUNDED_SINGLE_SOURCE
            final_reason = (
                "One lifecycle-valid source directly supports "
                "the material claim."
            )

        elif partial_support:
            groundedness = PARTIALLY_GROUNDED
            final_reason = (
                "The single source provides only partial support."
            )

        else:
            groundedness = UNGROUNDED
            final_reason = (
                "The supplied source does not materially "
                "support the claim."
            )

    elif relationship_state in {
        UNRELATED,
        UNKNOWN_RELATIONSHIP,
        VERSION_SUCCESSION,
    }:
        groundedness = RELATIONSHIP_UNVERIFIED
        final_reason = (
            "Multiple evidence items cannot be composed because "
            "their support relationship is not sufficient for "
            "joint grounding."
        )

    elif composition == COMPOSITION_ALLOWED:
        if direct_support:
            groundedness = GROUNDED_MULTI_SOURCE
            final_reason = (
                "Multiple lifecycle-valid evidence items have an "
                "explicit relationship permitting composition."
            )

        elif partial_support:
            groundedness = PARTIALLY_GROUNDED
            final_reason = (
                "Related evidence provides only partial support."
            )

        else:
            groundedness = UNGROUNDED
            final_reason = (
                "Related evidence still does not materially "
                "support the claim."
            )

    else:
        groundedness = RELATIONSHIP_UNVERIFIED
        final_reason = (
            "Evidence relationship does not permit confident "
            "multi-source composition."
        )

    return {
        "claim_id": claim_id,
        "groundedness_status": groundedness,
        "material": material,
        "evidence_ids_considered": (
            evidence_ids
        ),
        "source_level_results": [
            {
                "evidence_id": result.evidence_id,
                "support_status": (
                    result.support_status
                ),
                "lifecycle_valid": (
                    result.lifecycle_valid
                ),
                "reason": (
                    result.reason
                ),
            }
            for result
            in source_results
        ],
        "relationship_result": (
            composition
        ),
        "relationship": (
            relationship_state
        ),
        "supported_components": [
            result.evidence_id
            for result
            in (
                direct_support
                + partial_support
            )
        ],
        "unsupported_components": [
            result.evidence_id
            for result
            in unsupported
        ],
        "contradictory_components": (
            evidence_ids
            if relationship_state
            == EXPLICIT_CONFLICT
            else []
        ),
        "lifecycle_valid": (
            lifecycle_valid
        ),
        "composition_allowed": (
            composition
            == COMPOSITION_ALLOWED
        ),
        "final_reason": (
            final_reason
        ),
    }