from __future__ import annotations

import json
from pathlib import Path


DEFAULT_EVALUATION_PATH = Path(
    "data/synthetic/evaluation_cases.json"
)


REQUIRED_CASE_FIELDS = (
    "query_id",
    "category",
    "question",
    "expected_answerable",
    "expected_abstention",
    "notes",
)


def validate_evaluation_case(
    case: dict,
) -> None:
    """
    Validate one evaluation benchmark case.
    """

    if not isinstance(case, dict):
        raise TypeError(
            "evaluation case must be a dictionary"
        )

    for field in REQUIRED_CASE_FIELDS:
        if field not in case:
            raise ValueError(
                f"Missing evaluation case field: {field}"
            )

    for field in (
        "query_id",
        "category",
        "question",
        "notes",
    ):
        value = case.get(field)

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"{field} must be a non-empty string"
            )

    for field in (
        "expected_answerable",
        "expected_abstention",
    ):
        if not isinstance(
            case.get(field),
            bool,
        ):
            raise TypeError(
                f"{field} must be a boolean"
            )

    if (
        case["expected_answerable"]
        == case["expected_abstention"]
    ):
        raise ValueError(
            "expected_answerable and expected_abstention "
            "must be logical opposites"
        )


def load_evaluation_cases(
    path: str | Path = DEFAULT_EVALUATION_PATH,
) -> list[dict]:
    """
    Load and validate evaluation benchmark cases.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError(
            "evaluation dataset must contain a JSON list"
        )

    if not cases:
        raise ValueError(
            "evaluation dataset must not be empty"
        )

    seen_query_ids = set()

    for case in cases:
        validate_evaluation_case(
            case
        )

        query_id = case[
            "query_id"
        ]

        if query_id in seen_query_ids:
            raise ValueError(
                f"Duplicate query_id: {query_id}"
            )

        seen_query_ids.add(
            query_id
        )

    return cases


def group_cases_by_category(
    cases: list[dict],
) -> dict[str, list[dict]]:
    """
    Group benchmark cases by category.
    """

    grouped = {}

    for case in cases:
        category = case[
            "category"
        ]

        grouped.setdefault(
            category,
            [],
        ).append(
            case
        )

    return grouped


def count_answerable_cases(
    cases: list[dict],
) -> int:
    """
    Count answerable benchmark questions.
    """

    return sum(
        1
        for case in cases
        if case[
            "expected_answerable"
        ]
    )


def count_abstention_cases(
    cases: list[dict],
) -> int:
    """
    Count expected abstention questions.
    """

    return sum(
        1
        for case in cases
        if case[
            "expected_abstention"
        ]
    )
