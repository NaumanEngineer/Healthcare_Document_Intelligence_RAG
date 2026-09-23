from __future__ import annotations

import json
import re
from pathlib import Path


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.preprocessing.build_chunks import (
    build_document_chunks,
)

from src.retrieval.embeddings import (
    embed_chunks,
    get_model_identifier,
    load_embedding_model,
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

from src.retrieval.hybrid_search_rrf_only import (
    hybrid_search_rrf_only,
)

from src.retrieval.hybrid_search_evidence_rescue import (
    hybrid_search_evidence_rescue,
)

from src.retrieval.query_scope import assess_query_scope
from src.retrieval.evidence_sufficiency import assess_evidence_sufficiency

from src.evaluation.retrieval_benchmark import (
    compare_methods_for_case,
    evaluate_retrieval_results,
    summarise_benchmark,
    summarise_method,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

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


# ============================================================
# EXPERIMENT CONFIGURATION
# ============================================================

TARGET_CHARS = 1000
OVERLAP_CHARS = 150

SEMANTIC_K = 10
KEYWORD_K = 10
FINAL_K = 3

# We deliberately leave thresholds disabled during this
# baseline experiment.
#
# The purpose is to observe the untreated behaviour before
# calibrating abstention/evidence sufficiency.

SEMANTIC_MIN_SIMILARITY = None
KEYWORD_MIN_SCORE = None
MIN_RRF_SCORE = None


# ============================================================
# FILE / DOCUMENT HELPERS
# ============================================================

def extract_document_id(
    file_path: Path,
) -> str:
    """
    Extract a canonical DOC-### identifier from a filename.

    Example:

        DOC-008_ambulance_handover_guidance.pdf
        -> DOC-008
    """

    match = re.search(
        r"(DOC-\d{3})",
        file_path.name,
        re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            "Could not determine document ID "
            f"from filename: {file_path.name}"
        )

    return match.group(1).upper()


def parse_header_value(
    text: str,
    label: str,
    default: str,
) -> str:
    """
    Read a simple metadata line from a synthetic TXT file.

    Example:

        Status: Draft
        Version: 0.1
    """

    pattern = (
        rf"^{re.escape(label)}"
        rf"\s*:\s*(.+)$"
    )

    match = re.search(
        pattern,
        text,
        flags=(
            re.MULTILINE
            | re.IGNORECASE
        ),
    )

    if match:
        return (
            match.group(1)
            .strip()
        )

    return default


# ============================================================
# TXT CHUNKING ADAPTER
# ============================================================

def split_text_with_overlap(
    text: str,
    target_chars: int = TARGET_CHARS,
    overlap_chars: int = OVERLAP_CHARS,
) -> list[str]:
    """
    Deterministically split synthetic TXT documents into chunks.

    PDFs continue to use the project's normal chunking pipeline.

    TXT files are used for lifecycle stress tests such as:

    - Superseded DOC-001 v0.9
    - Active DOC-013
    - Draft DOC-014
    """

    if not isinstance(
        text,
        str,
    ):
        raise TypeError(
            "text must be a string"
        )

    cleaned = " ".join(
        text.split()
    )

    if not cleaned:
        return []

    if len(cleaned) <= target_chars:
        return [
            cleaned
        ]

    chunks: list[str] = []

    start = 0

    while start < len(cleaned):
        end = min(
            start + target_chars,
            len(cleaned),
        )

        # Prefer a word boundary rather than cutting
        # directly through a word.
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

        next_start = (
            end
            - overlap_chars
        )

        # Safety protection against accidental
        # infinite loops.
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def build_txt_document_chunks(
    file_path: Path,
) -> list[dict]:
    """
    Build canonical chunk dictionaries from one synthetic TXT file.
    """

    text = file_path.read_text(
        encoding="utf-8"
    )

    document_id = (
        extract_document_id(
            file_path
        )
    )

    title = (
        parse_header_value(
            text=text,
            label="Title",
            default=(
                file_path.stem.replace(
                    "_",
                    " ",
                )
            ),
        )
    )

    version = (
        parse_header_value(
            text=text,
            label="Version",
            default="1.0",
        )
    )

    effective_date = (
        parse_header_value(
            text=text,
            label="Effective Date",
            default="2026-01-01",
        )
    )

    status = (
        parse_header_value(
            text=text,
            label="Status",
            default="Active",
        )
    )

    pieces = (
        split_text_with_overlap(
            text=text,
            target_chars=TARGET_CHARS,
            overlap_chars=OVERLAP_CHARS,
        )
    )

    chunks: list[dict] = []

    safe_version = (
        version
        .replace(
            " ",
            "",
        )
    )

    for index, piece in enumerate(
        pieces,
        start=1,
    ):
        chunk_id = (
            f"{document_id}-"
            f"V{safe_version}-"
            f"P001-"
            f"C{index:03d}"
        )

        chunk = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "title": title,
            "document_type": (
                "Synthetic Operational Document"
            ),
            "source_type": "Synthetic",
            "source_location": str(
                file_path
            ),
            "version": version,
            "effective_date": effective_date,
            "status": status,
            "source_file": (
                file_path.name
            ),
            "page": 1,
            "chunk_number": index,
            "text": piece,
        }

        chunks.append(
            chunk
        )

    return chunks


# ============================================================
# CORPUS BUILDING
# ============================================================

def get_raw_corpus_files(
) -> list[Path]:
    """
    Return supported raw corpus files in deterministic order.
    """

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            "Raw corpus directory does not exist: "
            f"{RAW_DATA_DIR}"
        )

    files = sorted(
        [
            path
            for path
            in RAW_DATA_DIR.iterdir()
            if (
                path.is_file()
                and path.suffix.lower()
                in {
                    ".pdf",
                    ".txt",
                }
            )
        ],
        key=lambda path: path.name.lower(),
    )

    if not files:
        raise RuntimeError(
            "No PDF or TXT documents were found "
            "inside data/raw."
        )

    return files


