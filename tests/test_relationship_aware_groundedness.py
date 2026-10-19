"""Tests for Week 26 relationship-aware groundedness."""

from __future__ import annotations

from src.evaluation.relationship_aware_groundedness import (
    COMPOSITION_ALLOWED,
    COMPOSITION_BLOCKED,
    COMPOSITION_REVIEW_REQUIRED,
    CONFLICT_BLOCKED,
    COMPLEMENTARY_EVIDENCE,
    DIRECT_SUPPORT,
    EXPLICIT_CONFLICT,
    GROUNDED_MULTI_SOURCE,
    GROUNDED_SINGLE_SOURCE,
    RELATIONSHIP_UNVERIFIED,
    SAME_DOCUMENT_CONTEXT,
    UNRELATED,
    UNKNOWN_RELATIONSHIP,
    UNGROUNDED,
    assess_relationship_aware_groundedness,
    assess_source_support,
)


def _evidence(
    *,
    evidence_id: str,
    text: str,
    status: str = "active",
) -> dict:
    return {
        "evidence_id": evidence_id,
        "text": text,
        "status": status,
    }


def test_single_source_direct_support_is_grounded():
    evidence = _evidence(
        evidence_id="E1",
        text="Bed occupancy is high.",
    )

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Bed occupancy is high.",
        evidence_items=[
            evidence,
        ],
        relationship=SAME_DOCUMENT_CONTEXT,
    )

    assert (
        result["groundedness_status"]
        == GROUNDED_SINGLE_SOURCE
    )

    assert (
        result["source_level_results"][0]["support_status"]
        == DIRECT_SUPPORT
    )


def test_frankenstein_support_is_relationship_unverified():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text=(
                "Escalation may be considered "
                "if operational pressure continues."
            ),
        ),
        _evidence(
            evidence_id="E2",
            text=(
                "Elective activity is currently "
                "under pressure."
            ),
        ),
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text=(
            "Elective activity must be cancelled immediately."
        ),
        evidence_items=evidence_items,
        relationship=UNRELATED,
    )

    assert (
        result["groundedness_status"]
        == RELATIONSHIP_UNVERIFIED
    )

    assert (
        result["relationship_result"]
        == COMPOSITION_REVIEW_REQUIRED
    )

    assert result[
        "composition_allowed"
    ] is False


def test_unknown_relationship_cannot_create_multi_source_support():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text="Operational pressure is increasing.",
        ),
        _evidence(
            evidence_id="E2",
            text="Escalation may be considered.",
        ),
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Escalation may be considered.",
        evidence_items=evidence_items,
        relationship=UNKNOWN_RELATIONSHIP,
    )

    assert (
        result["groundedness_status"]
        == RELATIONSHIP_UNVERIFIED
    )

    assert (
        result["relationship_result"]
        == COMPOSITION_REVIEW_REQUIRED
    )


def test_legitimate_complementary_evidence_can_ground_multi_source_claim():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text=(
                "Policy A applies to all acute hospital sites."
            ),
        ),
        _evidence(
            evidence_id="E2",
            text=(
                "Site X is classified as an acute hospital site."
            ),
        ),
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text=(
            "Policy A applies to acute hospital sites."
        ),
        evidence_items=evidence_items,
        relationship=COMPLEMENTARY_EVIDENCE,
    )

    assert (
        result["groundedness_status"]
        == GROUNDED_MULTI_SOURCE
    )

    assert (
        result["relationship_result"]
        == COMPOSITION_ALLOWED
    )

    assert result[
        "composition_allowed"
    ] is True


def test_same_document_context_allows_multi_source_composition():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text="Bed occupancy is high.",
        ),
        _evidence(
            evidence_id="E2",
            text="Bed occupancy remains high today.",
        ),
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Bed occupancy is high.",
        evidence_items=evidence_items,
        relationship=SAME_DOCUMENT_CONTEXT,
    )

    assert (
        result["groundedness_status"]
        == GROUNDED_MULTI_SOURCE
    )

    assert result[
        "composition_allowed"
    ] is True


def test_explicit_conflict_blocks_composition():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text="Escalation may be required.",
        ),
        _evidence(
            evidence_id="E2",
            text="Escalation is not recommended.",
        ),
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text=(
            "Evidence generally supports escalation."
        ),
        evidence_items=evidence_items,
        relationship=EXPLICIT_CONFLICT,
    )

    assert (
        result["groundedness_status"]
        == CONFLICT_BLOCKED
    )

    assert (
        result["relationship_result"]
        == COMPOSITION_BLOCKED
    )

    assert result[
        "composition_allowed"
    ] is False

    assert set(
        result[
            "contradictory_components"
        ]
    ) == {
        "E1",
        "E2",
    }


def test_inactive_evidence_cannot_ground_current_claim():
    evidence_items = [
        _evidence(
            evidence_id="E1",
            text="Escalation must begin.",
            status="superseded",
        )
    ]

    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Escalation must begin.",
        evidence_items=evidence_items,
        relationship=SAME_DOCUMENT_CONTEXT,
    )

    assert (
        result["groundedness_status"]
        == UNGROUNDED
    )

    assert result[
        "lifecycle_valid"
    ] is False


def test_no_evidence_is_ungrounded():
    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Escalation must begin.",
        evidence_items=[],
        relationship=None,
    )

    assert (
        result["groundedness_status"]
        == UNGROUNDED
    )


def test_non_material_claim_is_not_applicable():
    result = assess_relationship_aware_groundedness(
        claim_id="C1",
        claim_text="Background information.",
        evidence_items=[],
        relationship=None,
        material=False,
    )

    assert (
        result["groundedness_status"]
        == "NOT_APPLICABLE"
    )

    assert result[
        "material"
    ] is False


def test_source_support_requires_active_lifecycle():
    evidence = _evidence(
        evidence_id="E1",
        text="Escalation is required.",
        status="archived",
    )

    result = assess_source_support(
        "Escalation is required.",
        evidence,
    )

    assert (
        result.support_status
        == "INVALID_SOURCE"
    )

    assert result.lifecycle_valid is False