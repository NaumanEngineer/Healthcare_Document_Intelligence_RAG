from __future__ import annotations

import json
import re
from pathlib import Path

from src.preprocessing.build_chunks import (
    build_document_chunks,
)

from src.retrieval.embeddings import (
    load_embedding_model,
    embed_chunks,
    get_model_identifier,
)

from src.retrieval.semantic_search import (
    semantic_search,
)

from src.retrieval.keyword_search import (
    keyword_search,
)

from src.retrieval.hybrid_search import (
    hybrid_search,
)

from src.evaluation.retrieval_benchmark import (
    compare_methods_for_case,
    summarise_benchmark,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

EVALUATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "evaluation_cases.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "week18_retrieval_benchmark.json"
)


TARGET_CHARS = 1000
OVERLAP_CHARS = 150

SEMANTIC_K = 10
KEYWORD_K = 10
FINAL_K = 3

SEMANTIC_MIN_SIMILARITY = None
KEYWORD_MIN_SCORE = None
MIN_RRF_SCORE = None


def extract_document_id(
    file_path: Path,
) -> str:
    """
    Extract DOC-### from a filename.
    """

    match = re.search(
        r"(DOC-\d{3})",
        file_path.name,
        re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            f"Could not determine document ID from {file_path.name}"
        )

    return match.group(1).upper()


def parse_header_value(
    text: str,
    label: str,
    default: str,
) -> str:
    """
    Read a simple 'Label: value' line from a synthetic TXT file.
    """

    pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"

    match = re.search(
        pattern,
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return default


def split_text_with_overlap(
    text: str,
    target_chars: int = TARGET_CHARS,
    overlap_chars: int = OVERLAP_CHARS,
) -> list[str]:
    """
    Lightweight deterministic chunking for the Week 18 TXT
    lifecycle stress documents.

    PDFs continue to use the project's normal production
    chunking pipeline.
    """

    cleaned = " ".join(
        text.split()
    )

    if not cleaned:
        return []

    if len(cleaned) <= target_chars:
        return [cleaned]

    chunks = []

    start = 0

    while start < len(cleaned):
        end = min(
            start + target_chars,
            len(cleaned),
        )

        if end < len(cleaned):
            boundary = cleaned.rfind(
                " ",
                start,
                end,
            )

            if boundary > start:
                end = boundary

        chunk = cleaned[
            start:end
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= len(cleaned):
            break

        next_start = end - overlap_chars

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def build_txt_document_chunks(
    file_path: Path,
) -> list[dict]:
    """
    Build benchmark chunks from the synthetic Week 18 TXT
    lifecycle stress documents.
    """

    text = file_path.read_text(
        encoding="utf-8"
    )

    document_id = extract_document_id(
        file_path
    )

    version = parse_header_value(
        text,
        "Version",
        "1.0",
    )

    effective_date = parse_header_value(
        text,
        "Effective Date",
        "2026-01-01",
    )

    status = parse_header_value(
        text,
        "Status",
        "Active",
    )

    title = parse_header_value(
        text,
        "Title",
        file_path.stem.replace(
            "_",
            " ",
        ),
    )

    pieces = split_text_with_overlap(
        text=text,
    )

    chunks = []

    safe_version = version.replace(
        " ",
        "",
    )

    for index, piece in enumerate(
        pieces,
        start=1,
    ):
        chunks.append(
            {
                "chunk_id": (
                    f"{document_id}-"
                    f"V{safe_version}-"
                    f"P001-"
                    f"C{index:03d}"
                ),
                "document_id": document_id,
                "title": title,
                "document_type": (
                    "Synthetic Operational Document"
                ),
                "source_type": "Synthetic",
                "version": version,
                "effective_date": effective_date,
                "status": status,
                "source_file": file_path.name,
                "source_location": str(
                    file_path
                ),
                "page": 1,
                "chunk_number": index,
                "text": piece,
            }
        )

    return chunks


def build_benchmark_corpus() -> list[dict]:
    """
    Build chunks from all supported synthetic raw documents.

    PDFs:
        use the project's normal document chunking pipeline.

    TXT lifecycle stress documents:
        use a small deterministic benchmark adapter.
    """

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_DIR}"
        )

    all_chunks = []

    files = sorted(
        [
            path
            for path in RAW_DATA_DIR.iterdir()
            if path.suffix.lower()
            in {".pdf", ".txt"}
        ]
    )

    if not files:
        raise RuntimeError(
            "No PDF or TXT documents found in data/raw"
        )

    print(
        f"Found {len(files)} raw corpus files."
    )

    for file_path in files:
        document_id = extract_document_id(
            file_path
        )

        print(
            f"Loading {file_path.name}"
        )

        if (
            file_path.suffix.lower()
            == ".pdf"
        ):
            document_chunks = (
                build_document_chunks(
                    file_path=str(
                        file_path
                    ),
                    document_id=document_id,
                    target_chars=TARGET_CHARS,
                    overlap_chars=OVERLAP_CHARS,
                )
            )

        else:
            document_chunks = (
                build_txt_document_chunks(
                    file_path
                )
            )

        print(
            f"  -> {len(document_chunks)} chunks"
        )

        all_chunks.extend(
            document_chunks
        )

    if not all_chunks:
        raise RuntimeError(
            "Corpus produced zero chunks."
        )

    return all_chunks


def load_evaluation_cases() -> list[dict]:
    """
    Load the controlled Week 18 benchmark questions.
    """

    with EVALUATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(
            file
        )

    if not isinstance(
        cases,
        list,
    ):
        raise TypeError(
            "Evaluation dataset must contain a JSON list."
        )

    return cases


