"""Deterministic high-risk claim mismatch detection.

This module protects citation verification from unsafe semantic rescue.

It detects material differences between a generated claim and its cited
evidence, including:

- unsupported numbers;
- unsupported mandatory wording;
- unsupported actors;
- unsupported actions;
- negation mismatches;
- unsupported prohibitions.

If a high-risk mismatch is detected, downstream semantic similarity must not
be allowed to rescue the claim.

This is a deterministic governance control, not a general entailment model.
"""

from __future__ import annotations

import re


MANDATORY_TERMS = {
    "must",
    "mandatory",
    "require",
    "requires",
    "required",
    "immediate",
    "immediately",
}

PROHIBITION_TERMS = {
    "prohibits",
    "forbids",
    "forbidden",
    "must not",
    "cannot",
}

ACTOR_TERMS = {
    "chief executive",
    "executive",
    "manager",
    "managers",
}


ACTION_TERMS = {
    "suspend",
    "cancel",
    "redeploy",
    "restore",
    "open",
    "close",
    "evacuate",
    "evacuation",
}


def _normalise(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def _remove_document_ids(
    text: str,
) -> str:
    return re.sub(
        r"\bDOC-\d+\b",
        "",
        text,
        flags=re.IGNORECASE,
    )


def _extract_numbers(
    text: str,
) -> set[str]:
    cleaned = _remove_document_ids(
        text
    )

    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            _normalise(cleaned),
        )
    )


def _contains_terms(
    text: str,
    terms: set[str],
) -> set[str]:
    normalised = _normalise(
        text
    )

    return {
        term
        for term in terms
        if term in normalised
    }


def detect_high_risk_mismatch(
    claim_text: str,
    evidence_text: str,
) -> dict:
    """Detect material claim/evidence mismatches.

    Returns:

    {
        "guard_triggered": bool,
        "reasons": [...],
        "unsupported_numbers": [...],
        "unsupported_actors": [...],
        "unsupported_actions": [...]
    }
    """

    if not isinstance(
        claim_text,
        str,
    ):
        raise TypeError(
            "claim_text must be a string"
        )

    if not claim_text.strip():
        raise ValueError(
            "claim_text must not be blank"
        )

    if not isinstance(
        evidence_text,
        str,
    ):
        raise TypeError(
            "evidence_text must be a string"
        )

    if not evidence_text.strip():
        raise ValueError(
            "evidence_text must not be blank"
        )

    reasons: list[str] = []

    # --------------------------------------------------------------
    # Numbers / thresholds / deadlines
    # --------------------------------------------------------------

    claim_numbers = _extract_numbers(
        claim_text
    )

    evidence_numbers = _extract_numbers(
        evidence_text
    )

    unsupported_numbers = (
        claim_numbers
        - evidence_numbers
    )

    if unsupported_numbers:
        reasons.append(
            "unsupported_number"
        )

    # --------------------------------------------------------------
    # Mandatory wording
    # --------------------------------------------------------------

    claim_mandatory = (
        _contains_terms(
            claim_text,
            MANDATORY_TERMS,
        )
    )

    evidence_mandatory = (
        _contains_terms(
            evidence_text,
            MANDATORY_TERMS,
        )
    )

    if (
        claim_mandatory
        and not evidence_mandatory
    ):
        reasons.append(
            "unsupported_mandatory_wording"
        )

    # --------------------------------------------------------------
    # Prohibition wording
    # --------------------------------------------------------------

    claim_prohibition = (
        _contains_terms(
            claim_text,
            PROHIBITION_TERMS,
        )
    )

    evidence_prohibition = (
        _contains_terms(
            evidence_text,
            PROHIBITION_TERMS,
        )
    )

    if (
        claim_prohibition
        and not evidence_prohibition
    ):
        reasons.append(
            "unsupported_prohibition"
        )

    # --------------------------------------------------------------
    # Actors / responsibility
    # --------------------------------------------------------------

    claim_actors = (
        _contains_terms(
            claim_text,
            ACTOR_TERMS,
        )
    )

    evidence_actors = (
        _contains_terms(
            evidence_text,
            ACTOR_TERMS,
        )
    )

    unsupported_actors = (
        claim_actors
        - evidence_actors
    )

    if unsupported_actors:
        reasons.append(
            "unsupported_actor"
        )

    # --------------------------------------------------------------
    # Material actions
    # --------------------------------------------------------------

    claim_actions = (
        _contains_terms(
            claim_text,
            ACTION_TERMS,
        )
    )

    evidence_actions = (
        _contains_terms(
            evidence_text,
            ACTION_TERMS,
        )
    )

    unsupported_actions = (
        claim_actions
        - evidence_actions
    )

    if unsupported_actions:
        reasons.append(
            "unsupported_action"
        )

    # --------------------------------------------------------------
    # Negation mismatch
    # --------------------------------------------------------------

    claim_normalised = (
        _normalise(
            claim_text
        )
    )

    evidence_normalised = (
        _normalise(
            evidence_text
        )
    )

    claim_has_not = (
        " not "
        in f" {claim_normalised} "
    )

    evidence_has_not = (
        " not "
        in f" {evidence_normalised} "
    )

    if (
        claim_has_not
        and not evidence_has_not
    ):
        reasons.append(
            "negation_mismatch"
        )

    return {
        "guard_triggered": bool(
            reasons
        ),
        "reasons": reasons,
        "unsupported_numbers": sorted(
            unsupported_numbers
        ),
        "unsupported_actors": sorted(
            unsupported_actors
        ),
        "unsupported_actions": sorted(
            unsupported_actions
        ),
    }