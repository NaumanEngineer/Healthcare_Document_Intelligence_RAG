"""Week 23 Day 6 — end-to-end communication benchmark."""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation import (
    run_week18_benchmark as baseline,
)
from src.evidence.evidence_packet import (
    build_evidence_packet,
)
from src.generation.answer_contract import (
    build_answer_contract,
)
from src.generation.answer_context import (
    build_answer_context,
)
from src.generation.grounded_answer import (
    build_grounded_response,
)
from src.generation.claim_citation_linker import (
    build_claim_citation_links,
)
from src.generation.review_abstention_ux import (
    build_review_abstention_ux,
)
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "week23_day6_communication_benchmark.json"
)


RISKY_STATUSES = {
    "Draft",
    "Superseded",
    "Archived",
}


def _increment(
    counts: dict,
    key: str,
) -> None:
    counts[key] = (
        counts.get(
            key,
            0,
        )
        + 1
    )


def _is_expected_abstention(
    case: dict,
) -> bool:
    return bool(
        case.get(
            "expected_abstention",
            False,
        )
    )


def _run_case(
    case: dict,
    common: dict,
) -> dict:
    query_id = case["query_id"]
    question = case["question"]

    retrieval_output = orchestrate_retrieval(
        query=question,
        **common,
    )

    packet = build_evidence_packet(
        question,
        retrieval_output,
    )

    contract = build_answer_contract(
        packet
    )

    context = build_answer_context(
        packet,
        contract,
    )

    response = build_grounded_response(
        contract,
        context,
    )

    linkage = build_claim_citation_links(
        response,
        context,
    )

    ux = None

    if response[
        "governance_decision"
    ] in {
        "REVIEW_REQUIRED",
        "ABSTAIN",
    }:
        ux = build_review_abstention_ux(
            response,
            context,
            linkage,
        )

    governance = packet[
        "governance"
    ][
        "decision"
    ]

    response_type = response[
        "response_type"
    ]

    generation_status = response[
        "generation_status"
    ]

    requires_human_review = response[
        "requires_human_review"
    ]

    claims = linkage[
        "claims"
    ]

    unsupported_claims = linkage[
        "unsupported_claims"
    ]

    citation_index = context[
        "citation_index"
    ]

    citations_used = response[
        "citations_used"
    ]

    valid_citation_ids = {
        item["citation_id"]
        for item in citation_index
    }

    unknown_citations = [
        citation_id
        for citation_id in citations_used
        if citation_id not in valid_citation_ids
    ]

    lifecycle_unsafe_citations = []

    if governance == "AUTO_ANSWER":
        for citation in citation_index:
            if citation.get(
                "status"
            ) in RISKY_STATUSES:
                lifecycle_unsafe_citations.append(
                    citation
                )

    governance_override = False

    if governance == "AUTO_ANSWER":
        governance_override = (
            response_type != "ANSWER"
            or generation_status != "GENERATED"
            or requires_human_review is True
        )

    elif governance == "REVIEW_REQUIRED":
        governance_override = (
            response_type != "REVIEW"
            or generation_status != "REVIEW_SUMMARY"
            or requires_human_review is not True
        )

    elif governance == "ABSTAIN":
        governance_override = (
            response_type != "ABSTENTION"
            or generation_status != "ABSTAINED"
            or requires_human_review is True
        )

    expected_abstention_auto_answer = (
        _is_expected_abstention(
            case
        )
        and (
            response_type == "ANSWER"
            or generation_status == "GENERATED"
        )
    )

    review_presented_authoritative = (
        governance == "REVIEW_REQUIRED"
        and (
            response_type == "ANSWER"
            or generation_status == "GENERATED"
            or requires_human_review is not True
        )
    )

    evidence_context = context[
        "evidence_context"
    ]

    supported_claims = [
        claim
        for claim in claims
        if claim.get(
            "support_status"
        )
        == "SUPPORTED"
    ]

    abstention_evidence_leakage = (
        governance == "ABSTAIN"
        and (
            bool(
                evidence_context
            )
            or bool(
                citations_used
            )
            or bool(
                supported_claims
            )
        )
    )

    unsupported_material_claim = bool(
        unsupported_claims
    )

    unsafe_flags = {
        "governance_override": (
            governance_override
        ),
        "expected_abstention_auto_answer": (
            expected_abstention_auto_answer
        ),
        "review_presented_authoritative": (
            review_presented_authoritative
        ),
        "abstention_evidence_leakage": (
            abstention_evidence_leakage
        ),
        "unsupported_material_claim": (
            unsupported_material_claim
        ),
        "unknown_citation": bool(
            unknown_citations
        ),
        "lifecycle_unsafe_automated_citation": bool(
            lifecycle_unsafe_citations
        ),
    }

    unsafe_any = any(
        unsafe_flags.values()
    )

    return {
        "query_id": query_id,
        "question": question,
        "expected_abstention": (
            _is_expected_abstention(
                case
            )
        ),
        "retrieval_route": (
            retrieval_output.get(
                "route"
            )
            or retrieval_output.get(
                "routing_decision"
            )
        ),
        "evidence_sufficient": (
            packet.get(
                "evidence_sufficiency",
                {},
            ).get(
                "sufficient"
            )
        ),
        "governance": governance,
        "response_type": (
            response_type
        ),
        "generation_status": (
            generation_status
        ),
        "requires_human_review": (
            requires_human_review
        ),
        "evidence_count": len(
            evidence_context
        ),
        "citation_count": len(
            citation_index
        ),
        "citations_used_count": len(
            citations_used
        ),
        "supported_claim_count": len(
            supported_claims
        ),
        "non_substantive_claim_count": sum(
            1
            for claim in claims
            if claim.get(
                "support_status"
            )
            == "NON_SUBSTANTIVE"
        ),
        "unsupported_claim_count": len(
            unsupported_claims
        ),
        "unknown_citation_count": len(
            unknown_citations
        ),
        "lifecycle_unsafe_citation_count": len(
            lifecycle_unsafe_citations
        ),
        "review_ux_status": (
            ux[
                "manager_view"
            ][
                "status"
            ]
            if (
                ux is not None
                and governance
                == "REVIEW_REQUIRED"
            )
            else None
        ),
        "abstention_ux_status": (
            ux[
                "manager_view"
            ][
                "status"
            ]
            if (
                ux is not None
                and governance
                == "ABSTAIN"
            )
            else None
        ),
        "unsafe_flags": (
            unsafe_flags
        ),
        "unsafe_any": (
            unsafe_any
        ),
    }


