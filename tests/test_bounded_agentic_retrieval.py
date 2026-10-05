from __future__ import annotations

import pytest

import src.retrieval.bounded_agentic_retrieval as agentic_module

from src.retrieval.bounded_agentic_retrieval import (
    bounded_agentic_retrieval,
)


def make_result(
    chunk_id: str,
    text: str,
    *,
    status: str = "Active",
    document_id: str | None = None,
) -> dict:
    """Create a minimally complete retrieval result."""

    if document_id is None:
        document_id = f"DOC-{chunk_id}"

    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": f"Policy {document_id}",
        "document_type": "Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": f"{document_id}.txt",
        "page": 1,
        "chunk_number": 1,
        "text": text,
        "rrf_score": 0.03,
        "rank": 1,
    }


def run_agentic(
    *,
    query: str,
    monkeypatch,
    retrieval_outputs: list[list[dict]],
    max_rounds: int = 2,
    final_k: int = 3,
    query_refiner=None,
):
    """Run bounded retrieval with controlled Hybrid outputs."""

    calls = []

    outputs = list(
        retrieval_outputs
    )

    def fake_hybrid_search(**kwargs):
        calls.append(
            kwargs["query"]
        )

        if not outputs:
            raise AssertionError(
                "Hybrid retrieval called more times than expected"
            )

        return outputs.pop(0)

    monkeypatch.setattr(
        agentic_module,
        "hybrid_search",
        fake_hybrid_search,
    )

    kwargs = {}

    if query_refiner is not None:
        kwargs["query_refiner"] = (
            query_refiner
        )

    result = bounded_agentic_retrieval(
        query=query,
        chunks=[],
        embedded_chunks=[],
        model=object(),
        embedding_model="test-model",
        final_k=final_k,
        max_rounds=max_rounds,
        **kwargs,
    )

    return result, calls


def test_initial_sufficient_evidence_stops_after_one_call(
    monkeypatch,
):
    initial = [
        make_result(
            "CHUNK-1",
            "Bed capacity pressure and hospital beds are monitored.",
        )
    ]

    result, calls = run_agentic(
        query="How should bed capacity be managed?",
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
    )

    assert len(calls) == 1

    assert (
        result["audit"]["retrieval_call_count"]
        == 1
    )

    assert (
        result["audit"]["stop_reason"]
        == "INITIAL_EVIDENCE_SUFFICIENT"
    )


def test_recoverable_gap_causes_one_refinement(
    monkeypatch,
):
    initial = [
        make_result(
            "CHUNK-BED",
            "Bed capacity pressure and hospital beds.",
        )
    ]

    refined = [
        make_result(
            "CHUNK-WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result, calls = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert len(calls) == 2

    assert (
        result["audit"]["retrieval_call_count"]
        == 2
    )

    assert (
        "workforce"
        in calls[1].lower()
    )

    assert (
        result["audit"]["final_evidence"][
            "sufficient"
        ]
        is True
    )

    assert (
        result["audit"]["stop_reason"]
        == "EVIDENCE_SUFFICIENT_AFTER_REFINEMENT"
    )


def test_max_rounds_one_prevents_refinement(
    monkeypatch,
):
    initial = [
        make_result(
            "CHUNK-BED",
            "Bed capacity pressure.",
        )
    ]

    result, calls = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
        max_rounds=1,
    )

    assert len(calls) == 1

    assert (
        result["audit"]["stop_reason"]
        == "MAX_ROUNDS_REACHED"
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        0,
        -1,
        3,
        True,
        False,
        1.5,
        "2",
        None,
    ],
)
def test_invalid_max_rounds_rejected(
    invalid_value,
):
    with pytest.raises(ValueError):
        bounded_agentic_retrieval(
            query="How should staffing pressure be managed?",
            chunks=[],
            embedded_chunks=[],
            model=object(),
            embedding_model="test-model",
            max_rounds=invalid_value,
        )


