from src.evaluation.overstatement_audit import (
    ABSTAIN,
    NOT_APPLICABLE,
    OVERSTATEMENT_DETECTED,
    PASS,
    PRESERVED,
    REVIEW_REQUIRED,
    audit_answer_overstatement,
    audit_claim_overstatement,
)


def _evidence(
    text,
):
    return [
        {
            "document_id": "DOC-A",
            "chunk_id": "DOC-A-C001",
            "status": "Active",
            "text": text,
        }
    ]


def test_uncertainty_preserved_passes():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Staffing pressure may contribute "
            "to operational delays."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Staffing pressure may contribute "
            "to operational delays."
        ),
    )

    assert result[
        "status"
    ] == PRESERVED


def test_hidden_uncertainty_is_detected():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Staffing pressure contributes "
            "to operational delays."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Staffing pressure may contribute "
            "to operational delays."
        ),
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert (
        "UNCERTAINTY_REMOVED"
        in result[
            "overstatement_types"
        ]
    )


def test_causal_increase_is_detected():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Staffing pressure causes "
            "operational delays."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Staffing pressure may be associated "
            "with operational delays."
        ),
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert (
        "CAUSALITY_INCREASED"
        in result[
            "overstatement_types"
        ]
    )


def test_supported_causal_wording_is_preserved():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The interruption causes "
            "the system to stop."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "The interruption causes "
            "the system to stop."
        ),
    )

    assert result[
        "status"
    ] == PRESERVED


def test_universal_scope_increase_is_detected():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "All services reported "
            "operational pressure."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Some services reported "
            "operational pressure."
        ),
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert (
        "UNIVERSALITY_INCREASED"
        in result[
            "overstatement_types"
        ]
    )


def test_supported_universal_scope_is_preserved():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "All participating services "
            "reported pressure."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "All participating services "
            "reported pressure."
        ),
    )

    assert result[
        "status"
    ] == PRESERVED


def test_advisory_to_mandatory_is_detected():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Teams must review "
            "staffing pressure."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Teams should consider reviewing "
            "staffing pressure."
        ),
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert (
        "MANDATORY_AUTHORITY_INCREASED"
        in result[
            "overstatement_types"
        ]
    )


def test_supported_mandatory_wording_is_preserved():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Teams must review "
            "staffing pressure."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Teams must review "
            "staffing pressure."
        ),
    )

    assert result[
        "status"
    ] == PRESERVED


def test_unsupported_policy_authority_is_detected():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The approved policy requires "
            "daily escalation review."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        _evidence(
            "Guidance recommends "
            "daily escalation review."
        ),
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert (
        "POLICY_AUTHORITY_INCREASED"
        in result[
            "overstatement_types"
        ]
    )


def test_non_substantive_claim_is_not_applicable():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Human review is required before use."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        [],
        material=False,
    )

    assert result[
        "status"
    ] == NOT_APPLICABLE


def test_no_supporting_evidence_fails_closed():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Staffing pressure causes delays."
        ),
    }

    result = audit_claim_overstatement(
        claim,
        [],
    )

    assert result[
        "status"
    ] == OVERSTATEMENT_DETECTED

    assert result[
        "overstatement_types"
    ] == [
        "NO_SUPPORTING_EVIDENCE"
    ]


def test_answer_passes_when_authority_is_preserved():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure may contribute "
                "to delays."
            ),
        }
    ]

    result = audit_answer_overstatement(
        claims,
        {
            "C1": _evidence(
                "Staffing pressure may contribute "
                "to delays."
            )
        },
    )

    assert result[
        "decision"
    ] == PASS


def test_answer_requires_review_for_hidden_uncertainty():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure contributes "
                "to delays."
            ),
        }
    ]

    result = audit_answer_overstatement(
        claims,
        {
            "C1": _evidence(
                "Staffing pressure may contribute "
                "to delays."
            )
        },
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_answer_requires_review_for_causal_overstatement():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure causes delays."
            ),
        }
    ]

    result = audit_answer_overstatement(
        claims,
        {
            "C1": _evidence(
                "Staffing pressure may be associated "
                "with delays."
            )
        },
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED


def test_abstention_without_material_claims_is_preserved():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "There is insufficient evidence "
                "to answer safely."
            ),
        }
    ]

    result = audit_answer_overstatement(
        claims,
        {},
        non_substantive_claim_ids=[
            "C1"
        ],
        upstream_governance_decision=(
            "ABSTAIN"
        ),
    )

    assert result[
        "decision"
    ] == ABSTAIN


def test_duplicate_claim_id_fails_closed():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure may "
                "contribute to delays."
            ),
        },
        {
            "claim_id": "C1",
            "claim_text": (
                "Staffing pressure may "
                "contribute to delays."
            ),
        },
    ]

    try:
        audit_answer_overstatement(
            claims,
            {
                "C1": _evidence(
                    "Staffing pressure may "
                    "contribute to delays."
                )
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate claim IDs "
            "to fail closed."
        )