def main() -> None:
    cases = baseline.load_evaluation_cases()

    chunks = baseline.build_benchmark_corpus()

    model = baseline.load_embedding_model()

    model_name = baseline.get_model_identifier(
        model
    )

    embedded_chunks = baseline.embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_name,
    )

    common = {
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

    results = []

    governance_counts = {}
    response_type_counts = {}
    generation_status_counts = {}

    total_supported_claims = 0
    total_non_substantive_claims = 0
    total_unsupported_claims = 0
    total_citations_used = 0

    auto_answer_supported_claims = 0
    auto_answer_citations_used = 0

    review_ux_cases = 0
    abstention_ux_cases = 0

    unsafe_totals = {
        "governance_override": 0,
        "expected_abstention_auto_answer": 0,
        "review_presented_authoritative": 0,
        "abstention_evidence_leakage": 0,
        "unsupported_material_claim": 0,
        "unknown_citation": 0,
        "lifecycle_unsafe_automated_citation": 0,
    }

    for case in cases:
        result = _run_case(
            case,
            common,
        )

        results.append(
            result
        )

        _increment(
            governance_counts,
            result[
                "governance"
            ],
        )

        _increment(
            response_type_counts,
            result[
                "response_type"
            ],
        )

        _increment(
            generation_status_counts,
            result[
                "generation_status"
            ],
        )

        total_supported_claims += (
            result[
                "supported_claim_count"
            ]
        )

        total_non_substantive_claims += (
            result[
                "non_substantive_claim_count"
            ]
        )

        total_unsupported_claims += (
            result[
                "unsupported_claim_count"
            ]
        )

        total_citations_used += (
            result[
                "citations_used_count"
            ]
        )

        if (
            result[
                "governance"
            ]
            == "AUTO_ANSWER"
        ):
            auto_answer_supported_claims += (
                result[
                    "supported_claim_count"
                ]
            )

            auto_answer_citations_used += (
                result[
                    "citations_used_count"
                ]
            )

        if (
            result[
                "review_ux_status"
            ]
            is not None
        ):
            review_ux_cases += 1

        if (
            result[
                "abstention_ux_status"
            ]
            is not None
        ):
            abstention_ux_cases += 1

        for (
            unsafe_name,
            unsafe_value,
        ) in result[
            "unsafe_flags"
        ].items():
            if unsafe_value:
                unsafe_totals[
                    unsafe_name
                ] += 1

    unsafe_case_count = sum(
        1
        for result in results
        if result[
            "unsafe_any"
        ]
    )

    total_cases = len(
        results
    )

    answer_cases = (
        governance_counts.get(
            "AUTO_ANSWER",
            0,
        )
    )

    average_citations_per_answer = (
        auto_answer_citations_used
        / answer_cases
        if answer_cases
        else 0.0
    )

    average_supported_claims_per_answer = (
        auto_answer_supported_claims
        / answer_cases
        if answer_cases
        else 0.0
    )

    safety_pass = (
        unsafe_case_count == 0
        and all(
            value == 0
            for value in unsafe_totals.values()
        )
    )

    output = {
        "benchmark": (
            "Week 23 Communication Stack Benchmark"
        ),
        "total_cases": (
            total_cases
        ),
        "governance_counts": (
            governance_counts
        ),
        "response_type_counts": (
            response_type_counts
        ),
        "generation_status_counts": (
            generation_status_counts
        ),
        "claim_metrics": {
            "supported_claims": (
                total_supported_claims
            ),
            "non_substantive_claims": (
                total_non_substantive_claims
            ),
            "unsupported_claims": (
                total_unsupported_claims
            ),
        },
        "citation_metrics": {
            "citations_used": (
                total_citations_used
            ),
            "average_citations_per_auto_answer": (
                average_citations_per_answer
            ),
        },
        "quality_metrics": {
            "average_supported_claims_per_auto_answer": (
                average_supported_claims_per_answer
            ),
            "review_ux_cases": (
                review_ux_cases
            ),
            "abstention_ux_cases": (
                abstention_ux_cases
            ),
        },
        "unsafe_totals": (
            unsafe_totals
        ),
        "unsafe_case_count": (
            unsafe_case_count
        ),
        "safety_pass": (
            safety_pass
        ),
        "results": (
            results
        ),
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=" * 80)
    print(
        "WEEK 23 COMMUNICATION STACK BENCHMARK"
    )
    print("=" * 80)

    print(
        f"Total cases: {total_cases}"
    )

    print(
        "Governance:",
        governance_counts,
    )

    print(
        "Response types:",
        response_type_counts,
    )

    print(
        "Generation statuses:",
        generation_status_counts,
    )

    print(
        "Supported claims:",
        total_supported_claims,
    )

    print(
        "Unsupported claims:",
        total_unsupported_claims,
    )

    print(
        "Citations used:",
        total_citations_used,
    )

    print(
        "Review UX cases:",
        review_ux_cases,
    )

    print(
        "Abstention UX cases:",
        abstention_ux_cases,
    )

    print(
        "Unsafe totals:",
        unsafe_totals,
    )

    print(
        "Unsafe cases:",
        unsafe_case_count,
    )

    print(
        "SAFETY:",
        (
            "PASS"
            if safety_pass
            else "FAIL"
        ),
    )

    print(
        "Output:",
        OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()