from __future__ import annotations

from pathlib import Path
import textwrap

import fitz


OUTPUT_DIRECTORY = Path(
    "data/raw"
)


DOCUMENTS = [
    {
        "document_id": "DOC-007",
        "title": "Emergency Department Escalation Procedure",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Emergency Department Pressure Triggers",
                "body": """
                Emergency Department escalation should be considered when
                demand exceeds the department's available operational
                capacity.

                Indicators may include sustained increases in attendances,
                deterioration in four-hour performance, crowding,
                ambulance arrivals exceeding available assessment capacity,
                and significant delays in patient flow.

                The operational site team should review pressure indicators
                collectively rather than relying on a single measure.
                """
            },
            {
                "heading": "Escalation Actions and Oversight",
                "body": """
                When Emergency Department pressure becomes severe,
                operational leadership should coordinate actions across
                emergency care, bed management, diagnostics, discharge
                services and workforce teams.

                Actions should be documented, reviewed at agreed intervals,
                and adjusted when operational conditions change.

                Decisions remain subject to local governance arrangements
                and human operational accountability.
                """
            },
        ],
    },
    {
        "document_id": "DOC-008",
        "title": "Ambulance Handover Escalation Guidance",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Ambulance Handover Pressure",
                "body": """
                Ambulance handover delays should be monitored as part of
                the wider urgent and emergency care pressure picture.

                Operational teams should review the number of delayed
                handovers, delay duration, Emergency Department capacity,
                available assessment space and downstream bed flow.

                Persistent handover delay may indicate pressure elsewhere
                in the patient pathway rather than an isolated ambulance
                problem.
                """
            },
            {
                "heading": "Coordinated Response",
                "body": """
                Where ambulance handover delay becomes significant,
                site coordination should bring together Emergency
                Department leadership, ambulance liaison, bed management
                and operational leadership.

                The response should focus on safe patient flow,
                prioritisation of operational bottlenecks and removal of
                avoidable delays.

                Handover escalation should be reviewed alongside wider
                organisational escalation arrangements.
                """
            },
        ],
    },
    {
        "document_id": "DOC-009",
        "title": "Severe Weather Operational Plan",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Severe Weather Readiness",
                "body": """
                Severe weather may affect patient demand, workforce
                availability, transport, supply chains and access to
                community services.

                Operational teams should monitor weather warnings,
                forecast conditions and known organisational
                vulnerabilities.

                Readiness activity should begin before expected disruption
                where credible weather information indicates increased
                operational risk.
                """
            },
            {
                "heading": "Operational Response",
                "body": """
                During severe weather, operational leadership should review
                staffing resilience, transport disruption, critical
                supplies, patient flow and business continuity arrangements.

                Escalation decisions should reflect the combined impact of
                weather conditions and existing organisational pressure.

                The Severe Weather Operational Plan should complement,
                rather than replace, wider winter-pressure and business
                continuity arrangements.
                """
            },
        ],
    },
    {
        "document_id": "DOC-010",
        "title": "Infection Surge Operational Response Plan",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Operational Impact of Infection Surge",
                "body": """
                An infection surge may create operational pressure through
                increased demand, staff absence, isolation requirements,
                reduced bed flexibility and disruption to normal patient
                flow.

                Operational teams should assess the combined effect on bed
                capacity, workforce resilience and service continuity.

                This document addresses operational coordination and does
                not provide clinical diagnosis or treatment guidance.
                """
            },
            {
                "heading": "Escalation and Coordination",
                "body": """
                Where infection-related operational pressure increases,
                leadership should coordinate capacity planning, workforce
                actions, patient flow and business continuity measures.

                Operational decisions should use current organisational
                guidance and should be reviewed as demand or staffing
                conditions change.

                Clinical decisions remain outside the scope of this
                operational response plan.
                """
            },
        ],
    },
    {
        "document_id": "DOC-011",
        "title": "Critical Staffing Contingency Procedure",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Critical Staffing Risk",
                "body": """
                Critical staffing pressure occurs when available staffing
                falls below the level required to maintain planned
                operational capacity safely and effectively.

                Indicators may include high unfilled shifts, increased
                sickness absence, unexpected specialist-role gaps,
                dependency on temporary staffing and repeated short-notice
                rota changes.

                Staffing pressure should be assessed alongside service
                demand and operational risk.
                """
            },
            {
                "heading": "Contingency Actions",
                "body": """
                Operational leadership should review redeployment options,
                temporary staffing arrangements, service prioritisation,
                escalation routes and the impact of staffing shortages on
                capacity.

                Significant decisions should be documented and reviewed.

                This contingency procedure complements the Workforce
                Escalation Procedure but focuses specifically on critical
                short-term staffing resilience.
                """
            },
        ],
    },
    {
        "document_id": "DOC-012",
        "title": "Site Flow Coordination Procedure",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": "Active",
        "pages": [
            {
                "heading": "Whole-Site Patient Flow",
                "body": """
                Effective site flow requires coordination across emergency
                care, inpatient services, bed management, discharge
                services and operational leadership.

                Flow pressure should be assessed using multiple indicators,
                including bed occupancy, emergency demand, delayed
                discharge, ambulance handover and available workforce.

                No single operational metric should be interpreted in
                isolation.
                """
            },
            {
                "heading": "Site Coordination Actions",
                "body": """
                During periods of significant pressure, the site
                coordination function should identify major operational
                bottlenecks, assign actions, record ownership and review
                progress.

                Actions may involve bed capacity, discharge coordination,
                workforce escalation, emergency-flow measures and
                cross-service support.

                The purpose is to coordinate operational response rather
                than replace individual service procedures.
                """
            },
        ],
    },
]


