from src.governance.citation_verification import (
    verify_answer_citations,
    verify_claim_citation,
)


def test_high_lexical_overlap_cannot_bypass_unsupported_action():
    claim = {
        "claim_id": "W25-C008-C1",
        "claim_text": (
            "Severe weather preparation should begin "
            "before disruption and all elective activity "
            "must be cancelled."
        ),
        "citation": {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-V1.0-P001-C001",
        },
    }

    evidence = {
        "document_id": "DOC-009",
        "chunk_id": "DOC-009-V1.0-P001-C001",
        "status": "Active",
        "title": "Severe Weather Operational Plan",
        "text": (
            "Severe weather preparation should begin "
            "before disruption affects service delivery."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] == "PARTIALLY_SUPPORTED"

    assert (
        result["high_risk_guard"]["guard_triggered"]
        is True
    )

    assert (
        "unsupported_action"
        in result["high_risk_guard"]["reasons"]
    )

    assert (
        "unsupported_mandatory_wording"
        in result["high_risk_guard"]["reasons"]
    )


def test_authority_inflation_cannot_bypass_guard():
    claim = {
        "claim_id": "W25-C009-C1",
        "claim_text": (
            "Operational escalation must be initiated "
            "immediately when pressure is identified."
        ),
        "citation": {
            "document_id": "DOC-001",
            "chunk_id": "DOC-001-V1.0-P002-C001",
        },
    }

    evidence = {
        "document_id": "DOC-001",
        "chunk_id": "DOC-001-V1.0-P002-C001",
        "status": "Active",
        "title": "Operational Escalation Policy",
        "text": (
            "Operational escalation may be considered "
            "where sustained pressure is identified."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] == "PARTIALLY_SUPPORTED"

    assert (
        result["high_risk_guard"]["guard_triggered"]
        is True
    )

    assert (
        "unsupported_mandatory_wording"
        in result["high_risk_guard"]["reasons"]
    )


def test_high_risk_claim_forces_answer_review():
    claims = [
        {
            "claim_id": "W25-C009-C1",
            "claim_text": (
                "Operational escalation must be initiated "
                "immediately when pressure is identified."
            ),
            "citation": {
                "document_id": "DOC-001",
                "chunk_id": "DOC-001-V1.0-P002-C001",
            },
        }
    ]

    evidence_items = [
        {
            "document_id": "DOC-001",
            "chunk_id": "DOC-001-V1.0-P002-C001",
            "status": "Active",
            "title": "Operational Escalation Policy",
            "text": (
                "Operational escalation may be considered "
                "where sustained pressure is identified."
            ),
        }
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
    )

    assert result["decision"] == "REVIEW_REQUIRED"

    assert (
        result["claim_results"][0]["status"]
        == "PARTIALLY_SUPPORTED"
    )


def test_safe_lexical_match_still_passes():
    claim = {
        "claim_id": "SAFE-C1",
        "claim_text": (
            "Ambulance handover delays should be monitored."
        ),
        "citation": {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-01",
        },
    }

    evidence = {
        "document_id": "DOC-008",
        "chunk_id": "DOC-008-01",
        "status": "Active",
        "title": "Ambulance Handover Escalation Guidance",
        "text": (
            "Ambulance handover delays should be monitored."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] == "SUPPORTED"

    assert (
        result["verification_method"]
        == "guarded_lexical_support"
    )


def test_unsupported_number_blocks_supported_decision():
    claim = {
        "claim_id": "NUMERIC-C1",
        "claim_text": (
            "Escalation must begin when bed occupancy "
            "reaches 95 percent."
        ),
        "citation": {
            "document_id": "DOC-001",
            "chunk_id": "DOC-001-01",
        },
    }

    evidence = {
        "document_id": "DOC-001",
        "chunk_id": "DOC-001-01",
        "status": "Active",
        "title": "Operational Escalation Policy",
        "text": (
            "Escalation triggers may include sustained "
            "bed occupancy pressure."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] != "SUPPORTED"

    assert (
        "unsupported_number"
        in result["high_risk_guard"]["reasons"]
    )


def test_lifecycle_rejection_still_precedes_guard():
    claim = {
        "claim_id": "LIFECYCLE-C1",
        "claim_text": (
            "Operational escalation guidance should be followed."
        ),
        "citation": {
            "document_id": "DOC-001",
            "chunk_id": "DOC-001-OLD",
        },
    }

    evidence = {
        "document_id": "DOC-001",
        "chunk_id": "DOC-001-OLD",
        "status": "Superseded",
        "title": "Operational Escalation Policy",
        "text": (
            "Operational escalation guidance should be followed."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] == "CITATION_MISMATCH"


def test_wrong_citation_still_fails_before_support_checks():
    claim = {
        "claim_id": "MISMATCH-C1",
        "claim_text": (
            "Ambulance handover delays should be monitored."
        ),
        "citation": {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-01",
        },
    }

    evidence = {
        "document_id": "DOC-009",
        "chunk_id": "DOC-009-01",
        "status": "Active",
        "title": "Severe Weather Operational Plan",
        "text": (
            "Ambulance handover delays should be monitored."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
    )

    assert result["status"] == "CITATION_MISMATCH"


def test_empty_claim_set_still_abstains():
    result = verify_answer_citations(
        [],
        [],
    )

    assert result["decision"] == "ABSTAIN"