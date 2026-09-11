import json

import pytest

from src.evaluation.evaluation_dataset import (
    validate_evaluation_case,
    load_evaluation_cases,
    group_cases_by_category,
    count_answerable_cases,
    count_abstention_cases,
)


def build_valid_case() -> dict:
    return {
        "query_id": "Q001",
        "category": "escalation",
        "question": (
            "What should operational leadership do?"
        ),
        "expected_answerable": True,
        "expected_abstention": False,
        "notes": "Test case.",
    }


def test_validate_evaluation_case_accepts_valid_case():
    validate_evaluation_case(
        build_valid_case()
    )


def test_validate_evaluation_case_rejects_missing_field():
    case = build_valid_case()

    del case["question"]

    with pytest.raises(
        ValueError,
        match="Missing evaluation case field",
    ):
        validate_evaluation_case(
            case
        )


def test_validate_evaluation_case_rejects_invalid_logic():
    case = build_valid_case()

    case[
        "expected_abstention"
    ] = True

    with pytest.raises(
        ValueError,
        match="logical opposites",
    ):
        validate_evaluation_case(
            case
        )


def test_load_evaluation_cases(tmp_path):
    path = tmp_path / (
        "evaluation_cases.json"
    )

    path.write_text(
        json.dumps(
            [
                build_valid_case()
            ]
        ),
        encoding="utf-8",
    )

    cases = load_evaluation_cases(
        path
    )

    assert len(cases) == 1

    assert (
        cases[0]["query_id"]
        == "Q001"
    )


def test_load_evaluation_cases_rejects_duplicates(
    tmp_path,
):
    path = tmp_path / (
        "evaluation_cases.json"
    )

    case = build_valid_case()

    path.write_text(
        json.dumps(
            [
                case,
                case,
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate query_id",
    ):
        load_evaluation_cases(
            path
        )


def test_group_cases_by_category():
    first = build_valid_case()

    second = build_valid_case()
    second["query_id"] = "Q002"
    second["category"] = "workforce"

    grouped = group_cases_by_category(
        [
            first,
            second,
        ]
    )

    assert "escalation" in grouped
    assert "workforce" in grouped


def test_count_answerable_cases():
    first = build_valid_case()

    second = build_valid_case()
    second["query_id"] = "Q002"
    second[
        "expected_answerable"
    ] = False
    second[
        "expected_abstention"
    ] = True

    assert count_answerable_cases(
        [
            first,
            second,
        ]
    ) == 1


def test_count_abstention_cases():
    first = build_valid_case()

    second = build_valid_case()
    second["query_id"] = "Q002"
    second[
        "expected_answerable"
    ] = False
    second[
        "expected_abstention"
    ] = True

    assert count_abstention_cases(
        [
            first,
            second,
        ]
    ) == 1
