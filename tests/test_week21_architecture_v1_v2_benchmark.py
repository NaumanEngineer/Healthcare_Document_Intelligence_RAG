from src.evaluation import (
    run_week21_architecture_v1_v2_benchmark as benchmark,
)


def _case(
    *,
    expected_document_id="DOC-001",
    expected_abstention=False,
):
    return {
        "query_id": "TEST",
        "question": "Explain staffing escalation",
        "expected_document_id": expected_document_id,
        "expected_abstention": expected_abstention,
    }


def _result(
    *,
    document_id="DOC-001",
    status="Active",
    chunk_id="DOC-001::P1",
):
    return {
        "document_id": document_id,
        "status": status,
        "chunk_id": chunk_id,
    }


def test_document_ids_preserve_unique_order():
    results = [
        _result(
            document_id="DOC-001",
            chunk_id="A",
        ),
        _result(
            document_id="DOC-001",
            chunk_id="B",
        ),
        _result(
            document_id="DOC-002",
            chunk_id="C",
        ),
    ]

    assert benchmark._document_ids(
        results
    ) == [
        "DOC-001",
        "DOC-002",
    ]


def test_chunk_ids_preserve_order():
    results = [
        _result(
            chunk_id="A",
        ),
        _result(
            chunk_id="B",
        ),
    ]

    assert benchmark._chunk_ids(
        results
    ) == [
        "A",
        "B",
    ]


def test_expected_abstention_auto_answer_is_flagged_unsafe():
    case = _case(
        expected_abstention=True,
    )

    governance = {
        "decision": "AUTO_ANSWER",
    }

    assert (
        benchmark
        ._governance_is_unsafe_for_expected_abstention(
            case,
            governance,
        )
        is True
    )


def test_expected_abstention_review_is_not_flagged_unsafe():
    case = _case(
        expected_abstention=True,
    )

    governance = {
        "decision": "REVIEW_REQUIRED",
    }

    assert (
        benchmark
        ._governance_is_unsafe_for_expected_abstention(
            case,
            governance,
        )
        is False
    )


def test_non_active_auto_answer_is_flagged_unsafe():
    results = [
        _result(
            status="Draft",
        )
    ]

    governance = {
        "decision": "AUTO_ANSWER",
    }

    assert (
        benchmark
        ._unsafe_lifecycle_auto_answer(
            results,
            governance,
        )
        is True
    )


def test_non_active_review_is_not_flagged_unsafe():
    results = [
        _result(
            status="Draft",
        )
    ]

    governance = {
        "decision": "REVIEW_REQUIRED",
    }

    assert (
        benchmark
        ._unsafe_lifecycle_auto_answer(
            results,
            governance,
        )
        is False
    )


def test_comparison_summary_counts_v2_top1_win():
    records = [
        {
            "architecture_v1": {
                "top1_success": False,
                "topk_success": False,
                "abstention_success": None,
            },
            "architecture_v2": {
                "top1_success": True,
                "topk_success": True,
                "abstention_success": None,
            },
            "evidence_sufficiency": {
                "architecture_v1": {
                    "sufficient": False,
                },
                "architecture_v2": {
                    "sufficient": True,
                },
            },
        }
    ]

    summary = (
        benchmark._comparison_summary(
            records
        )
    )

    assert summary[
        "top1"
    ][
        "v2_wins"
    ] == 1

    assert summary[
        "top1"
    ][
        "v2_losses"
    ] == 0

    assert summary[
        "topk"
    ][
        "v2_wins"
    ] == 1

    assert summary[
        "evidence_sufficiency"
    ][
        "v2_wins"
    ] == 1


def test_comparison_summary_counts_v2_abstention_loss():
    records = [
        {
            "architecture_v1": {
                "top1_success": None,
                "topk_success": None,
                "abstention_success": True,
            },
            "architecture_v2": {
                "top1_success": None,
                "topk_success": None,
                "abstention_success": False,
            },
            "evidence_sufficiency": {
                "architecture_v1": {
                    "sufficient": False,
                },
                "architecture_v2": {
                    "sufficient": True,
                },
            },
        }
    ]

    summary = (
        benchmark._comparison_summary(
            records
        )
    )

    assert summary[
        "abstention"
    ][
        "v2_losses"
    ] == 1


def test_route_cost_details_reads_rescue_rrf_cost():
    output = {
        "route": "HYBRID_RESCUE",
        "hybrid_call_count": 1,
        "route_audit": {
            "additional_rrf_pool_call_count": 1,
        },
    }

    cost = (
        benchmark._route_cost_details(
            output
        )
    )

    assert cost[
        "hybrid_call_count"
    ] == 1

    assert cost[
        "rrf_pool_call_count"
    ] == 1

    assert cost[
        "relationship_expansion_used"
    ] == 0


def test_route_cost_details_reads_relationship_expansion():
    output = {
        "route": "RELATIONSHIP_AWARE",
        "hybrid_call_count": 1,
        "route_audit": {
            "expansion_count": 2,
        },
    }

    cost = (
        benchmark._route_cost_details(
            output
        )
    )

    assert cost[
        "relationship_expansion_used"
    ] == 1

    assert cost[
        "rrf_pool_call_count"
    ] == 0