def safe_document_ids(
    results: list[dict],
) -> list[str]:
    """
    Convenience representation for console output.
    """

    ids = []

    for result in results:
        document_id = result.get(
            "document_id"
        )

        if (
            document_id
            and document_id not in ids
        ):
            ids.append(
                document_id
            )

    return ids


def run_benchmark() -> dict:
    """
    Execute the controlled Week 18 retrieval experiment.
    """

    print()
    print(
        "WEEK 18 RETRIEVAL BENCHMARK"
    )
    print(
        "=" * 50
    )

    cases = load_evaluation_cases()

    print(
        f"Evaluation cases: {len(cases)}"
    )

    chunks = build_benchmark_corpus()

    print(
        f"Total chunks: {len(chunks)}"
    )

    print()
    print(
        "Loading embedding model..."
    )

    model = load_embedding_model()

    model_identifier = (
        get_model_identifier(
            model
        )
    )

    print(
        f"Embedding model: {model_identifier}"
    )

    print()
    print(
        "Embedding corpus..."
    )

    embedded_chunks = embed_chunks(
        chunks=chunks,
        model=model,
        model_name=model_identifier,
    )

    print(
        f"Embedded chunks: {len(embedded_chunks)}"
    )

    case_results = []

    print()
    print(
        "Running benchmark..."
    )
    print()

    for case in cases:
        query_id = case[
            "query_id"
        ]

        question = case[
            "question"
        ]

        print(
            f"{query_id}: {question}"
        )

        semantic_results = (
            semantic_search(
                query=question,
                embedded_chunks=embedded_chunks,
                model=model,
                embedding_model=(
                    model_identifier
                ),
                candidate_k=SEMANTIC_K,
                final_k=FINAL_K,
                min_similarity=(
                    SEMANTIC_MIN_SIMILARITY
                ),
            )
        )

        keyword_results = (
            keyword_search(
                query=question,
                chunks=chunks,
                top_k=FINAL_K,
                min_score=(
                    KEYWORD_MIN_SCORE
                ),
            )
        )

        hybrid_results = (
            hybrid_search(
                query=question,
                chunks=chunks,
                embedded_chunks=(
                    embedded_chunks
                ),
                model=model,
                embedding_model=(
                    model_identifier
                ),
                semantic_k=SEMANTIC_K,
                keyword_k=KEYWORD_K,
                final_k=FINAL_K,
                semantic_min_similarity=(
                    SEMANTIC_MIN_SIMILARITY
                ),
                keyword_min_score=(
                    KEYWORD_MIN_SCORE
                ),
                min_rrf_score=(
                    MIN_RRF_SCORE
                ),
            )
        )

        comparison = (
            compare_methods_for_case(
                case=case,
                semantic_results=(
                    semantic_results
                ),
                keyword_results=(
                    keyword_results
                ),
                hybrid_results=(
                    hybrid_results
                ),
                top_k=FINAL_K,
            )
        )

        comparison[
            "raw_results"
        ] = {
            "semantic": (
                semantic_results
            ),
            "keyword": (
                keyword_results
            ),
            "hybrid": (
                hybrid_results
            ),
        }

        case_results.append(
            comparison
        )

        print(
            "  Semantic:",
            safe_document_ids(
                semantic_results
            ),
        )

        print(
            "  BM25:    ",
            safe_document_ids(
                keyword_results
            ),
        )

        print(
            "  Hybrid:  ",
            safe_document_ids(
                hybrid_results
            ),
        )

        print()

    summary = summarise_benchmark(
        case_results
    )

    output = {
        "experiment": (
            "week18_retrieval_benchmark"
        ),
        "evaluation_case_count": len(
            cases
        ),
        "corpus_file_count": len(
            [
                path
                for path
                in RAW_DATA_DIR.iterdir()
                if path.suffix.lower()
                in {".pdf", ".txt"}
            ]
        ),
        "chunk_count": len(
            chunks
        ),
        "embedding_model": (
            model_identifier
        ),
        "configuration": {
            "target_chars": TARGET_CHARS,
            "overlap_chars": (
                OVERLAP_CHARS
            ),
            "semantic_k": SEMANTIC_K,
            "keyword_k": KEYWORD_K,
            "final_k": FINAL_K,
            "semantic_min_similarity": (
                SEMANTIC_MIN_SIMILARITY
            ),
            "keyword_min_score": (
                KEYWORD_MIN_SCORE
            ),
            "min_rrf_score": (
                MIN_RRF_SCORE
            ),
        },
        "summary": summary,
        "case_results": (
            case_results
        ),
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "=" * 50
    )

    print(
        "BENCHMARK SUMMARY"
    )

    print(
        "=" * 50
    )

    for method_name in (
        "semantic",
        "keyword",
        "hybrid",
    ):
        metrics = summary[
            method_name
        ]

        print()
        print(
            method_name.upper()
        )

        print(
            "  Top-1:",
            metrics[
                "top1_success_rate"
            ],
        )

        print(
            "  Top-k:",
            metrics[
                "topk_success_rate"
            ],
        )

        print(
            "  Abstention:",
            metrics[
                "abstention_success_rate"
            ],
        )

        print(
            "  Active-only:",
            metrics[
                "active_only_rate"
            ],
        )

    print()
    print(
        f"Saved benchmark to:"
    )

    print(
        OUTPUT_FILE
    )

    return output


if __name__ == "__main__":
    run_benchmark()