def add_wrapped_text(
    page: fitz.Page,
    text: str,
    x: float,
    y: float,
    font_size: float = 11,
    line_height: float = 16,
    max_chars: int = 85,
) -> float:
    """
    Add wrapped text to a PDF page and return the final Y position.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.strip().split(
            "\n\n"
        )
        if paragraph.strip()
    ]

    current_y = y

    for paragraph in paragraphs:
        lines = textwrap.wrap(
            " ".join(
                paragraph.split()
            ),
            width=max_chars,
        )

        for line in lines:
            page.insert_text(
                (x, current_y),
                line,
                fontsize=font_size,
            )

            current_y += line_height

        current_y += line_height / 2

    return current_y


def create_document_pdf(
    document: dict,
    output_directory: Path,
) -> Path:
    """
    Create one synthetic operational PDF.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"{document['document_id']}_"
        + document["title"]
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        + ".pdf"
    )

    output_path = (
        output_directory
        / filename
    )

    pdf = fitz.open()

    for page_number, page_content in enumerate(
        document["pages"],
        start=1,
    ):
        page = pdf.new_page(
            width=595,
            height=842,
        )

        page.insert_text(
            (50, 55),
            document["title"],
            fontsize=16,
        )

        page.insert_text(
            (50, 80),
            (
                f"Document ID: "
                f"{document['document_id']}"
            ),
            fontsize=10,
        )

        page.insert_text(
            (50, 96),
            (
                f"Version: "
                f"{document['version']}"
            ),
            fontsize=10,
        )

        page.insert_text(
            (50, 112),
            (
                f"Effective Date: "
                f"{document['effective_date']}"
            ),
            fontsize=10,
        )

        page.insert_text(
            (50, 128),
            (
                f"Status: "
                f"{document['status']}"
            ),
            fontsize=10,
        )

        page.insert_text(
            (50, 144),
            (
                f"Page: {page_number}"
            ),
            fontsize=10,
        )

        page.insert_text(
            (50, 180),
            page_content[
                "heading"
            ],
            fontsize=13,
        )

        add_wrapped_text(
            page=page,
            text=page_content[
                "body"
            ],
            x=50,
            y=210,
        )

        page.insert_text(
            (50, 800),
            (
                "Synthetic training document — "
                "not an official NHS policy."
            ),
            fontsize=8,
        )

    pdf.save(
        output_path
    )

    pdf.close()

    return output_path


def create_week18_corpus() -> list[Path]:
    """
    Generate all Week 18 synthetic operational PDFs.
    """

    created_files = []

    for document in DOCUMENTS:
        output_path = (
            create_document_pdf(
                document=document,
                output_directory=OUTPUT_DIRECTORY,
            )
        )

        created_files.append(
            output_path
        )

    return created_files


if __name__ == "__main__":
    files = create_week18_corpus()

    print(
        f"Created {len(files)} synthetic PDFs:"
    )

    for file_path in files:
        print(
            f"- {file_path}"
        )
