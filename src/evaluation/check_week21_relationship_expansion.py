from __future__ import annotations

import src.evaluation.run_week18_benchmark as baseline

from src.retrieval.relationship_aware_retrieval import (
    expand_results_with_relationships,
)


def main():
    print(
        "Building benchmark corpus..."
    )

    chunks = baseline.build_benchmark_corpus()

    initial_results = [
        chunk
        for chunk in chunks
        if chunk.get(
            "document_id"
        ) == "DOC-011"
    ][:1]

    if not initial_results:
        raise RuntimeError(
            "No DOC-011 chunk found in corpus"
        )

    print()
    print(
        "INITIAL RESULT"
    )

    for item in initial_results:
        print(
            item.get("chunk_id"),
            "|",
            item.get("document_id"),
            "|",
            item.get("title"),
            "|",
            item.get("status"),
        )

    result = (
        expand_results_with_relationships(
            initial_results,
            chunks,
            relationship_type="COMPLEMENTS",
            max_related_chunks=2,
        )
    )

    print()
    print(
        "=" * 80
    )
    print(
        "RELATIONSHIP EXPANSION"
    )
    print(
        "=" * 80
    )

    print(
        "STOP:",
        result[
            "audit"
        ][
            "stop_reason"
        ],
    )

    print(
        "INITIAL DOCUMENT IDS:",
        result[
            "audit"
        ][
            "initial_document_ids"
        ],
    )

    print(
        "RELATED DOCUMENT IDS:",
        result[
            "audit"
        ][
            "related_document_ids"
        ],
    )

    print(
        "CANDIDATE CHUNKS:",
        result[
            "audit"
        ][
            "candidate_chunk_ids"
        ],
    )

    print(
        "ACCEPTED CHUNKS:",
        result[
            "audit"
        ][
            "accepted_chunk_ids"
        ],
    )

    print()
    print(
        "FINAL RESULTS"
    )

    for item in result[
        "results"
    ]:
        print(
            item.get("chunk_id"),
            "|",
            item.get("document_id"),
            "|",
            item.get("title"),
            "|",
            item.get("status"),
        )

    print()
    print(
        "RELATIONSHIP RECORDS"
    )

    for relationship in result[
        "audit"
    ][
        "relationship_records"
    ]:
        print(
            relationship
        )


if __name__ == "__main__":
    main()