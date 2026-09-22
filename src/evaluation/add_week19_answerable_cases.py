from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVALUATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "evaluation_cases.json"
)


NEW_CASES = [
    {
        "query_id": "Q015",
        "category": "clear_single_document",
        "question": (
            "Which guidance should be followed when ambulance "
            "handover delays create operational pressure?"
        ),
        "expected_document_id": "DOC-008",
        "expected_document_title": (
            "Ambulance Handover Escalation Guidance"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear single-document ambulance handover "
            "operational question."
        ),
    },
    {
        "query_id": "Q016",
        "category": "clear_single_document",
        "question": (
            "Which operational plan should be used during "
            "severe weather disruption?"
        ),
        "expected_document_id": "DOC-009",
        "expected_document_title": (
            "Severe Weather Operational Plan"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear severe-weather operational question."
        ),
    },
    {
        "query_id": "Q017",
        "category": "clear_single_document",
        "question": (
            "Which procedure should be followed when critical "
            "staffing gaps threaten service delivery?"
        ),
        "expected_document_id": "DOC-011",
        "expected_document_title": (
            "Critical Staffing Contingency Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear critical-staffing contingency question."
        ),
    },
    {
        "query_id": "Q018",
        "category": "clear_single_document",
        "question": (
            "Which procedure coordinates operational site flow "
            "during periods of system pressure?"
        ),
        "expected_document_id": "DOC-012",
        "expected_document_title": (
            "Site Flow Coordination Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear site-flow coordination question."
        ),
    },
    {
        "query_id": "Q019",
        "category": "clear_single_document",
        "question": (
            "Which procedure describes escalation within the "
            "emergency department during operational pressure?"
        ),
        "expected_document_id": "DOC-007",
        "expected_document_title": (
            "Emergency Department Escalation Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear emergency-department escalation question."
        ),
    },
    {
        "query_id": "Q020",
        "category": "clear_single_document",
        "question": (
            "Which operational response should be followed "
            "during an infection surge?"
        ),
        "expected_document_id": "DOC-010",
        "expected_document_title": (
            "Infection Surge Operational Response Plan"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Clear infection-surge operational response question."
        ),
    },
    {
        "query_id": "Q021",
        "category": "paraphrased_operational",
        "question": (
            "Where should staff look for guidance when routine "
            "services cannot continue normally after a major disruption?"
        ),
        "expected_document_id": "DOC-005",
        "expected_document_title": (
            "Business Continuity Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Paraphrase of a business-continuity question "
            "without using the exact document title."
        ),
    },
    {
        "query_id": "Q022",
        "category": "paraphrased_operational",
        "question": (
            "Where should operational teams look for guidance "
            "when hospital beds are approaching unsafe capacity?"
        ),
        "expected_document_id": "DOC-004",
        "expected_document_title": (
            "Bed Capacity Management Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Paraphrased bed-capacity question."
        ),
    },
    {
        "query_id": "Q023",
        "category": "paraphrased_operational",
        "question": (
            "Which procedure covers actions when rota gaps and "
            "staffing shortages begin to threaten operations?"
        ),
        "expected_document_id": "DOC-003",
        "expected_document_title": (
            "Workforce Escalation Procedure"
        ),
        "expected_status": "Active",
        "expected_answerable": True,
        "expected_abstention": False,
        "expected_page": None,
        "expected_chunk_id": None,
        "notes": (
            "Paraphrased workforce-pressure question."
        ),
    },
]


def main() -> None:
    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {EVALUATION_FILE}"
        )

    with EVALUATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        existing_cases = json.load(file)

    if not isinstance(existing_cases, list):
        raise TypeError(
            "Evaluation file must contain a JSON list."
        )

    existing_ids = {
        case.get("query_id")
        for case in existing_cases
    }

    duplicate_ids = [
        case["query_id"]
        for case in NEW_CASES
        if case["query_id"] in existing_ids
    ]

    if duplicate_ids:
        raise ValueError(
            "Refusing to append duplicate query IDs: "
            + ", ".join(duplicate_ids)
        )

    updated_cases = (
        existing_cases
        + NEW_CASES
    )

    with EVALUATION_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            updated_cases,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Original cases: {len(existing_cases)}"
    )

    print(
        f"Added cases: {len(NEW_CASES)}"
    )

    print(
        f"New total: {len(updated_cases)}"
    )

    print(
        "Added query IDs:",
        ", ".join(
            case["query_id"]
            for case in NEW_CASES
        ),
    )


if __name__ == "__main__":
    main()