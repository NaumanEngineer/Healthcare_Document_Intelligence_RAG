from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

BENCHMARK_PATH = (
    ROOT
    / "data"
    / "benchmark"
    / "week25_citation_faithfulness_benchmark.json"
)


ALLOWED_GOVERNANCE_DECISIONS = {
    "AUTO_ANSWER",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}

ALLOWED_RESPONSE_TYPES = {
    "ANSWER",
    "REVIEW",
    "ABSTENTION",
}

EXPECTED_RESPONSE_TYPE_BY_GOVERNANCE = {
    "AUTO_ANSWER": "ANSWER",
    "REVIEW_REQUIRED": "REVIEW",
    "ABSTAIN": "ABSTENTION",
}

ALLOWED_SUPPORT_STATUSES = {
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "UNSUPPORTED",
    "CITATION_MISMATCH",
}

ALLOWED_VERIFICATION_DECISIONS = {
    "PASS",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}

ALLOWED_PRECEDENCE_DECISIONS = {
    "SAFE_TO_COMBINE",
    "REVIEW_BEFORE_COMBINATION",
    "BLOCK_COMBINATION",
}

ALLOWED_OVERALL_STATUSES = {
    "PASS",
    "PASS_WITH_WARNINGS",
    "FAIL",
}


REQUIRED_CASE_FIELDS = {
    "case_id",
    "case_name",
    "description",
    "question",
    "expected_governance_decision",
    "expected_response_type",
    "evidence_items",
    "citation_index",
    "expected_claims",
    "required_citation_ids",
    "allowed_citation_ids",
    "forbidden_citation_ids",
    "forbidden_claims",
    "expected_verification_decision",
    "expected_precedence_decision",
    "requires_human_review",
    "conflict_expected",
    "uncertainty_expected",
    "abstention_expected",
    "expected_overall_faithfulness_status",
    "benchmark_tags",
}


def _require_non_blank_string(
    value: Any,
    field_name: str,
    context: str,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{context}: {field_name} must be a non-blank string."
        )


def _require_list(
    value: Any,
    field_name: str,
    context: str,
) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(
            f"{context}: {field_name} must be a list."
        )

    return value


def _require_bool(
    value: Any,
    field_name: str,
    context: str,
) -> None:
    if not isinstance(value, bool):
        raise TypeError(
            f"{context}: {field_name} must be a boolean."
        )


def _validate_case_id(
    case_id: str,
) -> None:
    if not case_id.startswith("W25-C"):
        raise ValueError(
            f"{case_id}: case_id must begin with W25-C."
        )


def _validate_governance_and_response_type(
    case: dict[str, Any],
) -> None:
    case_id = case["case_id"]

    governance = case[
        "expected_governance_decision"
    ]

    response_type = case[
        "expected_response_type"
    ]

    if governance not in ALLOWED_GOVERNANCE_DECISIONS:
        raise ValueError(
            f"{case_id}: unsupported governance decision "
            f"{governance!r}."
        )

    if response_type not in ALLOWED_RESPONSE_TYPES:
        raise ValueError(
            f"{case_id}: unsupported response type "
            f"{response_type!r}."
        )

    required_response_type = (
        EXPECTED_RESPONSE_TYPE_BY_GOVERNANCE[
            governance
        ]
    )

    if response_type != required_response_type:
        raise ValueError(
            f"{case_id}: governance decision "
            f"{governance} requires response type "
            f"{required_response_type}, not "
            f"{response_type}."
        )


def _validate_evidence_items(
    case: dict[str, Any],
) -> set[str]:
    case_id = case["case_id"]

    evidence_items = _require_list(
        case["evidence_items"],
        "evidence_items",
        case_id,
    )

    evidence_ids: set[str] = set()

    for evidence in evidence_items:
        if not isinstance(evidence, dict):
            raise TypeError(
                f"{case_id}: each evidence item "
                "must be a dictionary."
            )

        for field_name in (
            "evidence_id",
            "document_id",
            "chunk_id",
            "title",
            "status",
            "source_file",
            "version",
            "evidence_text",
            "evidence_role",
        ):
            _require_non_blank_string(
                evidence.get(field_name),
                field_name,
                case_id,
            )

        evidence_id = evidence["evidence_id"]

        if evidence_id in evidence_ids:
            raise ValueError(
                f"{case_id}: duplicate evidence_id "
                f"{evidence_id}."
            )

        evidence_ids.add(evidence_id)

        expected_evidence_id = (
            "EVIDENCE::"
            + evidence["chunk_id"]
        )

        if evidence_id != expected_evidence_id:
            raise ValueError(
                f"{case_id}: evidence_id "
                f"{evidence_id!r} does not match "
                f"{expected_evidence_id!r}."
            )

    return evidence_ids


