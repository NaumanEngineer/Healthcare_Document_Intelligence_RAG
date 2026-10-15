"""Answer-level hallucination resistance.

Week 25 Day 4.

This module combines:

- deterministic groundedness auditing;
- overstatement and uncertainty-preservation auditing;
- upstream governance preservation.

It protects against an answer being citation-valid but still unsafe because it:

- contains unsupported material content;
- increases certainty or authority;
- turns REVIEW_REQUIRED into operational instruction;
- places substantive advice inside ABSTAIN.

Safety principle:

    The answer may never become more authoritative than its evidence or
    governance state.
"""

from __future__ import annotations

import re
from typing import Any

from src.evaluation.groundedness_audit import (
    GROUNDED,
    NOT_APPLICABLE as GROUNDEDNESS_NOT_APPLICABLE,
    PASS as GROUNDEDNESS_PASS,
    audit_answer_groundedness,
)
from src.evaluation.overstatement_audit import (
    NOT_APPLICABLE as OVERSTATEMENT_NOT_APPLICABLE,
    PASS as OVERSTATEMENT_PASS,
    PRESERVED,
    audit_answer_overstatement,
)


CLEAR = "CLEAR"
HALLUCINATION_RISK = "HALLUCINATION_RISK"
REVIEW_AUTHORITY_INCREASE = "REVIEW_AUTHORITY_INCREASE"
ABSTENTION_VIOLATION = "ABSTENTION_VIOLATION"
NOT_APPLICABLE = "NOT_APPLICABLE"

PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


VALID_UPSTREAM_GOVERNANCE = {
    "AUTO_ANSWER",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}


MANDATORY_TERMS = {
    "must",
    "shall",
    "mandatory",
    "required",
    "requires",
    "immediately",
}


PROHIBITION_PHRASES = {
    "must not",
    "cannot",
    "prohibited",
    "forbidden",
    "never",
}


OPERATIONAL_ACTION_TERMS = {
    "cancel",
    "cancelled",
    "suspend",
    "suspended",
    "redeploy",
    "redeployed",
    "restore",
    "restored",
    "open",
    "opened",
    "close",
    "closed",
    "evacuate",
    "evacuated",
    "evacuation",
    "transfer",
    "transferred",
    "discharge",
    "discharged",
    "restrict",
    "restricted",
    "stop",
    "stopped",
}


