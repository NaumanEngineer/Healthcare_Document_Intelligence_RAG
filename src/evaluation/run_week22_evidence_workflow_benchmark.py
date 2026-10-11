"""Week 22 Day 6 — end-to-end Evidence Workflow benchmark.

Primary question:

Can Architecture v2 turn retrieved evidence into a structured,
traceable, lifecycle-aware, precedence-aware and manager-readable
evidence workflow without creating unsafe manager-ready outcomes?

The frozen Week 18 evaluation cases, corpus, embedding model and
retrieval thresholds are reused.

This remains a controlled synthetic benchmark.
It is not production NHS performance evidence.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evidence.evidence_packet import (
    build_evidence_packet,
)
from src.evidence.manager_evidence_brief import (
    BRIEF_READY,
    build_manager_evidence_brief,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


OUTPUT_PATH = (
    Path(
        baseline.PROJECT_ROOT
    )
    / "outputs"
    / "week22_day6_evidence_workflow_benchmark.json"
)


def _require_mapping(
    value: Any,
    field_name: str,
) -> dict:
    """Require a dictionary."""

    if not isinstance(
        value,
        dict,
    ):
        raise TypeError(
            f"{field_name} must be a dictionary"
        )

    return value


def _build_common_runtime(
    chunks: list[dict],
    embedded_chunks: list[dict],
    model: Any,
    model_name: str,
) -> dict:
    """Build shared retrieval runtime arguments."""

    return {
        "chunks": chunks,
        "embedded_chunks": embedded_chunks,
        "model": model,
        "embedding_model": model_name,
        "semantic_k": baseline.SEMANTIC_K,
        "keyword_k": baseline.KEYWORD_K,
        "final_k": baseline.FINAL_K,
        "semantic_min_similarity": (
            baseline.SEMANTIC_MIN_SIMILARITY
        ),
        "keyword_min_score": (
            baseline.KEYWORD_MIN_SCORE
        ),
        "min_rrf_score": (
            baseline.MIN_RRF_SCORE
        ),
    }


def _extract_case_record(
    case: dict,
    packet: dict,
    brief: dict,
) -> dict:
    """Create one compact benchmark record."""

    retrieval = _require_mapping(
        packet.get(
            "retrieval",
            {},
        ),
        "packet.retrieval",
    )

    evidence_sufficiency = (
        _require_mapping(
            packet.get(
                "evidence_sufficiency",
                {},
            ),
            "packet.evidence_sufficiency",
        )
    )

    provenance_summary = (
        _require_mapping(
            packet.get(
                "provenance_summary",
                {},
            ),
            "packet.provenance_summary",
        )
    )

    lifecycle_summary = (
        _require_mapping(
            packet.get(
                "lifecycle_summary",
                {},
            ),
            "packet.lifecycle_summary",
        )
    )

    precedence_assessment = (
        _require_mapping(
            packet.get(
                "precedence_assessment",
                {},
            ),
            "packet.precedence_assessment",
        )
    )

    governance = _require_mapping(
        packet.get(
            "governance",
            {},
        ),
        "packet.governance",
    )

    expected_abstention = bool(
        case.get(
            "expected_abstention",
            False,
        )
    )

    brief_status = brief.get(
        "brief_status"
    )

    governance_decision = (
        governance.get(
            "decision"
        )
    )

    precedence_decision = (
        precedence_assessment.get(
            "decision"
        )
    )

    evidence_sufficient = (
        evidence_sufficiency.get(
            "sufficient"
        )
        is True
    )

    evidence_count = packet.get(
        "evidence_count",
        0,
    )

    unsafe_ready_expected_abstention = (
        expected_abstention
        and brief_status
        == BRIEF_READY
    )

    unsafe_ready_governance = (
        brief_status
        == BRIEF_READY
        and governance_decision
        != "AUTO_ANSWER"
    )

    unsafe_ready_precedence = (
        brief_status
        == BRIEF_READY
        and precedence_decision
        != "SAFE_TO_COMBINE"
    )

    unsafe_ready_insufficient = (
        brief_status
        == BRIEF_READY
        and (
            evidence_sufficient
            is not True
            or evidence_count
            <= 0
        )
    )

    unsafe_manager_ready = any(
        (
            unsafe_ready_expected_abstention,
            unsafe_ready_governance,
            unsafe_ready_precedence,
            unsafe_ready_insufficient,
        )
    )

    return {
        "query_id": (
            case.get(
                "query_id"
            )
        ),
        "question": (
            case.get(
                "question"
            )
        ),
        "expected": {
            "expected_document_id": (
                case.get(
                    "expected_document_id"
                )
            ),
            "expected_abstention": (
                expected_abstention
            ),
        },
        "retrieval": {
            "route": (
                retrieval.get(
                    "route"
                )
            ),
            "stop_reason": (
                retrieval.get(
                    "stop_reason"
                )
            ),
        },
        "evidence": {
            "sufficient": (
                evidence_sufficient
            ),
            "evidence_count": (
                evidence_count
            ),
            "document_ids": (
                packet.get(
                    "document_ids",
                    [],
                )
            ),
        },
        "provenance": {
            "record_count": (
                provenance_summary.get(
                    "record_count",
                    0,
                )
            ),
            "all_verified": (
                provenance_summary.get(
                    "all_verified"
                )
                is True
            ),
        },
        "lifecycle": {
            "all_active": (
                lifecycle_summary.get(
                    "all_active"
                )
                is True
            ),
            "status_counts": (
                lifecycle_summary.get(
                    "status_counts",
                    {},
                )
            ),
        },
        "precedence": {
            "decision": (
                precedence_decision
            ),
            "reason": (
                precedence_assessment.get(
                    "reason"
                )
            ),
        },
        "governance": {
            "decision": (
                governance_decision
            ),
            "requires_human_review": (
                governance.get(
                    "requires_human_review"
                )
                is True
            ),
            "may_generate_answer": (
                governance.get(
                    "may_generate_answer"
                )
                is True
            ),
        },
        "manager_brief": {
            "brief_status": (
                brief_status
            ),
            "manager_action": (
                brief.get(
                    "manager_action"
                )
            ),
        },
        "safety": {
            "unsafe_ready_expected_abstention": (
                unsafe_ready_expected_abstention
            ),
            "unsafe_ready_governance": (
                unsafe_ready_governance
            ),
            "unsafe_ready_precedence": (
                unsafe_ready_precedence
            ),
            "unsafe_ready_insufficient": (
                unsafe_ready_insufficient
            ),
            "unsafe_manager_ready": (
                unsafe_manager_ready
            ),
        },
    }


def _counter(
    records: list[dict],
    path: tuple[str, ...],
) -> dict:
    """Count values at a nested record path."""

    counter = Counter()

    for record in records:
        value: Any = record

        for key in path:
            if not isinstance(
                value,
                dict,
            ):
                value = None
                break

            value = value.get(
                key
            )

        counter[
            str(
                value
            )
        ] += 1

    return dict(
        sorted(
            counter.items()
        )
    )


def _build_summary(
    cases: list[dict],
    records: list[dict],
    chunks: list[dict],
) -> dict:
    """Build benchmark-level Week 22 summary."""

    expected_abstention_cases = sum(
        1
        for case in cases
        if case.get(
            "expected_abstention",
            False,
        )
    )

    sufficient_cases = sum(
        1
        for record in records
        if record[
            "evidence"
        ][
            "sufficient"
        ]
        is True
    )

    evidence_bearing_cases = sum(
        1
        for record in records
        if record[
            "evidence"
        ][
            "evidence_count"
        ]
        > 0
    )

    fully_verified_cases = sum(
        1
        for record in records
        if (
            record[
                "evidence"
            ][
                "evidence_count"
            ]
            > 0
            and record[
                "provenance"
            ][
                "all_verified"
            ]
            is True
        )
    )

    all_active_cases = sum(
        1
        for record in records
        if (
            record[
                "evidence"
            ][
                "evidence_count"
            ]
            > 0
            and record[
                "lifecycle"
            ][
                "all_active"
            ]
            is True
        )
    )

    unsafe_expected_abstention = sum(
        1
        for record in records
        if record[
            "safety"
        ][
            "unsafe_ready_expected_abstention"
        ]
        is True
    )

    unsafe_governance = sum(
        1
        for record in records
        if record[
            "safety"
        ][
            "unsafe_ready_governance"
        ]
        is True
    )

    unsafe_precedence = sum(
        1
        for record in records
        if record[
            "safety"
        ][
            "unsafe_ready_precedence"
        ]
        is True
    )

    unsafe_insufficient = sum(
        1
        for record in records
        if record[
            "safety"
        ][
            "unsafe_ready_insufficient"
        ]
        is True
    )

    unsafe_total = sum(
        1
        for record in records
        if record[
            "safety"
        ][
            "unsafe_manager_ready"
        ]
        is True
    )

    return {
        "dataset": {
            "total_cases": len(
                cases
            ),
            "corpus_chunks": len(
                chunks
            ),
            "expected_abstention_cases": (
                expected_abstention_cases
            ),
        },
        "evidence_workflow": {
            "sufficient_cases": (
                sufficient_cases
            ),
            "evidence_bearing_cases": (
                evidence_bearing_cases
            ),
            "fully_verified_evidence_cases": (
                fully_verified_cases
            ),
            "all_active_evidence_cases": (
                all_active_cases
            ),
        },
        "retrieval_routes": _counter(
            records,
            (
                "retrieval",
                "route",
            ),
        ),
        "precedence_decisions": _counter(
            records,
            (
                "precedence",
                "decision",
            ),
        ),
        "governance_decisions": _counter(
            records,
            (
                "governance",
                "decision",
            ),
        ),
        "manager_brief_statuses": _counter(
            records,
            (
                "manager_brief",
                "brief_status",
            ),
        ),
        "safety": {
            "unsafe_brief_ready_on_expected_abstention": (
                unsafe_expected_abstention
            ),
            "unsafe_brief_ready_when_governance_not_auto_answer": (
                unsafe_governance
            ),
            "unsafe_brief_ready_when_precedence_not_safe": (
                unsafe_precedence
            ),
            "unsafe_brief_ready_with_insufficient_evidence": (
                unsafe_insufficient
            ),
            "unsafe_manager_ready_total": (
                unsafe_total
            ),
        },
    }


def main():
    """Run the complete frozen Week 22 evidence workflow benchmark."""

    cases = baseline.load_evaluation_cases()

    chunks = baseline.build_benchmark_corpus()

    model = baseline.load_embedding_model()

    model_name = baseline.get_model_identifier(
        model
    )

    embedded_chunks = (
        baseline.embed_chunks(
            chunks=chunks,
            model=model,
            model_name=model_name,
        )
    )

    common = _build_common_runtime(
        chunks,
        embedded_chunks,
        model,
        model_name,
    )

    print(
        "=" * 80
    )

    print(
        "WEEK 22 DAY 6 — EVIDENCE WORKFLOW BENCHMARK"
    )

    print(
        "=" * 80
    )

    print(
        f"Evaluation cases: {len(cases)}"
    )

    print(
        f"Corpus chunks: {len(chunks)}"
    )

    print()

    records = []

    for index, case in enumerate(
        cases,
        start=1,
    ):
        query_id = case.get(
            "query_id",
            f"CASE-{index}",
        )

        question = case[
            "question"
        ]

        retrieval_output = (
            orchestrate_retrieval(
                query=question,
                **common,
            )
        )

        packet = build_evidence_packet(
            question,
            retrieval_output,
        )

        brief = (
            build_manager_evidence_brief(
                packet
            )
        )

        record = _extract_case_record(
            case,
            packet,
            brief,
        )

        records.append(
            record
        )

        print(
            f"{query_id} complete"
            f" | route={record['retrieval']['route']}"
            f" | evidence={record['evidence']['sufficient']}"
            f" | governance={record['governance']['decision']}"
            f" | brief={record['manager_brief']['brief_status']}"
            f" | unsafe={record['safety']['unsafe_manager_ready']}"
        )

    summary = _build_summary(
        cases,
        records,
        chunks,
    )

    output = {
        "benchmark_question": (
            "Can Architecture v2 turn retrieved evidence into a "
            "structured, traceable, lifecycle-aware, precedence-aware "
            "and manager-readable workflow without creating unsafe "
            "manager-ready outcomes?"
        ),
        "benchmark_type": (
            "Controlled synthetic evaluation"
        ),
        "model_name": (
            model_name
        ),
        "summary": (
            summary
        ),
        "records": (
            records
        ),
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()

    print(
        "=" * 80
    )

    print(
        "WEEK 22 SUMMARY"
    )

    print(
        "=" * 80
    )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print()

    print(
        "Output written to:"
    )

    print(
        OUTPUT_PATH
    )

    print()

    unsafe_total = (
        summary[
            "safety"
        ][
            "unsafe_manager_ready_total"
        ]
    )

    if unsafe_total == 0:
        print(
            "SAFETY RESULT: PASS — "
            "0 unsafe manager-ready outcomes."
        )

    else:
        print(
            "SAFETY RESULT: FAIL — "
            f"{unsafe_total} unsafe manager-ready "
            "outcome(s) detected."
        )


if __name__ == "__main__":
    main()