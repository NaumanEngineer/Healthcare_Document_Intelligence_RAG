"""Week 26 semantic precision audit.

This module hardens claim support decisions against:

- modal strengthening;
- certainty inflation;
- immediacy inflation;
- role / responsibility hallucination;
- unsupported actor attribution.

It is designed to sit after ordinary citation verification.

Important safety rule:

    Semantic precision may reduce support confidence.
    It must never increase support confidence.

Examples:

Evidence:
    "Escalation may be considered."

Claim:
    "Escalation is expected to proceed."

Result:
    existing SUPPORTED -> PARTIALLY_SUPPORTED

Evidence:
    "Evacuation may be required."

Claim:
    "The site operations manager is responsible for initiating evacuation."

Result:
    existing PARTIALLY_SUPPORTED -> UNSUPPORTED
"""

from __future__ import annotations

import re
from typing import Any


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"
CITATION_MISMATCH = "CITATION_MISMATCH"


CLEAR = "CLEAR"
MODAL_STRENGTHENING = "MODAL_STRENGTHENING"
IMMEDIACY_STRENGTHENING = "IMMEDIACY_STRENGTHENING"
ROLE_RESPONSIBILITY_UNSUPPORTED = (
    "ROLE_RESPONSIBILITY_UNSUPPORTED"
)
AUTHORITY_ATTRIBUTION_UNSUPPORTED = (
    "AUTHORITY_ATTRIBUTION_UNSUPPORTED"
)
MULTIPLE_PRECISION_RISKS = "MULTIPLE_PRECISION_RISKS"


SUPPORT_ORDER = {
    CITATION_MISMATCH: 0,
    UNSUPPORTED: 1,
    PARTIALLY_SUPPORTED: 2,
    SUPPORTED: 3,
}


# Modal strength intentionally reflects operational authority.
#
# Important:
#
#     "may be considered"
#
# must remain weaker than:
#
#     "can"
#
# Therefore "consider", "considered" and "appropriate" do not
# independently increase the authority level beyond MAY.
MODAL_STRENGTH = {
    "may": 1,
    "might": 1,
    "could": 1,
    "consider": 1,
    "considered": 1,
    "appropriate": 1,
    "can": 2,
    "should": 3,
    "expected": 3,
    "expect": 3,
    "required": 4,
    "require": 4,
    "requires": 4,
    "must": 5,
    "mandatory": 5,
}


IMMEDIACY_TERMS = {
    "immediate",
    "immediately",
    "now",
    "without delay",
}


ROLE_TERMS = {
    "chief executive",
    "executive",
    "site operations manager",
    "operations manager",
    "manager",
    "managers",
    "clinical director",
    "medical director",
    "nurse director",
    "board",
    "leadership",
}


RESPONSIBILITY_TERMS = {
    "responsible",
    "responsibility",
    "authorise",
    "authorises",
    "authorised",
    "authorize",
    "authorizes",
    "authorized",
    "approve",
    "approves",
    "approved",
    "initiate",
    "initiates",
    "initiating",
    "must decide",
    "decision maker",
    "decision-maker",
}


def _normalise(
    text: str,
) -> str:
    """Normalise text for deterministic phrase matching."""

    return " ".join(
        str(
            text
        ).lower().strip().split()
    )


def _contains_phrase(
    text: str,
    phrase: str,
) -> bool:
    """Return True when a phrase occurs as lexical content."""

    text = _normalise(
        text
    )

    phrase = _normalise(
        phrase
    )

    if " " in phrase:
        return phrase in text

    return (
        re.search(
            rf"\b{re.escape(phrase)}\b",
            text,
        )
        is not None
    )


def _highest_modal_strength(
    text: str,
) -> tuple[
    int,
    list[str],
]:
    """Return highest detected modal strength and matching terms."""

    matches = [
        term
        for term
        in MODAL_STRENGTH
        if _contains_phrase(
            text,
            term,
        )
    ]

    if not matches:
        return (
            0,
            [],
        )

    strength = max(
        MODAL_STRENGTH[
            term
        ]
        for term
        in matches
    )

    strongest_terms = sorted(
        term
        for term
        in matches
        if MODAL_STRENGTH[
            term
        ]
        == strength
    )

    return (
        strength,
        strongest_terms,
    )


def _detected_phrases(
    text: str,
    candidates: set[str],
) -> list[str]:
    """Return deterministic list of detected phrases."""

    return sorted(
        phrase
        for phrase
        in candidates
        if _contains_phrase(
            text,
            phrase,
        )
    )


def _combined_evidence_text(
    evidence_items: list[dict[str, Any]],
) -> str:
    """Combine evidence text for precision comparison."""

    texts = []

    for evidence in evidence_items:
        text = evidence.get(
            "text"
        )

        if not isinstance(
            text,
            str,
        ):
            text = evidence.get(
                "evidence_text"
            )

        if (
            isinstance(
                text,
                str,
            )
            and text.strip()
        ):
            texts.append(
                text.strip()
            )

    return " ".join(
        texts
    )


def _reduce_support(
    existing_status: str,
    target_status: str,
) -> str:
    """Reduce support only.

    The semantic audit is forbidden from increasing support.
    """

    if existing_status not in SUPPORT_ORDER:
        raise ValueError(
            "Unknown existing support status: "
            f"{existing_status}"
        )

    if target_status not in SUPPORT_ORDER:
        raise ValueError(
            "Unknown target support status: "
            f"{target_status}"
        )

    if (
        SUPPORT_ORDER[
            target_status
        ]
        < SUPPORT_ORDER[
            existing_status
        ]
    ):
        return target_status

    return existing_status


