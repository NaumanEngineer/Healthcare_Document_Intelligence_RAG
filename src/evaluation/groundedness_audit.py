"""Deterministic groundedness and unsupported-claim auditing.

Week 25 Day 4.

This module evaluates whether material claim wording remains inside the
approved evidence boundary.

It complements citation verification.

A valid citation does not automatically make a claim grounded.

Claim-level statuses:

- GROUNDED
- PARTIALLY_GROUNDED
- UNGROUNDED
- NOT_APPLICABLE

The module reuses the existing high-risk claim guard so unsupported:

- numbers;
- mandatory wording;
- actors;
- actions;
- prohibitions;
- negation changes

remain fail-closed.

It also performs deterministic lexical support checks.

This module does not use semantic similarity as proof.
"""

from __future__ import annotations

import re
from typing import Any

from src.governance.high_risk_claim_guard import (
    detect_high_risk_mismatch,
)


GROUNDED = "GROUNDED"
PARTIALLY_GROUNDED = "PARTIALLY_GROUNDED"
UNGROUNDED = "UNGROUNDED"
NOT_APPLICABLE = "NOT_APPLICABLE"

PASS = "PASS"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
ABSTAIN = "ABSTAIN"


DEFAULT_GROUNDED_THRESHOLD = 0.60


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
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "must",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
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
    """Normalise text for deterministic lexical comparison."""

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def _material_terms(
    text: str,
) -> set[str]:
    """Extract simple material terms."""

    terms = set()

    for term in _normalise(
        text
    ).split():
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


def _combine_evidence_text(
    evidence_items: list[dict[str, Any]],
) -> str:
    """Combine approved evidence into deterministic audit text."""

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


def _support_ratio(
    claim_text: str,
    evidence_text: str,
) -> tuple[
    float,
    list[str],
    list[str],
]:
    """Calculate lexical material-term coverage."""

    claim_terms = _material_terms(
        claim_text
    )

    evidence_terms = _material_terms(
        evidence_text
    )

    if not claim_terms:
        return (
            0.0,
            [],
            [],
        )

    matched_terms = sorted(
        claim_terms
        & evidence_terms
    )

    missing_terms = sorted(
        claim_terms
        - evidence_terms
    )

    ratio = (
        len(
            matched_terms
        )
        / len(
            claim_terms
        )
    )

    return (
        ratio,
        matched_terms,
        missing_terms,
    )


def audit_claim_groundedness(
    claim: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    *,
    material: bool = True,
    grounded_threshold: float = (
        DEFAULT_GROUNDED_THRESHOLD
    ),
) -> dict[str, Any]:
    """Audit one claim against its approved evidence set."""

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
        grounded_threshold,
        (
            int,
            float,
        ),
    ):
        raise TypeError(
            "grounded_threshold must be numeric"
        )

    if not (
        0.0
        <= float(
            grounded_threshold
        )
        <= 1.0
    ):
        raise ValueError(
            "grounded_threshold must be between 0 and 1"
        )

    if not material:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": False,
            "status": NOT_APPLICABLE,
            "reason": (
                "Claim is non-substantive and does not "
                "require evidence groundedness auditing."
            ),
            "support_ratio": None,
            "matched_terms": [],
            "missing_terms": [],
            "high_risk_guard_triggered": False,
            "high_risk_reasons": [],
        }

    if not evidence_items:
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": UNGROUNDED,
            "reason": (
                "Material claim has no approved evidence "
                "available for groundedness assessment."
            ),
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "high_risk_guard_triggered": False,
            "high_risk_reasons": [],
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
            "status": UNGROUNDED,
            "reason": (
                "Approved evidence contains no usable text."
            ),
            "support_ratio": 0.0,
            "matched_terms": [],
            "missing_terms": sorted(
                _material_terms(
                    claim_text
                )
            ),
            "high_risk_guard_triggered": False,
            "high_risk_reasons": [],
        }

    (
        support_ratio,
        matched_terms,
        missing_terms,
    ) = _support_ratio(
        claim_text,
        evidence_text,
    )

    guard = (
        detect_high_risk_mismatch(
            claim_text,
            evidence_text,
        )
    )

    if guard[
        "guard_triggered"
    ]:
        status = (
            PARTIALLY_GROUNDED
            if support_ratio > 0
            else UNGROUNDED
        )

        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": status,
            "reason": (
                "Claim contains one or more material "
                "high-risk elements that are not justified "
                "by the approved evidence."
            ),
            "support_ratio": round(
                support_ratio,
                4,
            ),
            "matched_terms": (
                matched_terms
            ),
            "missing_terms": (
                missing_terms
            ),
            "high_risk_guard_triggered": True,
            "high_risk_reasons": list(
                guard[
                    "reasons"
                ]
            ),
        }

    if (
        support_ratio
        >= grounded_threshold
    ):
        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "material": True,
            "status": GROUNDED,
            "reason": (
                "Claim remains inside the approved "
                "evidence boundary."
            ),
            "support_ratio": round(
                support_ratio,
                4,
            ),
            "matched_terms": (
                matched_terms
            ),
            "missing_terms": (
                missing_terms
            ),
            "high_risk_guard_triggered": False,
            "high_risk_reasons": [],
        }

    if support_ratio > 0:
        status = (
            PARTIALLY_GROUNDED
        )

        reason = (
            "Claim shares some material content with "
            "the approved evidence but includes material "
            "content not sufficiently supported."
        )

    else:
        status = UNGROUNDED

        reason = (
            "Claim cannot be materially grounded in "
            "the approved evidence."
        )

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "material": True,
        "status": status,
        "reason": reason,
        "support_ratio": round(
            support_ratio,
            4,
        ),
        "matched_terms": (
            matched_terms
        ),
        "missing_terms": (
            missing_terms
        ),
        "high_risk_guard_triggered": False,
        "high_risk_reasons": [],
    }


def audit_answer_groundedness(
    claims: list[dict[str, Any]],
    evidence_by_claim_id: dict[
        str,
        list[dict[str, Any]],
    ],
    *,
    non_substantive_claim_ids: list[str] | None = None,
    upstream_governance_decision: str | None = None,
    grounded_threshold: float = (
        DEFAULT_GROUNDED_THRESHOLD
    ),
) -> dict[str, Any]:
    """Audit groundedness across all answer claims."""

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
            audit_claim_groundedness(
                claim,
                evidence_items,
                material=(
                    claim_id
                    not in non_substantive_set
                ),
                grounded_threshold=(
                    grounded_threshold
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
            "and no material claims require groundedness auditing."
        )

    elif not material_results:
        decision = PASS

        reason = (
            "No material claims require groundedness auditing."
        )

    elif all(
        result[
            "status"
        ]
        == GROUNDED
        for result
        in material_results
    ):
        decision = PASS

        reason = (
            "Every material claim is grounded "
            "in approved evidence."
        )

    else:
        decision = REVIEW_REQUIRED

        reason = (
            "At least one material claim is only partially "
            "grounded or ungrounded."
        )

    status_counts = {
        status: sum(
            1
            for result
            in results
            if result[
                "status"
            ]
            == status
        )
        for status
        in (
            GROUNDED,
            PARTIALLY_GROUNDED,
            UNGROUNDED,
            NOT_APPLICABLE,
        )
    }

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
        "status_counts": (
            status_counts
        ),
        "safety_summary": {
            "evidence_bounded": True,
            "semantic_override_used": False,
            "high_risk_guard_reused": True,
            "governance_upgrade_performed": False,
        },
    }