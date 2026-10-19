"""Validate the Week 26 adversarial faithfulness benchmark.

The validator enforces the structural and governance contract defined
for the separate Week 26 benchmark.

Run with:

    python -m src.evaluation.validate_week26_benchmark
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


BENCHMARK_PATH = Path(
    "data/benchmark/week26_adversarial_faithfulness_benchmark.json"
)

EXPECTED_CASE_COUNT = 12

EXPECTED_CASE_IDS = [
    f"W26-C{i:03d}"
    for i in range(
        1,
        EXPECTED_CASE_COUNT + 1,
    )
]

ALLOWED_GOVERNANCE = {
    "AUTO_ANSWER",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}

ALLOWED_RESPONSE_TYPES = {
    "ANSWER",
    "REVIEW",
    "ABSTENTION",
}

GOVERNANCE_TO_RESPONSE = {
    "AUTO_ANSWER": "ANSWER",
    "REVIEW_REQUIRED": "REVIEW",
    "ABSTAIN": "ABSTENTION",
}

ALLOWED_LIFECYCLE_STATUSES = {
    "active",
    "superseded",
    "draft",
    "archived",
}

ALLOWED_APPROVAL_STATUSES = {
    "approved",
    "draft",
    "unknown",
}

ALLOWED_CLAIM_TYPES = {
    "FACTUAL",
    "NUMERICAL",
    "OPERATIONAL",
    "POLICY",
    "AUTHORITY",
    "ROLE_RESPONSIBILITY",
    "TEMPORAL",
    "CONFLICT_DESCRIPTION",
    "ABSTENTION_TEXT",
}

ALLOWED_SUPPORT_STATUSES = {
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "UNSUPPORTED",
    "CITATION_MISMATCH",
}

ALLOWED_GROUNDEDNESS_STATUSES = {
    "GROUNDED_SINGLE_SOURCE",
    "GROUNDED_MULTI_SOURCE",
    "PARTIALLY_GROUNDED",
    "UNGROUNDED",
    "CONFLICT_BLOCKED",
    "RELATIONSHIP_UNVERIFIED",
    "NOT_APPLICABLE",
}

ALLOWED_TEMPORAL_STATUSES = {
    "TEMPORALLY_VALID",
    "TEMPORALLY_HISTORICAL",
    "TEMPORALLY_EXPIRED",
    "FUTURE_EFFECTIVE",
    "TEMPORALLY_UNKNOWN",
    "NOT_APPLICABLE",
}

ALLOWED_RELATIONSHIP_DEPENDENCIES = {
    "SAME_DOCUMENT_CONTEXT",
    "EXPLICIT_SUPPORT_CHAIN",
    "COMPLEMENTARY_EVIDENCE",
    "EXPLICIT_CONFLICT",
    "VERSION_SUCCESSION",
    "UNRELATED",
    "UNKNOWN_RELATIONSHIP",
    "NOT_APPLICABLE",
}

ALLOWED_RELATIONSHIP_RESULTS = {
    "COMPOSITION_ALLOWED",
    "COMPOSITION_REVIEW_REQUIRED",
    "COMPOSITION_BLOCKED",
    "RELATIONSHIP_UNVERIFIED",
    "NOT_APPLICABLE",
}

ALLOWED_PRECEDENCE_DECISIONS = {
    "SAFE_TO_COMBINE",
    "REVIEW_BEFORE_COMBINATION",
    "BLOCK_COMBINATION",
}

ALLOWED_HALLUCINATION_DECISIONS = {
    "CLEAR",
    "HALLUCINATION_RISK",
    "REVIEW_AUTHORITY_INCREASE",
    "ABSTENTION_VIOLATION",
    "NOT_APPLICABLE",
}

ALLOWED_ABSTENTION_DECISIONS = {
    "SAFE_ABSTENTION",
    "DIRECTIVE_LEAKAGE",
    "AUTHORITY_LEAKAGE",
    "UNSUPPORTED_CERTAINTY",
    "ACTION_ASSUMPTION",
    "INVALID_ABSTENTION_STRUCTURE",
    "NOT_APPLICABLE",
}

ALLOWED_PROMPT_INJECTION_DECISIONS = {
    "NO_INJECTION_DETECTED",
    "INJECTION_DETECTED",
    "GOVERNANCE_OVERRIDE_ATTEMPT",
    "CONFLICT_SUPPRESSION_ATTEMPT",
    "AUTHORITY_OVERRIDE_ATTEMPT",
    "RESPONSE_OVERRIDE_ATTEMPT",
    "NOT_APPLICABLE",
}

ALLOWED_FINAL_ASSURANCE_DECISIONS = {
    "PASS",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}


REQUIRED_CASE_FIELDS = {
    "case_id",
    "case_name",
    "description",
    "threat_class",
    "question",
    "query_date",
    "expected_governance_decision",
    "expected_response_type",
    "evidence_items",
    "citation_index",
    "candidate_claims",
    "expected_claim_results",
    "expected_relationship_result",
    "expected_temporal_result",
    "expected_precedence_decision",
    "expected_groundedness_decision",
    "expected_hallucination_decision",
    "expected_abstention_decision",
    "expected_prompt_injection_decision",
    "expected_final_assurance_decision",
    "requires_human_review",
    "conflict_expected",
    "prompt_injection_expected",
    "abstention_violation_expected",
    "benchmark_tags",
}


REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "document_id",
    "chunk_id",
    "title",
    "document_type",
    "source_type",
    "source_location",
    "source_file",
    "version",
    "effective_date",
    "superseded_date",
    "status",
    "approval_status",
    "replaces_document_id",
    "replaced_by_document_id",
    "page",
    "chunk_number",
    "text",
    "extraction_status",
    "ingestion_batch_id",
}


REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "text",
    "citation_ids",
    "material",
    "claim_type",
}


REQUIRED_EXPECTED_CLAIM_FIELDS = {
    "claim_id",
    "expected_support_status",
    "expected_groundedness_status",
    "expected_overstatement_detected",
    "expected_authority_increase_detected",
    "expected_role_hallucination_detected",
    "expected_temporal_validity",
    "expected_relationship_dependency",
    "required_evidence_ids",
    "forbidden_evidence_ids",
    "required_citation_ids",
}


def _require_mapping(
    value: Any,
    name: str,
) -> dict[str, Any]:
    """Require a dictionary."""

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be an object."
        )

    return value


def _require_list(
    value: Any,
    name: str,
) -> list[Any]:
    """Require a list."""

    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"{name} must be a list."
        )

    return value


def _require_bool(
    value: Any,
    name: str,
) -> bool:
    """Require a boolean."""

    if not isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f"{name} must be a boolean."
        )

    return value


def _require_non_blank_string(
    value: Any,
    name: str,
) -> str:
    """Require a non-blank string."""

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-blank string."
        )

    return value.strip()


def _validate_date_or_none(
    value: Any,
    name: str,
) -> None:
    """Validate YYYY-MM-DD date strings or null."""

    if value is None:
        return

    value = _require_non_blank_string(
        value,
        name,
    )

    try:
        date.fromisoformat(
            value
        )

    except ValueError as exc:
        raise ValueError(
            f"{name} must use YYYY-MM-DD format."
        ) from exc


def _require_fields(
    mapping: dict[str, Any],
    required_fields: set[str],
    context: str,
) -> None:
    """Require all fields from a contract set."""

    missing = (
        required_fields
        - set(
            mapping.keys()
        )
    )

    if missing:
        raise ValueError(
            f"{context} is missing required fields: "
            f"{sorted(missing)}"
        )


def _validate_top_level(
    benchmark: dict[str, Any],
) -> None:
    """Validate benchmark identity and metadata."""

    expected_fields = {
        "benchmark_name",
        "benchmark_version",
        "benchmark_purpose",
        "synthetic_data_only",
        "regression_dependency",
        "created_for_week",
        "cases",
    }

    _require_fields(
        benchmark,
        expected_fields,
        "benchmark",
    )

    if (
        benchmark[
            "benchmark_name"
        ]
        != "Week 26 Adversarial Faithfulness Benchmark"
    ):
        raise ValueError(
            "Unexpected benchmark_name."
        )

    if benchmark[
        "benchmark_version"
    ] != "1.0":
        raise ValueError(
            "Unexpected benchmark_version."
        )

    _require_non_blank_string(
        benchmark[
            "benchmark_purpose"
        ],
        "benchmark_purpose",
    )

    if benchmark[
        "synthetic_data_only"
    ] is not True:
        raise ValueError(
            "synthetic_data_only must be true."
        )

    _require_non_blank_string(
        benchmark[
            "regression_dependency"
        ],
        "regression_dependency",
    )

    if benchmark[
        "created_for_week"
    ] != 26:
        raise ValueError(
            "created_for_week must equal 26."
        )


def _validate_evidence_items(
    case: dict[str, Any],
) -> set[str]:
    """Validate evidence objects and return evidence IDs."""

    case_id = case[
        "case_id"
    ]

    evidence_items = _require_list(
        case[
            "evidence_items"
        ],
        f"{case_id}.evidence_items",
    )

    evidence_ids: set[str] = set()

    for index, raw_evidence in enumerate(
        evidence_items
    ):
        evidence = _require_mapping(
            raw_evidence,
            f"{case_id}.evidence_items[{index}]",
        )

        _require_fields(
            evidence,
            REQUIRED_EVIDENCE_FIELDS,
            f"{case_id}.evidence_items[{index}]",
        )

        evidence_id = _require_non_blank_string(
            evidence[
                "evidence_id"
            ],
            f"{case_id}.evidence_id",
        )

        if evidence_id in evidence_ids:
            raise ValueError(
                f"{case_id} contains duplicate evidence_id "
                f"{evidence_id}."
            )

        evidence_ids.add(
            evidence_id
        )

        for field_name in (
            "document_id",
            "chunk_id",
            "title",
            "document_type",
            "source_type",
            "source_location",
            "source_file",
            "version",
            "text",
            "extraction_status",
            "ingestion_batch_id",
        ):
            _require_non_blank_string(
                evidence[
                    field_name
                ],
                f"{case_id}.{field_name}",
            )

        if evidence[
            "status"
        ] not in ALLOWED_LIFECYCLE_STATUSES:
            raise ValueError(
                f"{case_id} has invalid evidence status "
                f"{evidence['status']}."
            )

        if evidence[
            "approval_status"
        ] not in ALLOWED_APPROVAL_STATUSES:
            raise ValueError(
                f"{case_id} has invalid approval_status "
                f"{evidence['approval_status']}."
            )

        _validate_date_or_none(
            evidence[
                "effective_date"
            ],
            f"{case_id}.effective_date",
        )

        _validate_date_or_none(
            evidence[
                "superseded_date"
            ],
            f"{case_id}.superseded_date",
        )

        if not isinstance(
            evidence[
                "page"
            ],
            int,
        ):
            raise ValueError(
                f"{case_id}.page must be an integer."
            )

        if not isinstance(
            evidence[
                "chunk_number"
            ],
            int,
        ):
            raise ValueError(
                f"{case_id}.chunk_number must be an integer."
            )

        for relationship_field in (
            "replaces_document_id",
            "replaced_by_document_id",
        ):
            value = evidence[
                relationship_field
            ]

            if value is not None:
                _require_non_blank_string(
                    value,
                    f"{case_id}.{relationship_field}",
                )

    return evidence_ids


def _validate_citation_index(
    case: dict[str, Any],
    evidence_ids: set[str],
) -> set[str]:
    """Validate citation-to-evidence mappings."""

    case_id = case[
        "case_id"
    ]

    citation_index = _require_list(
        case[
            "citation_index"
        ],
        f"{case_id}.citation_index",
    )

    citation_ids: set[str] = set()

    for index, raw_citation in enumerate(
        citation_index
    ):
        citation = _require_mapping(
            raw_citation,
            f"{case_id}.citation_index[{index}]",
        )

        _require_fields(
            citation,
            {
                "citation_id",
                "evidence_id",
            },
            f"{case_id}.citation_index[{index}]",
        )

        citation_id = _require_non_blank_string(
            citation[
                "citation_id"
            ],
            f"{case_id}.citation_id",
        )

        evidence_id = _require_non_blank_string(
            citation[
                "evidence_id"
            ],
            f"{case_id}.citation.evidence_id",
        )

        if citation_id in citation_ids:
            raise ValueError(
                f"{case_id} contains duplicate citation_id "
                f"{citation_id}."
            )

        if evidence_id not in evidence_ids:
            raise ValueError(
                f"{case_id} citation {citation_id} references "
                f"unknown evidence {evidence_id}."
            )

        citation_ids.add(
            citation_id
        )

    return citation_ids


def _validate_candidate_claims(
    case: dict[str, Any],
    citation_ids: set[str],
) -> set[str]:
    """Validate candidate claims and return claim IDs."""

    case_id = case[
        "case_id"
    ]

    candidate_claims = _require_list(
        case[
            "candidate_claims"
        ],
        f"{case_id}.candidate_claims",
    )

    claim_ids: set[str] = set()

    for index, raw_claim in enumerate(
        candidate_claims
    ):
        claim = _require_mapping(
            raw_claim,
            f"{case_id}.candidate_claims[{index}]",
        )

        _require_fields(
            claim,
            REQUIRED_CLAIM_FIELDS,
            f"{case_id}.candidate_claims[{index}]",
        )

        claim_id = _require_non_blank_string(
            claim[
                "claim_id"
            ],
            f"{case_id}.claim_id",
        )

        if claim_id in claim_ids:
            raise ValueError(
                f"{case_id} contains duplicate claim_id "
                f"{claim_id}."
            )

        claim_ids.add(
            claim_id
        )

        _require_non_blank_string(
            claim[
                "text"
            ],
            f"{case_id}.{claim_id}.text",
        )

        _require_bool(
            claim[
                "material"
            ],
            f"{case_id}.{claim_id}.material",
        )

        if claim[
            "claim_type"
        ] not in ALLOWED_CLAIM_TYPES:
            raise ValueError(
                f"{case_id}.{claim_id} has invalid claim_type "
                f"{claim['claim_type']}."
            )

        claim_citation_ids = _require_list(
            claim[
                "citation_ids"
            ],
            f"{case_id}.{claim_id}.citation_ids",
        )

        for citation_id in claim_citation_ids:
            citation_id = _require_non_blank_string(
                citation_id,
                f"{case_id}.{claim_id}.citation_id",
            )

            if citation_id not in citation_ids:
                raise ValueError(
                    f"{case_id}.{claim_id} references unknown "
                    f"citation {citation_id}."
                )

    return claim_ids


def _validate_expected_claim_results(
    case: dict[str, Any],
    claim_ids: set[str],
    evidence_ids: set[str],
    citation_ids: set[str],
) -> None:
    """Validate expected claim outcomes."""

    case_id = case[
        "case_id"
    ]

    results = _require_list(
        case[
            "expected_claim_results"
        ],
        f"{case_id}.expected_claim_results",
    )

    expected_claim_ids: set[str] = set()

    for index, raw_result in enumerate(
        results
    ):
        result = _require_mapping(
            raw_result,
            f"{case_id}.expected_claim_results[{index}]",
        )

        _require_fields(
            result,
            REQUIRED_EXPECTED_CLAIM_FIELDS,
            f"{case_id}.expected_claim_results[{index}]",
        )

        claim_id = _require_non_blank_string(
            result[
                "claim_id"
            ],
            f"{case_id}.expected_claim_result.claim_id",
        )

        if claim_id not in claim_ids:
            raise ValueError(
                f"{case_id} expected result references unknown "
                f"claim {claim_id}."
            )

        if claim_id in expected_claim_ids:
            raise ValueError(
                f"{case_id} contains duplicate expected result "
                f"for {claim_id}."
            )

        expected_claim_ids.add(
            claim_id
        )

        if result[
            "expected_support_status"
        ] not in ALLOWED_SUPPORT_STATUSES:
            raise ValueError(
                f"{case_id}.{claim_id} has invalid "
                "expected_support_status."
            )

        if result[
            "expected_groundedness_status"
        ] not in ALLOWED_GROUNDEDNESS_STATUSES:
            raise ValueError(
                f"{case_id}.{claim_id} has invalid "
                "expected_groundedness_status."
            )

        if result[
            "expected_temporal_validity"
        ] not in ALLOWED_TEMPORAL_STATUSES:
            raise ValueError(
                f"{case_id}.{claim_id} has invalid "
                "expected_temporal_validity."
            )

        if result[
            "expected_relationship_dependency"
        ] not in ALLOWED_RELATIONSHIP_DEPENDENCIES:
            raise ValueError(
                f"{case_id}.{claim_id} has invalid "
                "expected_relationship_dependency."
            )

        for bool_field in (
            "expected_overstatement_detected",
            "expected_authority_increase_detected",
            "expected_role_hallucination_detected",
        ):
            _require_bool(
                result[
                    bool_field
                ],
                f"{case_id}.{claim_id}.{bool_field}",
            )

        for evidence_field in (
            "required_evidence_ids",
            "forbidden_evidence_ids",
        ):
            values = _require_list(
                result[
                    evidence_field
                ],
                f"{case_id}.{claim_id}.{evidence_field}",
            )

            for evidence_id in values:
                evidence_id = _require_non_blank_string(
                    evidence_id,
                    f"{case_id}.{claim_id}.{evidence_field}",
                )

                if evidence_id not in evidence_ids:
                    raise ValueError(
                        f"{case_id}.{claim_id} references unknown "
                        f"evidence {evidence_id}."
                    )

        required_citation_ids = _require_list(
            result[
                "required_citation_ids"
            ],
            f"{case_id}.{claim_id}.required_citation_ids",
        )

        for citation_id in required_citation_ids:
            citation_id = _require_non_blank_string(
                citation_id,
                f"{case_id}.{claim_id}.required_citation_id",
            )

            if citation_id not in citation_ids:
                raise ValueError(
                    f"{case_id}.{claim_id} references unknown "
                    f"required citation {citation_id}."
                )

    if expected_claim_ids != claim_ids:
        raise ValueError(
            f"{case_id} expected claim results do not cover "
            "all candidate claims exactly once."
        )


def _validate_case_decisions(
    case: dict[str, Any],
) -> None:
    """Validate case-level expected decision states."""

    case_id = case[
        "case_id"
    ]

    governance = case[
        "expected_governance_decision"
    ]

    response_type = case[
        "expected_response_type"
    ]

    if governance not in ALLOWED_GOVERNANCE:
        raise ValueError(
            f"{case_id} has invalid governance decision."
        )

    if response_type not in ALLOWED_RESPONSE_TYPES:
        raise ValueError(
            f"{case_id} has invalid response type."
        )

    expected_response = (
        GOVERNANCE_TO_RESPONSE[
            governance
        ]
    )

    if response_type != expected_response:
        raise ValueError(
            f"{case_id} response type does not match "
            f"governance. Expected {expected_response}."
        )

    if case[
        "expected_relationship_result"
    ] not in ALLOWED_RELATIONSHIP_RESULTS:
        raise ValueError(
            f"{case_id} has invalid relationship result."
        )

    if case[
        "expected_temporal_result"
    ] not in ALLOWED_TEMPORAL_STATUSES:
        raise ValueError(
            f"{case_id} has invalid temporal result."
        )

    if case[
        "expected_precedence_decision"
    ] not in ALLOWED_PRECEDENCE_DECISIONS:
        raise ValueError(
            f"{case_id} has invalid precedence decision."
        )

    if case[
        "expected_groundedness_decision"
    ] not in ALLOWED_GROUNDEDNESS_STATUSES:
        raise ValueError(
            f"{case_id} has invalid groundedness decision."
        )

    if case[
        "expected_hallucination_decision"
    ] not in ALLOWED_HALLUCINATION_DECISIONS:
        raise ValueError(
            f"{case_id} has invalid hallucination decision."
        )

    if case[
        "expected_abstention_decision"
    ] not in ALLOWED_ABSTENTION_DECISIONS:
        raise ValueError(
            f"{case_id} has invalid abstention decision."
        )

    if case[
        "expected_prompt_injection_decision"
    ] not in ALLOWED_PROMPT_INJECTION_DECISIONS:
        raise ValueError(
            f"{case_id} has invalid prompt injection decision."
        )

    final_decision = case[
        "expected_final_assurance_decision"
    ]

    if final_decision not in ALLOWED_FINAL_ASSURANCE_DECISIONS:
        raise ValueError(
            f"{case_id} has invalid final assurance decision."
        )

    if governance == "REVIEW_REQUIRED":
        if final_decision != "REVIEW_REQUIRED":
            raise ValueError(
                f"{case_id} illegally increases review governance."
            )

    if governance == "ABSTAIN":
        if final_decision != "ABSTAIN":
            raise ValueError(
                f"{case_id} illegally increases abstention governance."
            )


def _validate_case_flags(
    case: dict[str, Any],
) -> None:
    """Validate case-level booleans and tag alignment."""

    case_id = case[
        "case_id"
    ]

    for bool_field in (
        "requires_human_review",
        "conflict_expected",
        "prompt_injection_expected",
        "abstention_violation_expected",
    ):
        _require_bool(
            case[
                bool_field
            ],
            f"{case_id}.{bool_field}",
        )

    tags = _require_list(
        case[
            "benchmark_tags"
        ],
        f"{case_id}.benchmark_tags",
    )

    normalised_tags = {
        _require_non_blank_string(
            tag,
            f"{case_id}.benchmark_tag",
        )
        for tag in tags
    }

    if (
        case[
            "prompt_injection_expected"
        ]
        and "prompt_injection"
        not in normalised_tags
    ):
        raise ValueError(
            f"{case_id} expects prompt injection but lacks "
            "prompt_injection tag."
        )

    if (
        case[
            "abstention_violation_expected"
        ]
        and case[
            "expected_governance_decision"
        ]
        != "ABSTAIN"
    ):
        raise ValueError(
            f"{case_id} abstention violation requires "
            "ABSTAIN governance."
        )


def _validate_candidate_response(
    case: dict[str, Any],
) -> None:
    """Validate optional abstention candidate response."""

    if "candidate_response" not in case:
        return

    case_id = case[
        "case_id"
    ]

    response = _require_mapping(
        case[
            "candidate_response"
        ],
        f"{case_id}.candidate_response",
    )

    required_sections = {
        "unable_to_answer_safely",
        "reason",
        "missing_information",
        "what_is_needed_to_continue",
    }

    _require_fields(
        response,
        required_sections,
        f"{case_id}.candidate_response",
    )

    for section in required_sections:
        _require_non_blank_string(
            response[
                section
            ],
            f"{case_id}.candidate_response.{section}",
        )

    if case[
        "expected_governance_decision"
    ] != "ABSTAIN":
        raise ValueError(
            f"{case_id} candidate_response is only valid "
            "for ABSTAIN governance cases."
        )


def _validate_case(
    case: dict[str, Any],
) -> None:
    """Validate one Week 26 benchmark case."""

    _require_fields(
        case,
        REQUIRED_CASE_FIELDS,
        "benchmark case",
    )

    case_id = _require_non_blank_string(
        case[
            "case_id"
        ],
        "case_id",
    )

    _require_non_blank_string(
        case[
            "case_name"
        ],
        f"{case_id}.case_name",
    )

    _require_non_blank_string(
        case[
            "description"
        ],
        f"{case_id}.description",
    )

    _require_non_blank_string(
        case[
            "threat_class"
        ],
        f"{case_id}.threat_class",
    )

    _require_non_blank_string(
        case[
            "question"
        ],
        f"{case_id}.question",
    )

    _validate_date_or_none(
        case[
            "query_date"
        ],
        f"{case_id}.query_date",
    )

    evidence_ids = _validate_evidence_items(
        case
    )

    citation_ids = _validate_citation_index(
        case,
        evidence_ids,
    )

    claim_ids = _validate_candidate_claims(
        case,
        citation_ids,
    )

    _validate_expected_claim_results(
        case,
        claim_ids,
        evidence_ids,
        citation_ids,
    )

    _validate_case_decisions(
        case
    )

    _validate_case_flags(
        case
    )

    _validate_candidate_response(
        case
    )


def validate_benchmark(
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    """Validate the complete Week 26 benchmark."""

    benchmark = _require_mapping(
        benchmark,
        "benchmark",
    )

    _validate_top_level(
        benchmark
    )

    cases = _require_list(
        benchmark[
            "cases"
        ],
        "cases",
    )

    if len(
        cases
    ) != EXPECTED_CASE_COUNT:
        raise ValueError(
            "Week 26 benchmark must contain exactly "
            f"{EXPECTED_CASE_COUNT} cases."
        )

    case_ids: list[str] = []

    for raw_case in cases:
        case = _require_mapping(
            raw_case,
            "benchmark case",
        )

        _validate_case(
            case
        )

        case_ids.append(
            case[
                "case_id"
            ]
        )

    if case_ids != EXPECTED_CASE_IDS:
        raise ValueError(
            "Week 26 case IDs must be sequential "
            "W26-C001 through W26-C012."
        )

    if len(
        set(
            case_ids
        )
    ) != EXPECTED_CASE_COUNT:
        raise ValueError(
            "Week 26 benchmark contains duplicate case IDs."
        )

    governance_counts = {
        decision: sum(
            1
            for case in cases
            if case[
                "expected_governance_decision"
            ]
            == decision
        )
        for decision in sorted(
            ALLOWED_GOVERNANCE
        )
    }

    final_decision_counts = {
        decision: sum(
            1
            for case in cases
            if case[
                "expected_final_assurance_decision"
            ]
            == decision
        )
        for decision in sorted(
            ALLOWED_FINAL_ASSURANCE_DECISIONS
        )
    }

    prompt_injection_count = sum(
        1
        for case in cases
        if case[
            "prompt_injection_expected"
        ]
    )

    abstention_violation_count = sum(
        1
        for case in cases
        if case[
            "abstention_violation_expected"
        ]
    )

    conflict_count = sum(
        1
        for case in cases
        if case[
            "conflict_expected"
        ]
    )

    human_review_count = sum(
        1
        for case in cases
        if case[
            "requires_human_review"
        ]
    )

    return {
        "benchmark_name": (
            benchmark[
                "benchmark_name"
            ]
        ),
        "benchmark_version": (
            benchmark[
                "benchmark_version"
            ]
        ),
        "case_count": len(
            cases
        ),
        "governance_counts": (
            governance_counts
        ),
        "final_decision_counts": (
            final_decision_counts
        ),
        "prompt_injection_case_count": (
            prompt_injection_count
        ),
        "abstention_violation_case_count": (
            abstention_violation_count
        ),
        "conflict_case_count": (
            conflict_count
        ),
        "human_review_count": (
            human_review_count
        ),
        "validation_status": "PASS",
    }


def load_benchmark() -> dict[str, Any]:
    """Load the Week 26 adversarial benchmark."""

    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {BENCHMARK_PATH}"
        )

    with BENCHMARK_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(
            file
        )


def main() -> None:
    """CLI entry point."""

    benchmark = load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    print(
        "Week 26 Adversarial Benchmark Validation"
    )

    print(
        "----------------------------------------"
    )

    print(
        f"Benchmark: {result['benchmark_name']}"
    )

    print(
        f"Cases: {result['case_count']}"
    )

    print(
        "Upstream governance:"
    )

    for decision, count in result[
        "governance_counts"
    ].items():
        print(
            f"  {decision}: {count}"
        )

    print(
        "Final assurance decisions:"
    )

    for decision, count in result[
        "final_decision_counts"
    ].items():
        print(
            f"  {decision}: {count}"
        )

    print(
        "Prompt-injection cases: "
        f"{result['prompt_injection_case_count']}"
    )

    print(
        "Abstention-violation cases: "
        f"{result['abstention_violation_case_count']}"
    )

    print(
        "Conflict cases: "
        f"{result['conflict_case_count']}"
    )

    print(
        "Cases requiring human review: "
        f"{result['human_review_count']}"
    )

    print(
        f"Validation: {result['validation_status']}"
    )


if __name__ == "__main__":
    main()