def build_benchmark_corpus(
) -> list[dict]:
    """
    Build the complete Week 18 retrieval corpus.

    PDF documents:
        use build_document_chunks()

    TXT stress documents:
        use build_txt_document_chunks()
    """

    files = (
        get_raw_corpus_files()
    )

    print(
        f"Found {len(files)} raw corpus files."
    )

    all_chunks: list[dict] = []

    for file_path in files:
        document_id = (
            extract_document_id(
                file_path
            )
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
                    document_id=(
                        document_id
                    ),
                    target_chars=(
                        TARGET_CHARS
                    ),
                    overlap_chars=(
                        OVERLAP_CHARS
                    ),
                )
            )

        else:
            document_chunks = (
                build_txt_document_chunks(
                    file_path
                )
            )

        print(
            "  -> "
            f"{len(document_chunks)} chunks"
        )

        all_chunks.extend(
            document_chunks
        )

    if not all_chunks:
        raise RuntimeError(
            "Corpus processing completed "
            "but produced zero chunks."
        )

    return all_chunks


# ============================================================
# EVALUATION DATASET
# ============================================================

def load_evaluation_cases(
) -> list[dict]:
    """
    Load the Week 18 controlled evaluation dataset.
    """

    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(
            "Evaluation dataset not found: "
            f"{EVALUATION_FILE}"
        )

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
            "Evaluation dataset must contain "
            "a JSON list."
        )

    if not cases:
        raise ValueError(
            "Evaluation dataset contains zero cases."
        )

    return cases


# ============================================================
# OUTPUT HELPERS
# ============================================================

def safe_document_ids(
    results: list[dict],
) -> list[str]:
    """
    Return unique document IDs while preserving
    result order.
    """

    document_ids: list[str] = []

    for result in results:
        document_id = (
            result.get(
                "document_id"
            )
        )

        if (
            isinstance(
                document_id,
                str,
            )
            and document_id
            and document_id
            not in document_ids
        ):
            document_ids.append(
                document_id
            )

    return document_ids


