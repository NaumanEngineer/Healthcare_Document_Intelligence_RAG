"""Deterministic overstatement and uncertainty-preservation auditing.

Week 25 Day 4.

This module detects cases where generated answer wording becomes stronger than
the approved evidence.

Examples:

Evidence:
    "Staffing pressure may contribute to delays."

Unsafe claim:
    "Staffing pressure causes delays."

Evidence:
    "Some services reported pressure."

Unsafe claim:
    "All services experience pressure."

Evidence:
    "Teams should consider escalation."

Unsafe claim:
    "Teams must escalate."

The purpose of this module is not to perform general natural-language
entailment.

It deterministically detects specific authority-increasing transformations:

- uncertainty removal;
- causal overstatement;
- universal overstatement;
- mandatory-authority increase;
- unsupported policy authority.

The module is evidence-bounded and does not use external knowledge.
"""

from __future__ import annotations

import re
from typing import Any


PRESERVED = "PRESERVED"
OVERSTATEMENT_DETECTED = "OVERSTATEMENT_DETECTED"
NOT_APPLICABLE = "NOT_APPLICABLE"

PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


UNCERTAINTY_MARKERS = {
    "may",
    "might",
    "could",
    "possibly",
    "possible",
    "potential",
    "potentially",
    "suggest",
    "suggests",
    "suggested",
    "appears",
    "appear",
    "likely",
    "unlikely",
    "uncertain",
    "uncertainty",
}


EVIDENCE_CAUTION_PHRASES = {
    "evidence suggests",
    "available evidence suggests",
    "may contribute",
    "may be associated",
    "might contribute",
    "could contribute",
    "associated with",
    "association with",
    "correlated with",
    "correlation with",
}


CAUSAL_MARKERS = {
    "cause",
    "causes",
    "caused",
    "causing",
    "leads to",
    "lead to",
    "results in",
    "result in",
    "drives",
    "drive",
    "produces",
    "produce",
    "creates",
    "create",
}


UNIVERSAL_MARKERS = {
    "all",
    "always",
    "every",
    "everyone",
    "entire",
    "universally",
}


LIMITED_SCOPE_MARKERS = {
    "some",
    "several",
    "certain",
    "selected",
    "a number of",
    "in some cases",
    "some services",
    "some teams",
}


MANDATORY_MARKERS = {
    "must",
    "mandatory",
    "required",
    "requires",
    "shall",
    "immediately",
}


POLICY_AUTHORITY_PHRASES = {
    "policy requires",
    "policy mandates",
    "policy prohibits",
    "approved policy requires",
    "approved policy mandates",
    "official policy requires",
    "the policy requires",
}


CAUTIOUS_RECOMMENDATION_MARKERS = {
    "should",
    "consider",
    "considered",
    "review",
    "reviewed",
    "recommend",
    "recommended",
    "guidance",
}