def _validate_citation_index(
    case: dict[str, Any],
) -> set[str]:
    case_id = case["case_id"]

    citation_index = _require_list(
        case["citation_index"],
        "citation_index",
        case_id,
    )

    citation_ids: set[str] = set()

    for citation in citation_index:
        if not isinstance(citation, dict):
            raise TypeError(
                f"{case_id}: each citation must "
                "be a dictionary."
            )

        citation_id = citation.get(
            "citation_id"
        )

        _require_non_blank_string(
            citation_id,
            "citation_id",
            case_id,
        )

        if citation_id in citation_ids:
            raise ValueError(
                f"{case_id}: duplicate citation ID "
                f"{citation_id}."
            )

        citation_ids.add(citation_id)

        for field_name in (
            "evidence_id",
            "document_id",
            "chunk_id",
            "source_file",
            "version",
            "status",
        ):
            _require_non_blank_string(
                citation.get(field_name),
                field_name,
                case_id,
            )

        page = citation.get("page")

        if (
            not isinstance(page, int)
            or isinstance(page, bool)
        ):
            raise TypeError(
                f"{case_id}: citation page "
                "must be an integer."
            )

    return citation_ids


def _validate_citation_evidence_alignment(
    case: dict[str, Any],
    evidence_ids: set[str],
) -> None:
    case_id = case["case_id"]

    evidence_lookup = {
        evidence["evidence_id"]: evidence
        for evidence in case[
            "evidence_items"
        ]
    }

    for citation in case[
        "citation_index"
    ]:
        evidence_id = citation[
            "evidence_id"
        ]

        if evidence_id not in evidence_ids:
            raise ValueError(
                f"{case_id}: citation "
                f"{citation['citation_id']} references "
                f"unknown evidence {evidence_id}."
            )

        evidence = evidence_lookup[
            evidence_id
        ]

        for field_name in (
            "document_id",
            "chunk_id",
            "source_file",
            "version",
            "status",
        ):
            if (
                citation.get(field_name)
                != evidence.get(field_name)
            ):
                raise ValueError(
                    f"{case_id}: citation "
                    f"{citation['citation_id']} "
                    f"{field_name} does not match "
                    "the referenced evidence."
                )


def _validate_claims(
    case: dict[str, Any],
    evidence_ids: set[str],
) -> None:
    case_id = case["case_id"]

    claims = _require_list(
        case["expected_claims"],
        "expected_claims",
        case_id,
    )

    claim_ids: set[str] = set()

    for claim in claims:
        if not isinstance(claim, dict):
            raise TypeError(
                f"{case_id}: each expected claim "
                "must be a dictionary."
            )

        claim_id = claim.get(
            "claim_id"
        )

        _require_non_blank_string(
            claim_id,
            "claim_id",
            case_id,
        )

        _require_non_blank_string(
            claim.get("claim_text"),
            "claim_text",
            case_id,
        )

        if claim_id in claim_ids:
            raise ValueError(
                f"{case_id}: duplicate claim_id "
                f"{claim_id}."
            )

        claim_ids.add(claim_id)

        support_status = claim.get(
            "expected_support_status"
        )

        if (
            support_status
            not in ALLOWED_SUPPORT_STATUSES
        ):
            raise ValueError(
                f"{case_id}: claim {claim_id} has "
                f"unsupported status "
                f"{support_status!r}."
            )

        supporting_evidence_ids = (
            _require_list(
                claim.get(
                    "supporting_evidence_ids"
                ),
                "supporting_evidence_ids",
                case_id,
            )
        )

        for evidence_id in supporting_evidence_ids:
            if evidence_id not in evidence_ids:
                raise ValueError(
                    f"{case_id}: claim {claim_id} "
                    f"references unknown evidence "
                    f"{evidence_id}."
                )

        _require_list(
            claim.get(
                "required_citation_ids"
            ),
            "required_citation_ids",
            case_id,
        )

        citation = claim.get(
            "citation"
        )

        if citation is not None:
            if not isinstance(citation, dict):
                raise TypeError(
                    f"{case_id}: claim {claim_id} "
                    "citation must be a dictionary "
                    "or null."
                )

            _require_non_blank_string(
                citation.get(
                    "document_id"
                ),
                "document_id",
                case_id,
            )

            _require_non_blank_string(
                citation.get(
                    "chunk_id"
                ),
                "chunk_id",
                case_id,
            )


