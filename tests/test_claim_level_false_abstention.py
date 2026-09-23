from src.retrieval.evidence_sufficiency import assess_evidence_sufficiency


def _assert_sufficient(question, evidence):
    result = assess_evidence_sufficiency(question, evidence)

    assert result["decision"] == "SUFFICIENT", result["reason"]
    assert result["sufficient"] is True


# ---------------------------------------------------------------------------
# 1. Supported relationship claims
# ---------------------------------------------------------------------------


def test_answerable_01_severe_weather_complements_continuity():
    question = (
        "How does the severe weather plan complement business continuity "
        "arrangements?"
    )

    evidence = [
        {
            "document_id": "DOC-009",
            "title": "Severe Weather Operational Plan",
            "text": (
                "The severe weather operational plan complements wider "
                "business continuity arrangements during weather disruption."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


def test_answerable_02_continuity_supports_essential_services():
    question = (
        "How do business continuity arrangements support essential services "
        "during a major disruption?"
    )

    evidence = [
        {
            "document_id": "DOC-005",
            "title": "Business Continuity Procedure",
            "text": (
                "Business continuity arrangements support essential services "
                "during a major disruption."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


# ---------------------------------------------------------------------------
# 2. Multi-document supported questions
# ---------------------------------------------------------------------------


def test_answerable_03_weather_and_handover():
    question = (
        "How should severe weather disruption and ambulance handover delays "
        "be considered together?"
    )

    evidence = [
        {
            "document_id": "DOC-009",
            "title": "Severe Weather Operational Plan",
            "text": "Prepare for severe weather disruption.",
        },
        {
            "document_id": "DOC-008",
            "title": "Ambulance Handover Escalation Guidance",
            "text": "Monitor ambulance handover delays and transfer delays.",
        },
    ]

    _assert_sufficient(question, evidence)


def test_answerable_04_workforce_and_site_flow():
    question = (
        "How should workforce shortages and site flow be considered together?"
    )

    evidence = [
        {
            "document_id": "DOC-003",
            "title": "Workforce Escalation Procedure",
            "text": "Review workforce shortages and staffing pressure.",
        },
        {
            "document_id": "DOC-012",
            "title": "Site Flow Coordination Procedure",
            "text": "Coordinate site flow and patient flow.",
        },
    ]

    _assert_sufficient(question, evidence)


def test_answerable_05_infection_and_bed_capacity():
    question = (
        "How can an infection surge affect bed capacity and operational "
        "bed flexibility?"
    )

    evidence = [
        {
            "document_id": "DOC-010",
            "title": "Infection Surge Operational Response Plan",
            "text": (
                "An infection surge can reduce bed flexibility through "
                "isolation requirements."
            ),
        },
        {
            "document_id": "DOC-004",
            "title": "Bed Capacity Management Procedure",
            "text": "Operational teams should review hospital bed capacity.",
        },
    ]

    _assert_sufficient(question, evidence)


# ---------------------------------------------------------------------------
# 3. Supported quantitative-style claims
# ---------------------------------------------------------------------------


def test_answerable_06_explicit_numerical_trigger():
    question = (
        "What exact numerical trigger is stated for escalation?"
    )

    evidence = [
        {
            "title": "Synthetic Escalation Procedure",
            "text": (
                "The exact numerical trigger for escalation is explicitly "
                "defined in this procedure."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


def test_answerable_07_explicit_percentage_requirement():
    question = (
        "What exact percentage is specified by the procedure?"
    )

    evidence = [
        {
            "title": "Synthetic Capacity Procedure",
            "text": (
                "The exact percentage is specified by the procedure and must "
                "be recorded during capacity review."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


# ---------------------------------------------------------------------------
# 4. Supported procedural / mandatory claims
# ---------------------------------------------------------------------------


def test_answerable_08_mandatory_review():
    question = (
        "What mandatory action applies during workforce pressure?"
    )

    evidence = [
        {
            "document_id": "DOC-003",
            "title": "Workforce Escalation Procedure",
            "text": (
                "A mandatory action during workforce pressure is review of "
                "staffing gaps and available redeployment options."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


def test_answerable_09_mandates_capacity_review():
    question = (
        "What action does the bed capacity procedure mandate?"
    )

    evidence = [
        {
            "document_id": "DOC-004",
            "title": "Bed Capacity Management Procedure",
            "text": (
                "The procedure mandates review of bed occupancy, expected "
                "admissions and planned discharges."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


# ---------------------------------------------------------------------------
# 5. Hard paraphrases
# ---------------------------------------------------------------------------


def test_answerable_10_handover_paraphrase():
    question = (
        "Which guidance applies when emergency transport crews are waiting "
        "to transfer responsibility for patients into hospital care?"
    )

    evidence = [
        {
            "document_id": "DOC-008",
            "title": "Ambulance Handover Escalation Guidance",
            "text": (
                "Ambulance handover guidance covers crews experiencing "
                "transfer delays into hospital."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


def test_answerable_11_business_continuity_paraphrase():
    question = (
        "Which procedure helps keep essential services operating when normal "
        "arrangements cannot continue?"
    )

    evidence = [
        {
            "document_id": "DOC-005",
            "title": "Business Continuity Procedure",
            "text": (
                "Business continuity arrangements maintain essential services "
                "when routine services are disrupted."
            ),
        }
    ]

    _assert_sufficient(question, evidence)


def test_answerable_12_weather_paraphrase():
    question = (
        "Which operational plan should teams use when forecast weather is "
        "likely to disrupt access and normal service delivery?"
    )

    evidence = [
        {
            "document_id": "DOC-009",
            "title": "Severe Weather Operational Plan",
            "text": (
                "The severe weather operational plan supports preparation "
                "before weather disruption affects service delivery."
            ),
        }
    ]

    _assert_sufficient(question, evidence)