def test_draft_evidence_excluded(
    monkeypatch,
):
    initial = [
        make_result(
            "ACTIVE-BED",
            "Bed capacity pressure.",
        ),
        make_result(
            "DRAFT-WORKFORCE",
            "Workforce pressure and staffing gaps.",
            status="Draft",
        ),
    ]

    refined = [
        make_result(
            "ACTIVE-WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    statuses = {
        item["status"]
        for item in result["results"]
    }

    assert statuses == {
        "Active",
    }

    ids = {
        item["chunk_id"]
        for item in result["results"]
    }

    assert "DRAFT-WORKFORCE" not in ids


def test_superseded_evidence_excluded(
    monkeypatch,
):
    initial = [
        make_result(
            "ACTIVE-BED",
            "Bed capacity pressure.",
        )
    ]

    refined = [
        make_result(
            "OLD-WORKFORCE",
            "Workforce pressure and staffing gaps.",
            status="Superseded",
        )
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert all(
        item["status"] == "Active"
        for item in result["results"]
    )

    assert (
        result["audit"]["stop_reason"]
        == "NO_COVERAGE_IMPROVEMENT"
    )


def test_archived_evidence_excluded(
    monkeypatch,
):
    initial = [
        make_result(
            "ACTIVE-BED",
            "Bed capacity pressure.",
        )
    ]

    refined = [
        make_result(
            "ARCHIVED-WORKFORCE",
            "Workforce pressure and staffing gaps.",
            status="Archived",
        )
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert all(
        item["status"] == "Active"
        for item in result["results"]
    )


def test_no_improvement_preserves_original_evidence(
    monkeypatch,
):
    initial = [
        make_result(
            "ORIGINAL",
            "Bed capacity pressure.",
        )
    ]

    refined = [
        make_result(
            "IRRELEVANT",
            "General administrative information.",
        )
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert [
        item["chunk_id"]
        for item in result["results"]
    ] == [
        "ORIGINAL",
    ]

    assert (
        result["audit"]["stop_reason"]
        == "NO_COVERAGE_IMPROVEMENT"
    )


def test_duplicate_chunk_is_not_added_twice(
    monkeypatch,
):
    original = make_result(
        "SAME",
        "Bed capacity pressure.",
    )

    initial = [
        original,
    ]

    refined = [
        {
            **original,
            "text": (
                "Bed capacity pressure and workforce pressure."
            ),
        }
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    chunk_ids = [
        item["chunk_id"]
        for item in result["results"]
    ]

    assert chunk_ids.count(
        "SAME"
    ) == 1


def test_final_evidence_never_exceeds_final_k(
    monkeypatch,
):
    initial = [
        make_result(
            "BED-1",
            "Bed capacity pressure.",
        ),
        make_result(
            "BED-2",
            "Hospital beds and capacity pressure.",
        ),
    ]

    refined = [
        make_result(
            "WORKFORCE-1",
            "Workforce pressure and staffing gaps.",
        ),
        make_result(
            "WORKFORCE-2",
            "Staffing gaps and workforce shortages.",
        ),
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert len(
        result["results"]
    ) <= 2


def test_refined_evidence_is_assessed_against_original_question(
    monkeypatch,
):
    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    refined = [
        make_result(
            "WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    final_matched = set(
        result["audit"][
            "final_evidence"
        ][
            "matched_query_terms"
        ]
    )

    assert "bed_capacity" in final_matched
    assert "workforce" in final_matched


def test_current_external_hard_block_does_not_refine(
    monkeypatch,
):
    initial = [
        make_result(
            "WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result, calls = run_agentic(
        query=(
            "What is the current rate for staffing "
            "pressure?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
    )

    assert len(calls) == 1

    assert (
        result["audit"]["stop_reason"]
        == "NO_RECOVERABLE_GAP"
    )


def test_precedence_hard_block_does_not_refine(
    monkeypatch,
):
    initial = [
        make_result(
            "ESCALATION",
            "Operational escalation policy guidance.",
        )
    ]

    result, calls = run_agentic(
        query=(
            "Which operational escalation policy "
            "takes precedence?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
    )

    assert len(calls) == 1

    assert (
        result["audit"]["stop_reason"]
        == "NO_RECOVERABLE_GAP"
    )


def test_blank_refined_query_stops_safely(
    monkeypatch,
):
    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    def blank_refiner(
        original_query,
        diagnostics,
    ):
        return "   "

    result, calls = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
        query_refiner=blank_refiner,
    )

    assert len(calls) == 1

    assert (
        result["audit"]["stop_reason"]
        == "REFINED_QUERY_INVALID"
    )


def test_duplicate_refined_query_stops_safely(
    monkeypatch,
):
    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    def duplicate_refiner(
        original_query,
        diagnostics,
    ):
        return original_query

    result, calls = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
        ],
        query_refiner=duplicate_refiner,
    )

    assert len(calls) == 1

    assert (
        result["audit"]["stop_reason"]
        == "REFINED_QUERY_INVALID"
    )


def test_refiner_failure_is_explicit(
    monkeypatch,
):
    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    def failing_refiner(
        original_query,
        diagnostics,
    ):
        raise RuntimeError(
            "simulated refiner failure"
        )

    with pytest.raises(
        RuntimeError,
        match="query refiner failed",
    ):
        run_agentic(
            query=(
                "How should staffing and bed capacity "
                "pressure be managed?"
            ),
            monkeypatch=monkeypatch,
            retrieval_outputs=[
                initial,
            ],
            query_refiner=failing_refiner,
        )


def test_refined_retrieval_failure_is_explicit(
    monkeypatch,
):
    call_count = 0

    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    def fake_hybrid_search(
        **kwargs,
    ):
        nonlocal call_count

        call_count += 1

        if call_count == 1:
            return initial

        raise RuntimeError(
            "simulated retrieval failure"
        )

    monkeypatch.setattr(
        agentic_module,
        "hybrid_search",
        fake_hybrid_search,
    )

    with pytest.raises(
        RuntimeError,
        match="refined retrieval failed",
    ):
        bounded_agentic_retrieval(
            query=(
                "How should staffing and bed capacity "
                "pressure be managed?"
            ),
            chunks=[],
            embedded_chunks=[],
            model=object(),
            embedding_model="test-model",
            final_k=2,
            max_rounds=2,
        )


def test_empty_initial_results_are_handled(
    monkeypatch,
):
    refined = [
        make_result(
            "WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result, calls = run_agentic(
        query=(
            "How should staffing pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            [],
            refined,
        ],
        final_k=2,
    )

    assert len(calls) == 2

    assert (
        result["audit"]["retrieval_call_count"]
        == 2
    )


def test_audit_trail_is_deterministic(
    monkeypatch,
):
    initial = [
        make_result(
            "BED",
            "Bed capacity pressure.",
        )
    ]

    refined = [
        make_result(
            "WORKFORCE",
            "Workforce pressure and staffing gaps.",
        )
    ]

    result_one, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    result_two, _ = run_agentic(
        query=(
            "How should staffing and bed capacity "
            "pressure be managed?"
        ),
        monkeypatch=monkeypatch,
        retrieval_outputs=[
            initial,
            refined,
        ],
        final_k=2,
    )

    assert (
        result_one["audit"]
        == result_two["audit"]
    )