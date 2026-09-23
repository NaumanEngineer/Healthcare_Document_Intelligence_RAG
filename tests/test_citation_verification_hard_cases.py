from src.governance.citation_verification import (
    verify_answer_citations,
    verify_claim_citation,
)


def test_hard_01_wrong_chunk_same_document():
    claim = {
        "claim_id": "HC1",
        "claim_text": "Ambulance handover delays should be monitored.",
        "citation": {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-02",
        },
    }

    evidence = {
        "document_id": "DOC-008",
        "chunk_id": "DOC-008-01",
        "status": "Active",
        "title": "Ambulance Handover Escalation Guidance",
        "text": "Ambulance handover delays should be monitored.",
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] == "CITATION_MISMATCH"


def test_hard_02_relevant_document_but_wrong_claim():
    claim = {
        "claim_id": "HC2",
        "claim_text": "A £500 national penalty applies after 30 minutes.",
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
            "Operational teams should monitor ambulance handover delays "
            "and persistent transfer delays."
        ),
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] in {
        "UNSUPPORTED",
        "PARTIALLY_SUPPORTED",
    }


def test_hard_03_supported_core_but_invented_threshold():
    claim = {
        "claim_id": "HC3",
        "claim_text": (
            "Bed occupancy should be reviewed throughout the day "
            "and 92 percent occupancy requires immediate executive escalation."
        ),
        "citation": {
            "document_id": "DOC-004",
            "chunk_id": "DOC-004-01",
        },
    }

    evidence = {
        "document_id": "DOC-004",
        "chunk_id": "DOC-004-01",
        "status": "Active",
        "title": "Bed Capacity Management Procedure",
        "text": (
            "Operational teams should review bed occupancy "
            "throughout the day."
        ),
    }

    result = verify_claim_citation(
        claim,
        evidence,
        support_threshold=0.80,
    )

    assert result["status"] == "PARTIALLY_SUPPORTED"


def test_hard_04_correct_document_wrong_lifecycle():
    claim = {
        "claim_id": "HC4",
        "claim_text": "Operational escalation guidance should be followed.",
        "citation": {
            "document_id": "DOC-001",
            "chunk_id": "DOC-001-OLD",
        },
    }

    evidence = {
        "document_id": "DOC-001",
        "chunk_id": "DOC-001-OLD",
        "status": "Draft",
        "title": "Operational Escalation Policy",
        "text": "Operational escalation guidance should be followed.",
    }

    result = verify_claim_citation(claim, evidence)

    assert result["status"] == "CITATION_MISMATCH"


def test_hard_05_multi_claim_answer_with_one_bad_claim():
    claims = [
        {
            "claim_id": "HC5A",
            "claim_text": "Severe weather preparation should begin before disruption.",
            "citation": {
                "document_id": "DOC-009",
                "chunk_id": "DOC-009-01",
            },
        },
        {
            "claim_id": "HC5B",
            "claim_text": "All elective activity must be cancelled.",
            "citation": {
                "document_id": "DOC-009",
                "chunk_id": "DOC-009-01",
            },
        },
    ]

    evidence_items = [
        {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01",
            "status": "Active",
            "title": "Severe Weather Operational Plan",
            "text": (
                "The severe weather operational plan supports "
                "advance preparation before disruption."
            ),
        }
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
        support_threshold=0.80,
    )

    assert result["decision"] == "REVIEW_REQUIRED"


def test_hard_06_supported_multi_document_answer():
    claims = [
        {
            "claim_id": "HC6A",
            "claim_text": "Severe weather preparation should begin before disruption.",
            "citation": {
                "document_id": "DOC-009",
                "chunk_id": "DOC-009-01",
            },
        },
        {
            "claim_id": "HC6B",
            "claim_text": "Ambulance handover delays should be monitored.",
            "citation": {
                "document_id": "DOC-008",
                "chunk_id": "DOC-008-01",
            },
        },
    ]

    evidence_items = [
        {
            "document_id": "DOC-009",
            "chunk_id": "DOC-009-01",
            "status": "Active",
            "title": "Severe Weather Operational Plan",
            "text": (
                "Severe weather preparation should begin before disruption."
            ),
        },
        {
            "document_id": "DOC-008",
            "chunk_id": "DOC-008-01",
            "status": "Active",
            "title": "Ambulance Handover Escalation Guidance",
            "text": (
                "Ambulance handover delays should be monitored."
            ),
        },
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
    )

    assert result["decision"] == "PASS"


def test_hard_07_citation_to_missing_evidence():
    claim = {
        "claim_id": "HC7",
        "claim_text": "Workforce gaps should be reviewed.",
        "citation": {
            "document_id": "DOC-003",
            "chunk_id": "DOC-003-99",
        },
    }

    result = verify_claim_citation(
        claim,
        None,
    )

    assert result["status"] == "CITATION_MISMATCH"


def test_hard_08_partial_support_should_not_pass_answer():
    claims = [
        {
            "claim_id": "HC8",
            "claim_text": (
                "Business continuity arrangements maintain essential "
                "services and require immediate evacuation of all premises."
            ),
            "citation": {
                "document_id": "DOC-005",
                "chunk_id": "DOC-005-01",
            },
        }
    ]

    evidence_items = [
        {
            "document_id": "DOC-005",
            "chunk_id": "DOC-005-01",
            "status": "Active",
            "title": "Business Continuity Procedure",
            "text": (
                "Business continuity arrangements maintain essential "
                "services during disruption."
            ),
        }
    ]

    result = verify_answer_citations(
        claims,
        evidence_items,
        support_threshold=0.80,
    )

    assert result["decision"] == "REVIEW_REQUIRED"