def print_method_results(
    label: str,
    results: list[dict],
) -> None:
    """
    Print readable retrieval output.
    """

    print(
        f"  {label:<9}",
        safe_document_ids(
            results
        ),
    )


def print_summary_metric(
    label: str,
    value,
) -> None:
    """
    Print benchmark metric consistently.
    """

    print(
        f"  {label}: {value}"
    )


# ============================================================
# MAIN BENCHMARK
# ============================================================

def run_benchmark(
) -> dict:
    """
    Execute the Week 18 retrieval experiment.

    Methods compared:

    1. Semantic retrieval
    2. BM25 keyword retrieval
    3. Original hybrid retrieval
       Semantic + BM25 -> RRF -> existing reranker
    4. RRF-only hybrid retrieval
       Semantic + BM25 -> RRF -> final selection

    5. Experimental hybrid evidence rescue

    The fourth method tests the hypothesis that the existing
    post-fusion reranker may be undoing useful BM25/RRF signals.
    """

    print()

    print(
        "WEEK 18 RETRIEVAL BENCHMARK"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # LOAD EVALUATION CASES
    # --------------------------------------------------------

    cases = (
        load_evaluation_cases()
    )

    print(
        f"Evaluation cases: {len(cases)}"
    )

    # --------------------------------------------------------
    # BUILD CORPUS
    # --------------------------------------------------------

    chunks = (
        build_benchmark_corpus()
    )

    print(
        f"Total chunks: {len(chunks)}"
    )

    # --------------------------------------------------------
    # LOAD EMBEDDING MODEL
    # --------------------------------------------------------

    print()

    print(
        "Loading embedding model..."
    )

    model = (
        load_embedding_model()
    )

    model_identifier = (
        get_model_identifier(
            model
        )
    )

    print(
        "Embedding model: "
        f"{model_identifier}"
    )

    # --------------------------------------------------------
    # EMBED CORPUS
    # --------------------------------------------------------

    print()

    print(
        "Embedding corpus..."
    )

    embedded_chunks = (
        embed_chunks(
            chunks=chunks,
            model=model,
            model_name=(
                model_identifier
            ),
        )
    )

    print(
        "Embedded chunks: "
        f"{len(embedded_chunks)}"
    )

    # --------------------------------------------------------
    # RUN EVERY EVALUATION CASE
    # --------------------------------------------------------

    print()

    print(
        "Running retrieval benchmark..."
    )

    print()

    case_results: list[dict] = []

    for case in cases:
        query_id = (
            case.get(
                "query_id"
            )
        )

        question = (
            case.get(
                "question"
            )
        )

        if not isinstance(
            question,
            str,
        ) or not question.strip():
            raise ValueError(
                f"{query_id} has an invalid question."
            )

        scope_assessment = assess_query_scope(question)

        print(
            f"{query_id}: {question}"
        )

        hybrid_rescue_results = []
        hybrid_rescue_audit = None

        if scope_assessment["allowed"] is False:
            semantic_results = []
            keyword_results = []
            hybrid_results = []
            rrf_only_results = []
            print("Scope: OUT_OF_SCOPE -> ABSTAIN")
        else:
            # ====================================================
            # METHOD 1 — SEMANTIC
            # ====================================================

            semantic_results = (
                semantic_search(
                    query=question,
                    embedded_chunks=(
                        embedded_chunks
                    ),
                    model=model,
                    embedding_model=(
                        model_identifier
                    ),
                    candidate_k=(
                        SEMANTIC_K
                    ),
                    final_k=(
                        FINAL_K
                    ),
                    min_similarity=(
                        SEMANTIC_MIN_SIMILARITY
                    ),
                )
            )

            # ====================================================
            # METHOD 2 — BM25
            # ====================================================

            keyword_results = (
                keyword_search(
                    query=question,
                    chunks=chunks,
                    top_k=(
                        FINAL_K
                    ),
                    min_score=(
                        KEYWORD_MIN_SCORE
                    ),
                )
            )

            # ====================================================
            # METHOD 3 — ORIGINAL HYBRID
            # ====================================================

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
                    semantic_k=(
                        SEMANTIC_K
                    ),
                    keyword_k=(
                        KEYWORD_K
                    ),
                    final_k=(
                        FINAL_K
                    ),
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

            # ====================================================
            # METHOD 4 — RRF-ONLY HYBRID
            # ====================================================

            rrf_only_results = (
                hybrid_search_rrf_only(
                    query=question,
                    chunks=chunks,
                    embedded_chunks=(
                        embedded_chunks
                    ),
                    model=model,
                    embedding_model=(
                        model_identifier
                    ),
                    semantic_k=(
                        SEMANTIC_K
                    ),
                    keyword_k=(
                        KEYWORD_K
                    ),
                    final_k=(
                        FINAL_K
                    ),
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

            hybrid_rescue_output = hybrid_search_evidence_rescue(
                query=question,
                chunks=chunks,
                embedded_chunks=embedded_chunks,
                model=model,
                embedding_model=model_identifier,
                semantic_k=SEMANTIC_K,
                keyword_k=KEYWORD_K,
                final_k=FINAL_K,
                semantic_min_similarity=SEMANTIC_MIN_SIMILARITY,
                keyword_min_score=KEYWORD_MIN_SCORE,
                min_rrf_score=MIN_RRF_SCORE,
            )
            hybrid_rescue_results = hybrid_rescue_output["results"]
            hybrid_rescue_audit = hybrid_rescue_output["audit"]

        # Preserve retrieval output before applying per-method evidence gates.
        raw_results = {
            "semantic": semantic_results,
            "keyword": keyword_results,
            "hybrid": hybrid_results,
            "rrf_only": rrf_only_results,
        }
        scoring_results = raw_results.copy()
        # None records that evidence assessment was skipped by the scope gate.
        evidence_assessments = dict.fromkeys(raw_results)
        if scope_assessment["allowed"]:
            for method, results in raw_results.items():
                assessment = assess_evidence_sufficiency(question, results)
                evidence_assessments[method] = assessment
                if assessment["decision"] == "INSUFFICIENT":
                    scoring_results[method] = []
                    label = {
                        "semantic": "Semantic",
                        "keyword": "BM25",
                        "hybrid": "Hybrid",
                        "rrf_only": "RRF-only",
                    }[method]
                    print(f"{label} evidence: INSUFFICIENT -> ABSTAIN")

        # Rescue has already assessed its final evidence internally.
        raw_results["hybrid_rescue"] = hybrid_rescue_results
        rescue_evidence = (
            hybrid_rescue_audit["final_evidence"]
            if hybrid_rescue_audit is not None else None
        )
        evidence_assessments["hybrid_rescue"] = rescue_evidence
        if rescue_evidence is None or rescue_evidence["decision"] != "SUFFICIENT":
            hybrid_rescue_results = []
            if rescue_evidence is not None:
                print("Hybrid rescue evidence: INSUFFICIENT -> ABSTAIN")

        semantic_results = scoring_results["semantic"]
        keyword_results = scoring_results["keyword"]
        hybrid_results = scoring_results["hybrid"]
        rrf_only_results = scoring_results["rrf_only"]

        # ====================================================
        # EVALUATE ORIGINAL THREE METHODS
        # ====================================================

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
                top_k=(
                    FINAL_K
                ),
            )
        )

        # ====================================================
        # EVALUATE RRF-ONLY METHOD
        # ====================================================

        rrf_only_evaluation = (
            evaluate_retrieval_results(
                case=case,
                results=(
                    rrf_only_results
                ),
                top_k=(
                    FINAL_K
                ),
            )
        )

        comparison[
            "rrf_only"
        ] = (
            rrf_only_evaluation
        )

        # ====================================================
        # PRESERVE RAW RETRIEVAL OUTPUT
        # ====================================================

        comparison["hybrid_rescue"] = evaluate_retrieval_results(
            case=case, results=hybrid_rescue_results, top_k=FINAL_K,
        )
        comparison["hybrid_rescue_audit"] = hybrid_rescue_audit
        comparison["raw_results"] = raw_results
        comparison["evidence_sufficiency"] = evidence_assessments

        comparison["scope_assessment"] = scope_assessment

        case_results.append(
            comparison
        )

        # ====================================================
        # PRINT CASE RESULTS
        # ====================================================

        print_method_results(
            "Semantic:",
            semantic_results,
        )

        print_method_results(
            "BM25:",
            keyword_results,
        )

        print_method_results(
            "Hybrid:",
            hybrid_results,
        )

        print_method_results(
            "RRF-only:",
            rrf_only_results,
        )
        print_method_results("Hybrid rescue:", hybrid_rescue_results)

        print()

    # --------------------------------------------------------
    # ORIGINAL THREE-METHOD SUMMARY
    # --------------------------------------------------------

    summary = (
        summarise_benchmark(
            case_results
        )
    )

    # --------------------------------------------------------
    # ADD RRF-ONLY SUMMARY
    # --------------------------------------------------------

    summary[
        "rrf_only"
    ] = (
        summarise_method(
            case_results,
            "rrf_only",
        )
    )

    # --------------------------------------------------------
    # EXPERIMENT METADATA
    # --------------------------------------------------------

    summary["hybrid_rescue"] = summarise_method(case_results, "hybrid_rescue")

    raw_files = (
        get_raw_corpus_files()
    )

    output = {
        "experiment": (
            "week18_retrieval_benchmark"
        ),
        "experiment_description": (
            "Semantic vs BM25 vs original hybrid "
            "vs RRF-only hybrid vs evidence-rescue hybrid retrieval"
        ),
        "evaluation_case_count": (
            len(cases)
        ),
        "corpus_file_count": (
            len(raw_files)
        ),
        "chunk_count": (
            len(chunks)
        ),
        "embedding_model": (
            model_identifier
        ),
        "configuration": {
            "target_chars": (
                TARGET_CHARS
            ),
            "overlap_chars": (
                OVERLAP_CHARS
            ),
            "semantic_k": (
                SEMANTIC_K
            ),
            "keyword_k": (
                KEYWORD_K
            ),
            "final_k": (
                FINAL_K
            ),
            "semantic_min_similarity": (
                SEMANTIC_MIN_SIMILARITY
            ),
            "keyword_min_score": (
                KEYWORD_MIN_SCORE
            ),
            "min_rrf_score": (
                MIN_RRF_SCORE
            ),
            "rrf_only_experiment": True,
            "hybrid_rescue_experiment": True,
        },
        "summary": (
            summary
        ),
        "case_results": (
            case_results
        ),
    }

    # --------------------------------------------------------
    # SAVE JSON OUTPUT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PRINT FINAL BENCHMARK SUMMARY
    # --------------------------------------------------------

    print(
        "=" * 60
    )

    print(
        "BENCHMARK SUMMARY"
    )

    print(
        "=" * 60
    )

    for method_name in (
        "semantic",
        "keyword",
        "hybrid",
        "rrf_only",
        "hybrid_rescue",
    ):
        metrics = (
            summary[
                method_name
            ]
        )

        print()

        print(
            method_name
            .replace(
                "_",
                " ",
            )
            .upper()
        )

        print_summary_metric(
            "Top-1",
            metrics[
                "top1_success_rate"
            ],
        )

        print_summary_metric(
            "Top-k",
            metrics[
                "topk_success_rate"
            ],
        )

        print_summary_metric(
            "Abstention",
            metrics[
                "abstention_success_rate"
            ],
        )

        print_summary_metric(
            "Active-only",
            metrics[
                "active_only_rate"
            ],
        )

    print()

    print(
        "Benchmark saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "Experiment complete."
    )

    return output


# ============================================================
# COMMAND-LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_benchmark()
