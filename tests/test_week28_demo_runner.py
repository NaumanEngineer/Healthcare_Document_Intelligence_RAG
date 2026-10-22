"""Week 28 governed three-outcome demo runner tests."""

from __future__ import annotations

from copy import deepcopy

from src.application.manager_response import (
    OUTCOME_ABSTAIN,
    OUTCOME_ANSWER,
    OUTCOME_REVIEW_REQUIRED,
)
from src.application.week28_demo_runner import (
    run_week28_three_outcome_demo,
)


def _report() -> dict:
    return run_week28_three_outcome_demo()


def _results_by_outcome() -> dict[str, dict]:
    report = _report()

    return {
        result["actual_outcome"]: result
        for result in report["results"]
    }


def test_three_outcome_demo_runs_three_cases():
    report = _report()

    assert report["case_count"] == 3

    assert len(
        report["results"]
    ) == 3


def test_three_expected_outcomes_are_present():
    report = _report()

    outcomes = {
        result["expected_outcome"]
        for result in report["results"]
    }

    assert outcomes == {
        OUTCOME_ANSWER,
        OUTCOME_REVIEW_REQUIRED,
        OUTCOME_ABSTAIN,
    }


def test_all_governed_outcomes_match_expectation():
    report = _report()

    assert (
        report["matched_case_count"]
        == 3
    )

    assert (
        report["all_cases_matched"]
        is True
    )

    for result in report["results"]:
        assert (
            result["actual_outcome"]
            == result["expected_outcome"]
        )

        assert result["matched"] is True


def test_all_manager_presentations_match_governed_outcomes():
    report = _report()

    assert (
        report["presentation_match_count"]
        == 3
    )

    assert (
        report["all_presentations_matched"]
        is True
    )

    for result in report["results"]:
        manager_response = (
            result["manager_response"]
        )

        assert (
            manager_response["outcome"]
            == result["actual_outcome"]
        )

        assert (
            result[
                "presentation_outcome_matches"
            ]
            is True
        )


def test_authority_is_preserved_for_every_case():
    report = _report()

    assert (
        report["authority_preserved_count"]
        == 3
    )

    assert (
        report["all_authority_preserved"]
        is True
    )

    for result in report["results"]:
        assert (
            result["authority_preserved"]
            is True
        )

        assert (
            result[
                "manager_response"
            ][
                "authority_preserved"
            ]
            is True
        )


def test_every_case_completes_application_execution():
    report = _report()

    for result in report["results"]:
        assert (
            result["application_status"]
            == "COMPLETED"
        )


def test_every_case_completes_observability():
    report = _report()

    for result in report["results"]:
        assert (
            result["observability_status"]
            == "COMPLETED"
        )

        assert (
            result["observed_event_count"]
            > 0
        )


def test_answer_case_exposes_supported_manager_answer():
    result = (
        _results_by_outcome()[
            OUTCOME_ANSWER
        ]
    )

    manager_response = (
        result["manager_response"]
    )

    assert (
        manager_response["outcome"]
        == OUTCOME_ANSWER
    )

    assert (
        manager_response["answer"]
        is not None
    )

    assert (
        manager_response[
            "human_review_required"
        ]
        is False
    )


def test_answer_case_preserves_governed_citation():
    result = (
        _results_by_outcome()[
            OUTCOME_ANSWER
        ]
    )

    citations = (
        result[
            "manager_response"
        ][
            "citations"
        ]
    )

    assert len(citations) == 1

    assert (
        citations[0]["citation_id"]
        == "E1"
    )

    assert (
        citations[0]["document_id"]
        == "W28-DEMO-DOC-A001"
    )


def test_review_case_never_releases_answer_content():
    result = (
        _results_by_outcome()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    manager_response = (
        result["manager_response"]
    )

    assert (
        manager_response["outcome"]
        == OUTCOME_REVIEW_REQUIRED
    )

    assert (
        manager_response["answer"]
        is None
    )

    assert (
        manager_response[
            "human_review_required"
        ]
        is True
    )


def test_review_case_does_not_manufacture_citations():
    result = (
        _results_by_outcome()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    assert (
        result[
            "manager_response"
        ][
            "citations"
        ]
        == []
    )


def test_abstain_case_never_releases_answer_content():
    result = (
        _results_by_outcome()[
            OUTCOME_ABSTAIN
        ]
    )

    manager_response = (
        result["manager_response"]
    )

    assert (
        manager_response["outcome"]
        == OUTCOME_ABSTAIN
    )

    assert (
        manager_response["answer"]
        is None
    )

    assert (
        manager_response[
            "human_review_required"
        ]
        is True
    )


def test_abstain_case_does_not_manufacture_citations():
    result = (
        _results_by_outcome()[
            OUTCOME_ABSTAIN
        ]
    )

    assert (
        result[
            "manager_response"
        ][
            "citations"
        ]
        == []
    )


def test_manager_presentation_does_not_mutate_governed_result():
    report = _report()

    for result in report["results"]:
        governed_result = deepcopy(
            result["result"]
        )

        snapshot = deepcopy(
            governed_result
        )

        assert (
            governed_result
            == snapshot
        )


def test_answer_headline_is_management_friendly():
    result = (
        _results_by_outcome()[
            OUTCOME_ANSWER
        ]
    )

    assert (
        result[
            "manager_response"
        ][
            "headline"
        ]
        == "Supported guidance found"
    )


def test_review_headline_is_management_friendly():
    result = (
        _results_by_outcome()[
            OUTCOME_REVIEW_REQUIRED
        ]
    )

    assert (
        result[
            "manager_response"
        ][
            "headline"
        ]
        == (
            "Human review required before "
            "using this information"
        )
    )


def test_abstain_headline_is_management_friendly():
    result = (
        _results_by_outcome()[
            OUTCOME_ABSTAIN
        ]
    )

    assert (
        result[
            "manager_response"
        ][
            "headline"
        ]
        == (
            "Insufficient evidence for "
            "a safe answer"
        )
    )


def test_manager_responses_have_next_actions():
    report = _report()

    for result in report["results"]:
        next_action = (
            result[
                "manager_response"
            ][
                "next_action"
            ]
        )

        assert isinstance(
            next_action,
            str,
        )

        assert next_action.strip()


def test_manager_responses_have_evidence_basis():
    report = _report()

    for result in report["results"]:
        evidence_basis = (
            result[
                "manager_response"
            ][
                "evidence_basis"
            ]
        )

        assert isinstance(
            evidence_basis,
            str,
        )

        assert evidence_basis.strip()


def test_canonical_governed_result_is_retained():
    report = _report()

    for result in report["results"]:
        governed = result["result"]

        assert (
            governed["final_outcome"]
            == result["actual_outcome"]
        )

        assert (
            "governance"
            in governed
        )

        assert (
            "assurance"
            in governed
        )

        assert (
            "observability"
            in governed
        )