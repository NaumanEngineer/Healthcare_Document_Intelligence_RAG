from __future__ import annotations

import pytest

from src.generation.answer_contract import (
    ABSTAIN,
    AUTO_ANSWER,
    REVIEW_REQUIRED,
    RESPONSE_TYPE_ABSTENTION,
    RESPONSE_TYPE_ANSWER,
    RESPONSE_TYPE_REVIEW,
    build_answer_contract,
)


def _packet(
    decision: str,
    **governance_overrides,
) -> dict:
    governance = {
        "decision": decision,
    }

    governance.update(
        governance_overrides
    )

    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance": governance,
    }


def test_auto_answer_contract():
    contract = build_answer_contract(
        _packet(
            AUTO_ANSWER
        )
    )

    assert (
        contract["governance_decision"]
        == AUTO_ANSWER
    )

    assert (
        contract["response_type"]
        == RESPONSE_TYPE_ANSWER
    )

    assert (
        contract["requires_human_review"]
        is False
    )

    assert (
        contract["may_generate_answer"]
        is True
    )

    assert (
        contract[
            "may_issue_authoritative_recommendation"
        ]
        is True
    )

    assert (
        contract["must_preserve_citations"]
        is True
    )


def test_review_required_contract():
    contract = build_answer_contract(
        _packet(
            REVIEW_REQUIRED
        )
    )

    assert (
        contract["governance_decision"]
        == REVIEW_REQUIRED
    )

    assert (
        contract["response_type"]
        == RESPONSE_TYPE_REVIEW
    )

    assert (
        contract["requires_human_review"]
        is True
    )

    assert (
        contract["may_generate_answer"]
        is False
    )

    assert (
        contract[
            "may_issue_authoritative_recommendation"
        ]
        is False
    )

    assert (
        contract["must_preserve_citations"]
        is True
    )


def test_abstain_contract():
    contract = build_answer_contract(
        _packet(
            ABSTAIN
        )
    )

    assert (
        contract["governance_decision"]
        == ABSTAIN
    )

    assert (
        contract["response_type"]
        == RESPONSE_TYPE_ABSTENTION
    )

    assert (
        contract["requires_human_review"]
        is False
    )

    assert (
        contract["may_generate_answer"]
        is False
    )

    assert (
        contract[
            "may_issue_authoritative_recommendation"
        ]
        is False
    )

    assert (
        contract["must_preserve_citations"]
        is False
    )


def test_unsupported_governance_fails_closed():
    with pytest.raises(
        ValueError,
        match="Unsupported governance decision",
    ):
        build_answer_contract(
            _packet(
                "UNKNOWN_STATE"
            )
        )


def test_missing_governance_fails_closed():
    with pytest.raises(
        TypeError,
        match="evidence_packet.governance",
    ):
        build_answer_contract(
            {
                "packet_id": (
                    "EVIDENCE_PACKET::TEST"
                ),
            }
        )


def test_missing_packet_id_fails_closed():
    with pytest.raises(
        TypeError,
        match="evidence_packet.packet_id",
    ):
        build_answer_contract(
            {
                "governance": {
                    "decision": (
                        AUTO_ANSWER
                    ),
                }
            }
        )


def test_blank_packet_id_fails_closed():
    with pytest.raises(
        ValueError,
        match="must not be blank",
    ):
        build_answer_contract(
            {
                "packet_id": "   ",
                "governance": {
                    "decision": (
                        AUTO_ANSWER
                    ),
                },
            }
        )


def test_review_required_cannot_issue_authoritative_recommendation():
    contract = build_answer_contract(
        _packet(
            REVIEW_REQUIRED
        )
    )

    assert (
        contract[
            "may_issue_authoritative_recommendation"
        ]
        is False
    )


def test_abstain_cannot_generate_answer():
    contract = build_answer_contract(
        _packet(
            ABSTAIN
        )
    )

    assert (
        contract["may_generate_answer"]
        is False
    )


def test_auto_answer_sections_are_manager_facing():
    contract = build_answer_contract(
        _packet(
            AUTO_ANSWER
        )
    )

    assert (
        contract["response_sections"]
        == [
            "management_summary",
            "evidence_based_explanation",
            "operational_implication",
            "caveats",
            "sources",
        ]
    )


def test_review_sections_require_human_review():
    contract = build_answer_contract(
        _packet(
            REVIEW_REQUIRED
        )
    )

    assert (
        "why_human_review_is_required"
        in contract[
            "response_sections"
        ]
    )


def test_abstain_sections_include_missing_evidence():
    contract = build_answer_contract(
        _packet(
            ABSTAIN
        )
    )

    assert (
        "missing_evidence"
        in contract[
            "response_sections"
        ]
    )


def test_abstain_cannot_claim_generation_permission():
    with pytest.raises(
        ValueError,
        match=(
            "ABSTAIN cannot permit "
            "answer generation"
        ),
    ):
        build_answer_contract(
            _packet(
                ABSTAIN,
                may_generate_answer=True,
            )
        )


def test_review_required_cannot_claim_generation_permission():
    with pytest.raises(
        ValueError,
        match=(
            "REVIEW_REQUIRED cannot permit "
            "answer generation"
        ),
    ):
        build_answer_contract(
            _packet(
                REVIEW_REQUIRED,
                may_generate_answer=True,
            )
        )


def test_auto_answer_cannot_explicitly_prohibit_generation():
    with pytest.raises(
        ValueError,
        match=(
            "AUTO_ANSWER cannot explicitly "
            "prohibit generation"
        ),
    ):
        build_answer_contract(
            _packet(
                AUTO_ANSWER,
                may_generate_answer=False,
            )
        )


def test_review_required_cannot_disable_human_review():
    with pytest.raises(
        ValueError,
        match=(
            "REVIEW_REQUIRED cannot explicitly "
            "disable human review"
        ),
    ):
        build_answer_contract(
            _packet(
                REVIEW_REQUIRED,
                requires_human_review=False,
            )
        )


def test_abstain_cannot_require_human_review_in_answer_contract():
    with pytest.raises(
        ValueError,
        match=(
            "ABSTAIN cannot require human "
            "review in the answer contract"
        ),
    ):
        build_answer_contract(
            _packet(
                ABSTAIN,
                requires_human_review=True,
            )
        )