from src.governance.citation_verification import (
    verify_answer_citations,
    verify_claim_citation,
)


def test_supported_claim_with_correct_citation():
    claim = {
        "claim_id": "C1",
        "claim_text": "Severe weather preparation should begin before disruption.",
        "citation": {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01",
        },
    }

    evidence = {
        "document_id": "DOC-009",
        "chunk_id": "DOC-009-01",
        "status": "Active",
        "title": "Severe Weather Operational Plan",
        "text": (
            "The severe weather operational plan supports preparation "
            "before disruption affects service delivery."
        ),
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] == "SUPPORTED"


def test_wrong_document_citation_is_mismatch():
    claim = {
        "claim_id": "C2",
        "claim_text": "Ambulance handover delays should be monitored.",
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
        "text": "Prepare for severe weather disruption.",
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] == "CITATION_MISMATCH"


def test_missing_citation_is_unsupported():
    claim = {
        "claim_id": "C3",
        "claim_text": "A £500 national penalty applies after 30 minutes.",
        "citation": None,
    }

    result = verify_claim_citation(claim, None)

    assert result["status"] == "UNSUPPORTED"


def test_superseded_evidence_is_rejected():
    claim = {
        "claim_id": "C4",
        "claim_text": "Operational escalation guidance should be followed.",
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
        "text": "Operational escalation guidance should be followed.",
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] == "CITATION_MISMATCH"


def test_partially_supported_claim():
    claim = {
        "claim_id": "C5",
        "claim_text": (
            "Severe weather preparation should begin before disruption "
            "and all elective activity must be cancelled."
        ),
        "citation": {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01",
        },
    }

    evidence = {
        "document_id": "DOC-009",
        "chunk_id": "DOC-009-01",
        "status": "Active",
        "title": "Severe Weather Operational Plan",
        "text": (
            "The severe weather operational plan supports preparation "
            "before disruption affects service delivery."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
        support_threshold=0.80,
    )

    assert result["status"] == "PARTIALLY_SUPPORTED"


def test_answer_passes_when_all_claims_supported():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": "Ambulance handover delays should be monitored.",
            "citation": {
                "document_id": "DOC-008",
                "chunk_id": "DOC-008-01",
            },
        },
        {
            "claim_id": "C2",
            "claim_text": "Severe weather preparation should begin before disruption.",
            "citation": {
                "document_id": "DOC-009",
                "chunk_id": "DOC-009-01",
            },
        },
    ]

    evidence_items = [
        {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-01",
            "status": "Active",
            "title": "Ambulance Handover Escalation Guidance",
            "text": "Ambulance handover delays should be monitored.",
        },
        {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01",
            "status": "Active",
            "title": "Severe Weather Operational Plan",
            "text": (
                "Severe weather preparation should begin before disruption."
            ),
        },
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
    )

    assert result["decision"] == "PASS"


def test_answer_requires_review_when_one_claim_is_unsupported():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": "Ambulance handover delays should be monitored.",
            "citation": {
                "document_id": "DOC-008",
                "chunk_id": "DOC-008-01",
            },
        },
        {
            "claim_id": "C2",
            "claim_text": "A £500 national penalty applies after 30 minutes.",
            "citation": None,
        },
    ]

    evidence_items = [
        {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-01",
            "status": "Active",
            "title": "Ambulance Handover Escalation Guidance",
            "text": "Ambulance handover delays should be monitored.",
        }
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
    )

    assert result["decision"] == "REVIEW_REQUIRED"


def test_empty_answer_abstains():
    result = verify_answer_citations(
        [],
        [],
    )

    assert result["decision"] == "ABSTAIN"