def _validate_citation_sets(
    case: dict[str, Any],
    citation_ids: set[str],
) -> None:
    case_id = case["case_id"]

    required = set(
        _require_list(
            case[
                "required_citation_ids"
            ],
            "required_citation_ids",
            case_id,
        )
    )

    allowed = set(
        _require_list(
            case[
                "allowed_citation_ids"
            ],
            "allowed_citation_ids",
            case_id,
        )
    )

    forbidden = set(
        _require_list(
            case[
                "forbidden_citation_ids"
            ],
            "forbidden_citation_ids",
            case_id,
        )
    )

    if not required.issubset(
        allowed
    ):
        raise ValueError(
            f"{case_id}: required citations "
            "must also be allowed."
        )

    if allowed & forbidden:
        raise ValueError(
            f"{case_id}: citation cannot be "
            "both allowed and forbidden."
        )

    for citation_id in allowed:
        if citation_id not in citation_ids:
            raise ValueError(
                f"{case_id}: allowed citation "
                f"{citation_id} is absent from "
                "citation_index."
            )

    for citation_id in required:
        if citation_id not in citation_ids:
            raise ValueError(
                f"{case_id}: required citation "
                f"{citation_id} is absent from "
                "citation_index."
            )


def _validate_expected_decisions(
    case: dict[str, Any],
) -> None:
    case_id = case["case_id"]

    verification = case[
        "expected_verification_decision"
    ]

    precedence = case[
        "expected_precedence_decision"
    ]

    overall = case[
        "expected_overall_faithfulness_status"
    ]

    if verification not in ALLOWED_VERIFICATION_DECISIONS:
        raise ValueError(
            f"{case_id}: unsupported expected "
            f"verification decision "
            f"{verification!r}."
        )

    if precedence not in ALLOWED_PRECEDENCE_DECISIONS:
        raise ValueError(
            f"{case_id}: unsupported expected "
            f"precedence decision "
            f"{precedence!r}."
        )

    if overall not in ALLOWED_OVERALL_STATUSES:
        raise ValueError(
            f"{case_id}: unsupported overall "
            f"faithfulness status "
            f"{overall!r}."
        )


def _validate_governance_flags(
    case: dict[str, Any],
) -> None:
    """
    Validate benchmark handling flags.

    Important Week 25 distinction:

    expected_governance_decision describes the upstream
    governance state before the candidate answer is evaluated.

    requires_human_review describes the expected safe handling
    after citation / faithfulness evaluation.

    Therefore an upstream AUTO_ANSWER case may legitimately
    require human review if the candidate answer fails
    faithfulness verification.
    """

    case_id = case["case_id"]

    for field_name in (
        "requires_human_review",
        "conflict_expected",
        "uncertainty_expected",
        "abstention_expected",
    ):
        _require_bool(
            case[field_name],
            field_name,
            case_id,
        )

    governance = case[
        "expected_governance_decision"
    ]

    requires_human_review = case[
        "requires_human_review"
    ]

    abstention_expected = case[
        "abstention_expected"
    ]

    verification = case[
        "expected_verification_decision"
    ]

    if (
        governance == "REVIEW_REQUIRED"
        and not requires_human_review
    ):
        raise ValueError(
            f"{case_id}: upstream REVIEW_REQUIRED "
            "must preserve human review."
        )

    if governance == "ABSTAIN":
        if not abstention_expected:
            raise ValueError(
                f"{case_id}: ABSTAIN governance "
                "must set abstention_expected=true."
            )

    if (
        governance != "ABSTAIN"
        and abstention_expected
    ):
        raise ValueError(
            f"{case_id}: non-ABSTAIN governance "
            "cannot set abstention_expected=true."
        )

    if (
        verification == "REVIEW_REQUIRED"
        and governance != "ABSTAIN"
        and not requires_human_review
    ):
        raise ValueError(
            f"{case_id}: expected verification "
            "REVIEW_REQUIRED must result in "
            "human review for non-abstention cases."
        )