IGNORED_TERMS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
}


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary."""

    if not isinstance(
        value,
        dict,
    ):
        raise TypeError(
            f"{field_name} must be a dictionary"
        )

    return value


def _require_list(
    value: Any,
    field_name: str,
) -> list:
    """Require a list."""

    if not isinstance(
        value,
        list,
    ):
        raise TypeError(
            f"{field_name} must be a list"
        )

    return value


def _require_non_empty_string(
    value: Any,
    field_name: str,
) -> str:
    """Require a non-empty string."""

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string"
        )

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return cleaned


def _normalise(
    text: str,
) -> str:
    """Normalise text for deterministic phrase matching."""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return " ".join(
        text.split()
    )


def _tokens(
    text: str,
) -> set[str]:
    """Return lexical material terms."""

    normalised = _normalise(
        text
    )

    terms = set()

    for term in normalised.split():
        if len(
            term
        ) <= 2:
            continue

        if term in IGNORED_TERMS:
            continue

        terms.add(
            term
        )

    return terms


def _contains_phrase_or_token(
    text: str,
    markers: set[str],
) -> bool:
    """Check markers deterministically."""

    normalised = _normalise(
        text
    )

    tokens = set(
        normalised.split()
    )

    for marker in markers:
        marker_normalised = (
            _normalise(
                marker
            )
        )

        if " " in marker_normalised:
            if marker_normalised in normalised:
                return True

        elif marker_normalised in tokens:
            return True

    return False


def _material_overlap(
    claim_text: str,
    evidence_text: str,
) -> float:
    """Measure whether claim and evidence address materially related content."""

    claim_terms = _tokens(
        claim_text
    )

    evidence_terms = _tokens(
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


def _combine_evidence_text(
    evidence_items: list[dict[str, Any]],
) -> str:
    """Combine approved evidence text."""

    parts = []

    for evidence in evidence_items:
        evidence = _require_mapping(
            evidence,
            "evidence item",
        )

        for field in (
            "title",
            "section",
            "text",
            "evidence_text",
        ):
            value = evidence.get(
                field
            )

            if (
                isinstance(
                    value,
                    str,
                )
                and value.strip()
            ):
                parts.append(
                    value.strip()
                )

    return " ".join(
        parts
    )


def _detect_uncertainty_removal(
    claim_text: str,
    evidence_text: str,
) -> bool:
    """Detect cautious evidence turned into an unqualified assertion."""

    evidence_uncertain = (
        _contains_phrase_or_token(
            evidence_text,
            UNCERTAINTY_MARKERS,
        )
        or _contains_phrase_or_token(
            evidence_text,
            EVIDENCE_CAUTION_PHRASES,
        )
    )

    claim_uncertain = (
        _contains_phrase_or_token(
            claim_text,
            UNCERTAINTY_MARKERS,
        )
        or _contains_phrase_or_token(
            claim_text,
            EVIDENCE_CAUTION_PHRASES,
        )
    )

    return (
        evidence_uncertain
        and not claim_uncertain
    )


def _detect_causal_increase(
    claim_text: str,
    evidence_text: str,
) -> bool:
    """Detect association/caution converted into causality."""

    claim_causal = (
        _contains_phrase_or_token(
            claim_text,
            CAUSAL_MARKERS,
        )
    )

    evidence_causal = (
        _contains_phrase_or_token(
            evidence_text,
            CAUSAL_MARKERS,
        )
    )

    evidence_cautious = (
        _contains_phrase_or_token(
            evidence_text,
            EVIDENCE_CAUTION_PHRASES,
        )
        or _contains_phrase_or_token(
            evidence_text,
            UNCERTAINTY_MARKERS,
        )
    )

    return (
        claim_causal
        and not evidence_causal
        and evidence_cautious
    )


def _detect_universal_increase(
    claim_text: str,
    evidence_text: str,
) -> bool:
    """Detect limited evidence converted into universal claims."""

    claim_universal = (
        _contains_phrase_or_token(
            claim_text,
            UNIVERSAL_MARKERS,
        )
    )

    evidence_universal = (
        _contains_phrase_or_token(
            evidence_text,
            UNIVERSAL_MARKERS,
        )
    )

    evidence_limited = (
        _contains_phrase_or_token(
            evidence_text,
            LIMITED_SCOPE_MARKERS,
        )
    )

    return (
        claim_universal
        and not evidence_universal
        and evidence_limited
    )


def _detect_mandatory_increase(
    claim_text: str,
    evidence_text: str,
) -> bool:
    """Detect advisory wording converted into obligation."""

    claim_mandatory = (
        _contains_phrase_or_token(
            claim_text,
            MANDATORY_MARKERS,
        )
    )

    evidence_mandatory = (
        _contains_phrase_or_token(
            evidence_text,
            MANDATORY_MARKERS,
        )
    )

    evidence_cautious = (
        _contains_phrase_or_token(
            evidence_text,
            CAUTIOUS_RECOMMENDATION_MARKERS,
        )
    )

    return (
        claim_mandatory
        and not evidence_mandatory
        and evidence_cautious
    )


def _detect_policy_authority_increase(
    claim_text: str,
    evidence_text: str,
) -> bool:
    """Detect unsupported policy-level authority."""

    claim_policy_authority = (
        _contains_phrase_or_token(
            claim_text,
            POLICY_AUTHORITY_PHRASES,
        )
    )

    evidence_policy_authority = (
        _contains_phrase_or_token(
            evidence_text,
            POLICY_AUTHORITY_PHRASES,
        )
    )

    return (
        claim_policy_authority
        and not evidence_policy_authority
    )


def audit_claim_overstatement(
    claim: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    *,
    material: bool = True,
    minimum_material_overlap: float = 0.25,
) -> dict[str, Any]:
    """Audit one claim for authority or certainty increase."""

    claim = _require_mapping(
        claim,
        "claim",
    )

    evidence_items = _require_list(
        evidence_items,
        "evidence_items",
    )

    claim_id = _require_non_empty_string(
        claim.get(
            "claim_id"
        ),
        "claim.claim_id",
    )

    claim_text = _require_non_empty_string(
        claim.get(
            "claim_text"
        ),
        "claim.claim_text",
    )

    if not isinstance(
        material,
        bool,
    ):
        raise TypeError(
            "material must be a boolean"
        )

    if not isinstance(
        minimum_material_overlap,
        (
            int,
            float,
        ),
    ):
        raise TypeError(
            "minimum_material_overlap must be numeric"
        )

    if not (
        0.0
        <= float(
            minimum_material_overlap
        )
        <= 1.0
    ):
        raise ValueError(
            "minimum_material_overlap must be between 0 and 1"
        )

    if not material:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": False,
            "status": NOT_APPLICABLE,
            "reason": (
                "Claim is non-substantive and does not "
                "require overstatement auditing."
            ),
            "material_overlap": None,
            "overstatement_types": [],
        }

    evidence_text = (
        _combine_evidence_text(
            evidence_items
        )
    )

    if not evidence_text:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": OVERSTATEMENT_DETECTED,
            "reason": (
                "No approved evidence text is available "
                "to justify the material claim."
            ),
            "material_overlap": 0.0,
            "overstatement_types": [
                "NO_SUPPORTING_EVIDENCE"
            ],
        }

    overlap = _material_overlap(
        claim_text,
        evidence_text,
    )

    overstatement_types = []

    if _detect_uncertainty_removal(
        claim_text,
        evidence_text,
    ):
        overstatement_types.append(
            "UNCERTAINTY_REMOVED"
        )

    if _detect_causal_increase(
        claim_text,
        evidence_text,
    ):
        overstatement_types.append(
            "CAUSALITY_INCREASED"
        )

    if _detect_universal_increase(
        claim_text,
        evidence_text,
    ):
        overstatement_types.append(
            "UNIVERSALITY_INCREASED"
        )

    if _detect_mandatory_increase(
        claim_text,
        evidence_text,
    ):
        overstatement_types.append(
            "MANDATORY_AUTHORITY_INCREASED"
        )

    if _detect_policy_authority_increase(
        claim_text,
        evidence_text,
    ):
        overstatement_types.append(
            "POLICY_AUTHORITY_INCREASED"
        )

    if (
        overstatement_types
        and overlap
        >= minimum_material_overlap
    ):
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": OVERSTATEMENT_DETECTED,
            "reason": (
                "Claim increases certainty, causality, "
                "scope, or authority beyond the "
                "approved evidence."
            ),
            "material_overlap": round(
                overlap,
                4,
            ),
            "overstatement_types": (
                overstatement_types
            ),
        }

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "material": True,
        "status": PRESERVED,
        "reason": (
            "No deterministic authority or certainty "
            "increase was detected."
        ),
        "material_overlap": round(
            overlap,
            4,
        ),
        "overstatement_types": [],
    }


def audit_answer_overstatement(
    claims: list[dict[str, Any]],
    evidence_by_claim_id: dict[
        str,
        list[dict[str, Any]],
    ],
    *,
    non_substantive_claim_ids: list[str] | None = None,
    upstream_governance_decision: str | None = None,
) -> dict[str, Any]:
    """Audit overstatement across an answer."""

    claims = _require_list(
        claims,
        "claims",
    )

    evidence_by_claim_id = (
        _require_mapping(
            evidence_by_claim_id,
            "evidence_by_claim_id",
        )
    )

    if non_substantive_claim_ids is None:
        non_substantive_claim_ids = []

    non_substantive_claim_ids = (
        _require_list(
            non_substantive_claim_ids,
            "non_substantive_claim_ids",
        )
    )

    non_substantive_set = {
        _require_non_empty_string(
            claim_id,
            "non-substantive claim ID",
        )
        for claim_id
        in non_substantive_claim_ids
    }

    results = []

    seen_claim_ids = set()

    for claim in claims:
        claim = _require_mapping(
            claim,
            "claim",
        )

        claim_id = _require_non_empty_string(
            claim.get(
                "claim_id"
            ),
            "claim.claim_id",
        )

        if claim_id in seen_claim_ids:
            raise ValueError(
                "Duplicate claim ID: "
                f"{claim_id}"
            )

        seen_claim_ids.add(
            claim_id
        )

        evidence_items = (
            evidence_by_claim_id.get(
                claim_id,
                [],
            )
        )

        result = (
            audit_claim_overstatement(
                claim,
                evidence_items,
                material=(
                    claim_id
                    not in non_substantive_set
                ),
            )
        )

        results.append(
            result
        )

    material_results = [
        result
        for result
        in results
        if result[
            "material"
        ]
    ]

    if (
        upstream_governance_decision
        == "ABSTAIN"
        and not material_results
    ):
        decision = ABSTAIN

        reason = (
            "Upstream governance requires abstention "
            "and no material claims require overstatement auditing."
        )

    elif not material_results:
        decision = PASS

        reason = (
            "No material claims require overstatement auditing."
        )

    elif all(
        result[
            "status"
        ]
        == PRESERVED
        for result
        in material_results
    ):
        decision = PASS

        reason = (
            "No material answer claim increases "
            "authority or certainty beyond the evidence."
        )

    else:
        decision = REVIEW_REQUIRED

        reason = (
            "At least one material claim increases "
            "certainty, causality, scope, or authority "
            "beyond the approved evidence."
        )

    return {
        "decision": decision,
        "reason": reason,
        "claim_count": len(
            results
        ),
        "material_claim_count": len(
            material_results
        ),
        "claim_results": results,
        "overstatement_count": sum(
            1
            for result
            in results
            if result[
                "status"
            ]
            == OVERSTATEMENT_DETECTED
        ),
        "safety_summary": {
            "uncertainty_preservation_checked": True,
            "causal_authority_checked": True,
            "scope_authority_checked": True,
            "mandatory_authority_checked": True,
            "policy_authority_checked": True,
            "governance_upgrade_performed": False,
        },
    }