POLICY_AUTHORITY_PHRASES = {
    "policy requires",
    "policy mandates",
    "approved policy requires",
    "approved policy mandates",
    "official policy requires",
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
    """Normalise text for deterministic governance checks."""

    return " ".join(
        re.sub(
            r"[^a-z0-9]+",
            " ",
            text.lower(),
        ).split()
    )


def _contains_token(
    text: str,
    terms: set[str],
) -> bool:
    """Check whether normalised text contains one of the terms."""

    tokens = set(
        _normalise(
            text
        ).split()
    )

    return bool(
        tokens
        & terms
    )


def _contains_phrase(
    text: str,
    phrases: set[str],
) -> bool:
    """Check deterministic phrase presence."""

    normalised = _normalise(
        text
    )

    return any(
        _normalise(
            phrase
        )
        in normalised
        for phrase
        in phrases
    )


def _claim_is_directive(
    claim_text: str,
) -> tuple[
    bool,
    list[str],
]:
    """Detect authority-increasing operational wording.

    REVIEW_REQUIRED may communicate evidence and uncertainty.

    It must not quietly become an authoritative instruction.
    """

    reasons = []

    if _contains_token(
        claim_text,
        MANDATORY_TERMS,
    ):
        reasons.append(
            "MANDATORY_LANGUAGE"
        )

    if _contains_phrase(
        claim_text,
        PROHIBITION_PHRASES,
    ):
        reasons.append(
            "PROHIBITION_LANGUAGE"
        )

    if _contains_token(
        claim_text,
        OPERATIONAL_ACTION_TERMS,
    ):
        reasons.append(
            "OPERATIONAL_ACTION"
        )

    if _contains_phrase(
        claim_text,
        POLICY_AUTHORITY_PHRASES,
    ):
        reasons.append(
            "POLICY_AUTHORITY"
        )

    return (
        bool(
            reasons
        ),
        reasons,
    )


def _build_result_lookup(
    results: list[dict[str, Any]],
) -> dict[
    str,
    dict[str, Any],
]:
    """Build claim-result lookup and fail closed on duplicates."""

    lookup = {}

    for result in results:
        result = _require_mapping(
            result,
            "audit result",
        )

        claim_id = _require_non_empty_string(
            result.get(
                "claim_id"
            ),
            "audit result claim_id",
        )

        if claim_id in lookup:
            raise ValueError(
                "Duplicate audit result for claim ID: "
                f"{claim_id}"
            )

        lookup[
            claim_id
        ] = result

    return lookup


def audit_answer_hallucination_resistance(
    claims: list[dict[str, Any]],
    evidence_by_claim_id: dict[
        str,
        list[dict[str, Any]],
    ],
    *,
    non_substantive_claim_ids: list[str] | None = None,
    upstream_governance_decision: str,
) -> dict[str, Any]:
    """Run answer-level hallucination-resistance assurance.

    Governance is never upgraded.

    AUTO_ANSWER:
        PASS is possible when every material claim is grounded and authority is
        preserved.

    REVIEW_REQUIRED:
        Final decision remains REVIEW_REQUIRED even if every claim is safe.
        Directive operational wording is additionally flagged as an authority
        increase.

    ABSTAIN:
        Final decision always remains ABSTAIN.
        Any material claim creates an abstention violation.
    """

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

    upstream_governance_decision = (
        _require_non_empty_string(
            upstream_governance_decision,
            "upstream_governance_decision",
        )
    )

    if (
        upstream_governance_decision
        not in VALID_UPSTREAM_GOVERNANCE
    ):
        raise ValueError(
            "Unsupported upstream governance decision: "
            f"{upstream_governance_decision}"
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

    seen_claim_ids = set()

    validated_claims = []

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

        claim_text = _require_non_empty_string(
            claim.get(
                "claim_text"
            ),
            "claim.claim_text",
        )

        if claim_id in seen_claim_ids:
            raise ValueError(
                "Duplicate claim ID: "
                f"{claim_id}"
            )

        seen_claim_ids.add(
            claim_id
        )

        validated_claims.append(
            {
                **claim,
                "claim_id": claim_id,
                "claim_text": claim_text,
            }
        )

    groundedness = (
        audit_answer_groundedness(
            validated_claims,
            evidence_by_claim_id,
            non_substantive_claim_ids=(
                list(
                    non_substantive_set
                )
            ),
            upstream_governance_decision=(
                upstream_governance_decision
            ),
        )
    )

    overstatement = (
        audit_answer_overstatement(
            validated_claims,
            evidence_by_claim_id,
            non_substantive_claim_ids=(
                list(
                    non_substantive_set
                )
            ),
            upstream_governance_decision=(
                upstream_governance_decision
            ),
        )
    )

    groundedness_lookup = (
        _build_result_lookup(
            groundedness[
                "claim_results"
            ]
        )
    )

    overstatement_lookup = (
        _build_result_lookup(
            overstatement[
                "claim_results"
            ]
        )
    )

    claim_results = []

    abstention_violation = False

    review_authority_increase = False

    for claim in validated_claims:
        claim_id = claim[
            "claim_id"
        ]

        claim_text = claim[
            "claim_text"
        ]

        material = (
            claim_id
            not in non_substantive_set
        )

        groundedness_result = (
            groundedness_lookup[
                claim_id
            ]
        )

        overstatement_result = (
            overstatement_lookup[
                claim_id
            ]
        )

        governance_flags = []

        if (
            upstream_governance_decision
            == "ABSTAIN"
            and material
        ):
            governance_flags.append(
                ABSTENTION_VIOLATION
            )

            abstention_violation = True

        if (
            upstream_governance_decision
            == "REVIEW_REQUIRED"
            and material
        ):
            (
                directive,
                directive_reasons,
            ) = _claim_is_directive(
                claim_text
            )

            if directive:
                governance_flags.append(
                    REVIEW_AUTHORITY_INCREASE
                )

                governance_flags.extend(
                    directive_reasons
                )

                review_authority_increase = True

        if not material:
            combined_status = (
                NOT_APPLICABLE
            )

        elif (
            groundedness_result[
                "status"
            ]
            == GROUNDED
            and overstatement_result[
                "status"
            ]
            == PRESERVED
            and not governance_flags
        ):
            combined_status = CLEAR

        elif (
            ABSTENTION_VIOLATION
            in governance_flags
        ):
            combined_status = (
                ABSTENTION_VIOLATION
            )

        elif (
            REVIEW_AUTHORITY_INCREASE
            in governance_flags
        ):
            combined_status = (
                REVIEW_AUTHORITY_INCREASE
            )

        else:
            combined_status = (
                HALLUCINATION_RISK
            )

        claim_results.append(
            {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "material": material,
                "status": (
                    combined_status
                ),
                "groundedness_status": (
                    groundedness_result[
                        "status"
                    ]
                ),
                "overstatement_status": (
                    overstatement_result[
                        "status"
                    ]
                ),
                "governance_flags": (
                    governance_flags
                ),
            }
        )

    material_claim_results = [
        result
        for result
        in claim_results
        if result[
            "material"
        ]
    ]

    hallucination_risk_count = sum(
        1
        for result
        in claim_results
        if result[
            "status"
        ]
        == HALLUCINATION_RISK
    )

    if (
        upstream_governance_decision
        == "ABSTAIN"
    ):
        final_decision = ABSTAIN

        if abstention_violation:
            final_reason = (
                "ABSTAIN was preserved, but substantive "
                "material content was detected inside the "
                "abstention response."
            )

        else:
            final_reason = (
                "ABSTAIN was preserved and no substantive "
                "answer content escaped the governance boundary."
            )

    elif (
        upstream_governance_decision
        == "REVIEW_REQUIRED"
    ):
        final_decision = (
            REVIEW_REQUIRED
        )

        if review_authority_increase:
            final_reason = (
                "REVIEW_REQUIRED was preserved and "
                "authority-increasing operational wording "
                "was detected."
            )

        elif hallucination_risk_count:
            final_reason = (
                "REVIEW_REQUIRED was preserved and at "
                "least one material claim contains a "
                "groundedness or overstatement risk."
            )

        else:
            final_reason = (
                "REVIEW_REQUIRED was preserved without "
                "additional hallucination or authority-increase risk."
            )

    elif (
        groundedness[
            "decision"
        ]
        == GROUNDEDNESS_PASS
        and overstatement[
            "decision"
        ]
        == OVERSTATEMENT_PASS
        and not hallucination_risk_count
        and not review_authority_increase
        and not abstention_violation
    ):
        final_decision = PASS

        final_reason = (
            "All material claims are grounded, preserve "
            "evidential authority, and remain inside "
            "the governance boundary."
        )

    else:
        final_decision = (
            REVIEW_REQUIRED
        )

        final_reason = (
            "At least one material claim presents a "
            "groundedness, overstatement, or governance risk."
        )

    return {
        "decision": final_decision,
        "reason": final_reason,
        "upstream_governance_decision": (
            upstream_governance_decision
        ),
        "claim_count": len(
            claim_results
        ),
        "material_claim_count": len(
            material_claim_results
        ),
        "claim_results": (
            claim_results
        ),
        "groundedness_audit": (
            groundedness
        ),
        "overstatement_audit": (
            overstatement
        ),
        "hallucination_risk_count": (
            hallucination_risk_count
        ),
        "review_authority_increase_detected": (
            review_authority_increase
        ),
        "abstention_violation_detected": (
            abstention_violation
        ),
        "safety_summary": {
            "groundedness_checked": True,
            "overstatement_checked": True,
            "review_authority_checked": True,
            "abstention_boundary_checked": True,
            "governance_upgrade_performed": False,
            "external_knowledge_used": False,
        },
    }