def _validate_case(
    case: dict[str, Any],
) -> None:
    if not isinstance(case, dict):
        raise TypeError(
            "Each benchmark case must be a dictionary."
        )

    missing_fields = (
        REQUIRED_CASE_FIELDS
        - set(case.keys())
    )

    if missing_fields:
        raise ValueError(
            "Benchmark case is missing fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    case_id = case["case_id"]

    _require_non_blank_string(
        case_id,
        "case_id",
        case_id,
    )

    _validate_case_id(
        case_id
    )

    for field_name in (
        "case_name",
        "description",
        "question",
    ):
        _require_non_blank_string(
            case[field_name],
            field_name,
            case_id,
        )

    _validate_governance_and_response_type(
        case
    )

    evidence_ids = (
        _validate_evidence_items(
            case
        )
    )

    citation_ids = (
        _validate_citation_index(
            case
        )
    )

    _validate_citation_evidence_alignment(
        case,
        evidence_ids,
    )

    _validate_claims(
        case,
        evidence_ids,
    )

    _validate_citation_sets(
        case,
        citation_ids,
    )

    _validate_expected_decisions(
        case
    )

    _validate_governance_flags(
        case
    )

    _require_list(
        case[
            "forbidden_claims"
        ],
        "forbidden_claims",
        case_id,
    )

    tags = _require_list(
        case[
            "benchmark_tags"
        ],
        "benchmark_tags",
        case_id,
    )

    if not tags:
        raise ValueError(
            f"{case_id}: benchmark_tags "
            "must not be empty."
        )


def validate_benchmark(
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(
        benchmark,
        dict,
    ):
        raise TypeError(
            "Benchmark root must be a dictionary."
        )

    for field_name in (
        "benchmark_name",
        "benchmark_version",
        "project",
        "purpose",
    ):
        _require_non_blank_string(
            benchmark.get(
                field_name
            ),
            field_name,
            "BENCHMARK",
        )

    if (
        benchmark.get(
            "synthetic_data_only"
        )
        is not True
    ):
        raise ValueError(
            "BENCHMARK: synthetic_data_only "
            "must be true."
        )

    cases = benchmark.get(
        "cases"
    )

    if not isinstance(
        cases,
        list,
    ):
        raise TypeError(
            "BENCHMARK: cases must be a list."
        )

    if len(cases) != 18:
        raise ValueError(
            "BENCHMARK: expected exactly "
            f"18 cases, found {len(cases)}."
        )

    case_ids: set[str] = set()

    for case in cases:
        _validate_case(
            case
        )

        case_id = case[
            "case_id"
        ]

        if case_id in case_ids:
            raise ValueError(
                f"BENCHMARK: duplicate case_id "
                f"{case_id}."
            )

        case_ids.add(
            case_id
        )

    expected_case_ids = {
        f"W25-C{number:03d}"
        for number in range(
            1,
            19,
        )
    }

    if case_ids != expected_case_ids:
        missing = sorted(
            expected_case_ids
            - case_ids
        )

        unexpected = sorted(
            case_ids
            - expected_case_ids
        )

        raise ValueError(
            "BENCHMARK: case ID sequence mismatch. "
            f"Missing={missing}; "
            f"Unexpected={unexpected}."
        )

    governance_counts = {
        decision: 0
        for decision
        in ALLOWED_GOVERNANCE_DECISIONS
    }

    verification_counts = {
        decision: 0
        for decision
        in ALLOWED_VERIFICATION_DECISIONS
    }

    overall_counts = {
        status: 0
        for status
        in ALLOWED_OVERALL_STATUSES
    }

    human_review_count = 0

    for case in cases:
        governance_counts[
            case[
                "expected_governance_decision"
            ]
        ] += 1

        verification_counts[
            case[
                "expected_verification_decision"
            ]
        ] += 1

        overall_counts[
            case[
                "expected_overall_faithfulness_status"
            ]
        ] += 1

        if case[
            "requires_human_review"
        ]:
            human_review_count += 1

    return {
        "benchmark_name": benchmark[
            "benchmark_name"
        ],
        "case_count": len(cases),
        "governance_counts": governance_counts,
        "verification_counts": verification_counts,
        "overall_status_counts": overall_counts,
        "human_review_count": human_review_count,
        "validation_status": "PASS",
    }


def load_benchmark() -> dict[str, Any]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: "
            f"{BENCHMARK_PATH}"
        )

    with BENCHMARK_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main() -> None:
    benchmark = load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    print(
        "Week 25 Benchmark Integrity Validation"
    )
    print(
        "--------------------------------------"
    )
    print(
        f"Benchmark: "
        f"{result['benchmark_name']}"
    )
    print(
        f"Cases: "
        f"{result['case_count']}"
    )

    print("Upstream governance:")

    for decision in (
        "AUTO_ANSWER",
        "REVIEW_REQUIRED",
        "ABSTAIN",
    ):
        print(
            f"  {decision}: "
            f"{result['governance_counts'][decision]}"
        )

    print("Expected verification:")

    for decision in (
        "PASS",
        "REVIEW_REQUIRED",
        "ABSTAIN",
    ):
        print(
            f"  {decision}: "
            f"{result['verification_counts'][decision]}"
        )

    print(
        "Expected overall outcomes:"
    )

    for status in (
        "PASS",
        "PASS_WITH_WARNINGS",
        "FAIL",
    ):
        print(
            f"  {status}: "
            f"{result['overall_status_counts'][status]}"
        )

    print(
        "Cases requiring human review: "
        f"{result['human_review_count']}"
    )

    print(
        f"Validation: "
        f"{result['validation_status']}"
    )


if __name__ == "__main__":
    main()