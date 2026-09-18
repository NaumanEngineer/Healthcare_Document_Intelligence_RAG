from pathlib import Path
import textwrap

import fitz


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


DOCUMENTS = [
    {
        "document_id": "DOC-001",
        "filename": "DOC-001_operational_escalation_policy.pdf",
        "title": "Operational Escalation Policy",
        "document_type": "Policy",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This policy defines the organisational approach to operational
        escalation when service pressure exceeds normal operating capacity.

        Escalation triggers may include sustained bed occupancy pressure,
        emergency department crowding, ambulance handover delay, workforce
        shortages, increased incident activity, infection pressures and
        disruption to patient flow.

        Operational leaders should review current pressure, confirm the
        severity of the situation, identify affected services and coordinate
        proportionate escalation actions.

        Actions may include increasing management oversight, reviewing
        available capacity, redeploying resources, accelerating discharge
        processes, coordinating with site-flow teams and escalating unresolved
        risks through the agreed operational command structure.

        Decisions should be documented, reviewed regularly and based on current
        approved operational information.

        This document is intended for operational decision support and does not
        replace clinical judgement.
        """,
    },
    {
        "document_id": "DOC-002",
        "filename": "DOC-002_winter_pressure_plan.pdf",
        "title": "Winter Pressure Plan",
        "document_type": "Operational Plan",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This plan supports operational resilience during periods of increased
        winter demand.

        Winter pressure may include increased emergency attendances, respiratory
        illness, weather disruption, staff absence, reduced discharge capacity
        and increased bed occupancy.

        Operational teams should monitor demand, staffing, bed availability,
        delayed discharge, emergency department performance and external
        disruption.

        Appropriate actions may include additional operational coordination,
        expanded capacity where authorised, workforce contingency measures,
        discharge acceleration, escalation to system partners and enhanced
        monitoring of high-risk services.

        Winter actions should remain proportionate to current demand and should
        be reviewed when pressure reduces or changes.
        """,
    },
    {
        "document_id": "DOC-003",
        "filename": "DOC-003_workforce_escalation_procedure.pdf",
        "title": "Workforce Escalation Procedure",
        "document_type": "Procedure",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This procedure describes operational escalation when workforce capacity
        becomes insufficient to support planned service delivery.

        Indicators may include unfilled shifts, high sickness absence, critical
        skill shortages, excessive agency dependence or staffing levels below
        locally agreed safe operational requirements.

        Managers should assess the affected service, identify available internal
        staffing options, review redeployment opportunities and escalate risks
        through the appropriate operational management route.

        Where pressure continues, contingency actions may include authorised
        redeployment, additional temporary staffing, service prioritisation and
        senior operational review.

        Workforce escalation decisions should be documented and reviewed until
        staffing pressure returns to an acceptable level.
        """,
    },
    {
        "document_id": "DOC-004",
        "filename": "DOC-004_bed_capacity_management_procedure.pdf",
        "title": "Bed Capacity Management Procedure",
        "document_type": "Procedure",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This procedure supports management of hospital bed capacity and patient
        flow during operational pressure.

        Capacity pressure may be indicated by high bed occupancy, limited
        available beds, delayed transfers, non-criteria-to-reside patients,
        discharge delays or increasing emergency demand.

        Site and operational teams should review current occupancy, expected
        admissions, planned discharges, delayed discharge barriers and available
        escalation capacity.

        Actions may include discharge coordination, use of approved escalation
        capacity, review of elective activity, cross-site coordination and
        escalation to senior operational leadership where pressure remains high.

        Bed capacity actions should be reviewed throughout the day and recorded
        through normal operational governance arrangements.
        """,
    },
    {
        "document_id": "DOC-005",
        "filename": "DOC-005_business_continuity_procedure.pdf",
        "title": "Business Continuity Procedure",
        "document_type": "Procedure",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This procedure supports continued delivery of critical operational
        services during disruption.

        Disruption may include infrastructure failure, digital outage, severe
        weather, workforce shortage, supply disruption or loss of access to
        facilities.

        Managers should identify affected critical services, assess available
        resources, activate appropriate continuity arrangements and establish
        clear operational communication.

        Priority should be given to maintaining essential services, protecting
        safety, restoring normal operations and escalating unresolved risks.

        Continuity actions and major decisions should be documented and reviewed
        until normal service arrangements are restored.
        """,
    },
    {
        "document_id": "DOC-006",
        "filename": "DOC-006_operational_governance_standard.pdf",
        "title": "Operational Governance Standard",
        "document_type": "Governance Standard",
        "status": "Active",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "body": """
        Purpose

        This standard defines governance expectations for operational
        decision-making and escalation.

        Operational decisions should use current approved information, have a
        clear accountable owner and maintain appropriate auditability.

        Teams should distinguish approved guidance from draft, archived or
        superseded material.

        Decisions should be proportionate to the operational risk, documented
        where required and reviewed when circumstances change.

        Automated or AI-supported systems may assist operational teams but
        should not remove human accountability.

        Evidence used to support operational decisions should be traceable to
        an identifiable source and lifecycle status.

        Human oversight remains required for significant operational decisions.
        """,
    },
]


def create_pdf(document: dict) -> None:
    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DIR / document["filename"]

    pdf = fitz.open()

    pages = [
        (
            f"{document['title']}\n\n"
            f"Document ID: {document['document_id']}\n"
            f"Document Type: {document['document_type']}\n"
            f"Version: {document['version']}\n"
            f"Effective Date: {document['effective_date']}\n"
            f"Status: {document['status']}\n\n"
        ),
        textwrap.dedent(
            document["body"]
        ).strip(),
    ]

    for page_number, text in enumerate(
        pages,
        start=1,
    ):
        page = pdf.new_page(
            width=595,
            height=842,
        )

        margin = 50

        rect = fitz.Rect(
            margin,
            margin,
            545,
            790,
        )

        page.insert_textbox(
            rect,
            text,
            fontsize=11,
            lineheight=1.4,
        )

        footer = (
            f"Page {page_number} | "
            "Synthetic training document — "
            "not an official NHS policy."
        )

        page.insert_text(
            (50, 815),
            footer,
            fontsize=8,
        )

    pdf.save(
        output_path
    )

    pdf.close()

    print(
        f"Created {output_path.name}"
    )


def main() -> None:
    for document in DOCUMENTS:
        create_pdf(
            document
        )

    print()
    print(
        f"Created {len(DOCUMENTS)} Week 17 core documents."
    )


if __name__ == "__main__":
    main()
