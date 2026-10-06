from __future__ import annotations

import src.evaluation.run_week18_benchmark as baseline

from src.governance.evidence_set_relationship import (
    validate_evidence_set_relationship,
)
from src.retrieval.relationship_aware_retrieval import (
    expand_results_with_relationships,
)


def main():
    chunks = baseline.build_benchmark_corpus()

    initial_results = [
        chunk
        for chunk in chunks
        if chunk.get("document_id") == "DOC-011"
    ][:1]

    if not initial_results:
        raise RuntimeError(
            "No DOC-011 chunk found in corpus"
        )

    expanded = expand_results_with_relationships(
        initial_results,
        chunks,
        relationship_type="COMPLEMENTS",
        max_related_chunks=2,
    )

    evidence_items = expanded["results"]

    print("=" * 80)
    print("EXPANDED EVIDENCE")
    print("=" * 80)

    for item in evidence_items:
        print(
            item.get("chunk_id"),
            "|",
            item.get("document_id"),
            "|",
            item.get("status"),
        )

    print()
    print("=" * 80)
    print("GOVERNANCE VALIDATION")
    print("=" * 80)

    relationship_result = (
        validate_evidence_set_relationship(
            "COMPLEMENTS",
            evidence_items,
        )
    )

    print(
        "DECISION:",
        relationship_result.get("decision"),
    )

    print(
        "DOCUMENT IDS:",
        relationship_result.get("document_ids"),
    )

    print(
        "EVIDENCE STATUS:",
        relationship_result.get("evidence_status"),
    )

    print(
        "MATCHED TERMS:",
        relationship_result.get(
            "matched_relationship_terms"
        ),
    )

    print(
        "REASON:",
        relationship_result.get("reason"),
    )

    print()
    print("=" * 80)
    print("CONTROL CHECK: FALSE RELATIONSHIP TYPE")
    print("=" * 80)

    false_relationship_result = (
        validate_evidence_set_relationship(
            "CONFLICT",
            evidence_items,
        )
    )

    print(
        "DECISION:",
        false_relationship_result.get("decision"),
    )

    print(
        "MATCHED TERMS:",
        false_relationship_result.get(
            "matched_relationship_terms"
        ),
    )

    print(
        "REASON:",
        false_relationship_result.get("reason"),
    )


if __name__ == "__main__":
    main()