def audit_semantic_precision(
    *,
    claim_id: str,
    claim_text: str,
    evidence_items: list[dict[str, Any]],
    existing_support_status: str,
) -> dict[str, Any]:
    """Audit semantic precision for one material claim.

    The audit looks for differences between the authority / certainty
    expressed by the evidence and the authority / certainty expressed
    by the claim.

    It returns a revised support status but cannot increase support.
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

    if existing_support_status not in SUPPORT_ORDER:
        raise ValueError(
            "Unsupported support status: "
            f"{existing_support_status}"
        )

    evidence_text = (
        _combined_evidence_text(
            evidence_items
        )
    )

    (
        claim_modal_strength,
        claim_modal_terms,
    ) = _highest_modal_strength(
        claim_text
    )

    (
        evidence_modal_strength,
        evidence_modal_terms,
    ) = _highest_modal_strength(
        evidence_text
    )

    claim_immediacy = (
        _detected_phrases(
            claim_text,
            IMMEDIACY_TERMS,
        )
    )

    evidence_immediacy = (
        _detected_phrases(
            evidence_text,
            IMMEDIACY_TERMS,
        )
    )

    claim_roles = (
        _detected_phrases(
            claim_text,
            ROLE_TERMS,
        )
    )

    evidence_roles = (
        _detected_phrases(
            evidence_text,
            ROLE_TERMS,
        )
    )

    claim_responsibility = (
        _detected_phrases(
            claim_text,
            RESPONSIBILITY_TERMS,
        )
    )

    evidence_responsibility = (
        _detected_phrases(
            evidence_text,
            RESPONSIBILITY_TERMS,
        )
    )

    modal_strengthening = (
        claim_modal_strength
        > evidence_modal_strength
        and claim_modal_strength > 0
    )

    immediacy_strengthening = (
        bool(
            claim_immediacy
        )
        and not bool(
            evidence_immediacy
        )
    )

    unsupported_claim_roles = [
        role
        for role
        in claim_roles
        if not _contains_phrase(
            evidence_text,
            role,
        )
    ]

    role_introduced = bool(
        unsupported_claim_roles
    )

    responsibility_introduced = (
        bool(
            claim_responsibility
        )
        and not bool(
            evidence_responsibility
        )
    )

    role_responsibility_unsupported = (
        bool(
            claim_roles
        )
        and bool(
            claim_responsibility
        )
        and (
            role_introduced
            or responsibility_introduced
        )
    )

    authority_attribution_unsupported = (
        bool(
            claim_roles
        )
        and (
            claim_modal_strength >= 4
            or bool(
                claim_responsibility
            )
        )
        and (
            role_introduced
            or responsibility_introduced
        )
    )

    risks = []

    revised_status = (
        existing_support_status
    )

    if modal_strengthening:
        risks.append(
            MODAL_STRENGTHENING
        )

        revised_status = (
            _reduce_support(
                revised_status,
                PARTIALLY_SUPPORTED,
            )
        )

    if immediacy_strengthening:
        risks.append(
            IMMEDIACY_STRENGTHENING
        )

        revised_status = (
            _reduce_support(
                revised_status,
                UNSUPPORTED,
            )
        )

    if role_responsibility_unsupported:
        risks.append(
            ROLE_RESPONSIBILITY_UNSUPPORTED
        )

        revised_status = (
            _reduce_support(
                revised_status,
                UNSUPPORTED,
            )
        )

    elif authority_attribution_unsupported:
        risks.append(
            AUTHORITY_ATTRIBUTION_UNSUPPORTED
        )

        revised_status = (
            _reduce_support(
                revised_status,
                UNSUPPORTED,
            )
        )

    if not risks:
        decision = CLEAR

    elif len(
        risks
    ) == 1:
        decision = risks[
            0
        ]

    else:
        decision = (
            MULTIPLE_PRECISION_RISKS
        )

    return {
        "claim_id": claim_id,
        "decision": decision,
        "existing_support_status": (
            existing_support_status
        ),
        "revised_support_status": (
            revised_status
        ),
        "support_reduced": (
            revised_status
            != existing_support_status
        ),
        "modal_strengthening_detected": (
            modal_strengthening
        ),
        "immediacy_strengthening_detected": (
            immediacy_strengthening
        ),
        "role_responsibility_unsupported": (
            role_responsibility_unsupported
        ),
        "authority_attribution_unsupported": (
            authority_attribution_unsupported
        ),
        "unsupported_claim_roles": (
            unsupported_claim_roles
        ),
        "claim_modal_strength": (
            claim_modal_strength
        ),
        "evidence_modal_strength": (
            evidence_modal_strength
        ),
        "claim_modal_terms": (
            claim_modal_terms
        ),
        "evidence_modal_terms": (
            evidence_modal_terms
        ),
        "claim_immediacy_terms": (
            claim_immediacy
        ),
        "evidence_immediacy_terms": (
            evidence_immediacy
        ),
        "claim_role_terms": (
            claim_roles
        ),
        "evidence_role_terms": (
            evidence_roles
        ),
        "claim_responsibility_terms": (
            claim_responsibility
        ),
        "evidence_responsibility_terms": (
            evidence_responsibility
        ),
        "risk_signals": (
            risks
        ),
    }