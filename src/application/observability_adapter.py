"""Week 27 Day 4 — safe observability adapter for RAG application results."""

from __future__ import annotations

from typing import Any

from src.application.observability import (
    EVENT_ASSURANCE,
    EVENT_FAILURE,
    EVENT_FINAL,
    EVENT_GENERATION,
    EVENT_GOVERNANCE,
    EVENT_REQUEST,
    EVENT_RETRIEVAL,
    EVENT_STAGE,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_STARTED,
    ObservabilityTrace,
)


_STAGE_EVENT_TYPES = {
    "REQUEST_RECEIVED": EVENT_REQUEST,
    "INPUT_VALIDATED": EVENT_STAGE,
    "RETRIEVAL_COMPLETED": EVENT_RETRIEVAL,
    "EVIDENCE_PACKET_BUILT": EVENT_STAGE,
    "PRE_GOVERNANCE_COMPLETED": EVENT_GOVERNANCE,
    "ANSWER_CONTRACT_BUILT": EVENT_GENERATION,
    "ANSWER_CONTEXT_BUILT": EVENT_GENERATION,
    "DETERMINISTIC_RESPONSE_BUILT": EVENT_GENERATION,
    "MODEL_EXECUTION_COMPLETED": EVENT_GENERATION,
    "RESPONSE_SELECTED": EVENT_GENERATION,
    "ASSURANCE_COMPLETED": EVENT_ASSURANCE,
    "FINAL_GOVERNANCE_COMPLETED": EVENT_FINAL,
}


_SAFE_RUNTIME_KEYS = {
    "source",
    "execution_mode",
}


def _require_dictionary(
    value: Any,
    name: str,
) -> dict:
    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be a dictionary."
        )

    return value


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _safe_runtime_metadata(
    governance: dict,
) -> dict:
    runtime = governance.get(
        "runtime",
        {},
    )

    if not isinstance(
        runtime,
        dict,
    ):
        return {}

    output: dict = {}

    for key in _SAFE_RUNTIME_KEYS:
        value = runtime.get(
            key
        )

        if isinstance(
            value,
            (
                str,
                bool,
                int,
                float,
            ),
        ) or value is None:
            output[
                key
            ] = value

    metadata = runtime.get(
        "metadata"
    )

    if isinstance(
        metadata,
        dict,
    ):
        for key in (
            "environment",
            "application_name",
            "runtime_version",
        ):
            value = metadata.get(
                key
            )

            if isinstance(
                value,
                str,
            ):
                output[
                    key
                ] = value

    return output


def _safe_retrieval_metadata(
    result: dict,
) -> dict:
    evidence = result.get(
        "evidence",
        {},
    )

    if not isinstance(
        evidence,
        dict,
    ):
        return {}

    output: dict = {}

    retrieval_route = evidence.get(
        "retrieval_route"
    )

    if isinstance(
        retrieval_route,
        str,
    ):
        output[
            "retrieval_route"
        ] = retrieval_route

    evidence_count = evidence.get(
        "evidence_count"
    )

    if (
        isinstance(
            evidence_count,
            int,
        )
        and not isinstance(
            evidence_count,
            bool,
        )
    ):
        output[
            "evidence_count"
        ] = evidence_count

    evidence_sufficient = evidence.get(
        "evidence_sufficient"
    )

    if isinstance(
        evidence_sufficient,
        bool,
    ):
        output[
            "evidence_sufficient"
        ] = evidence_sufficient

    precedence_decision = evidence.get(
        "precedence_decision"
    )

    if isinstance(
        precedence_decision,
        str,
    ):
        output[
            "precedence_decision"
        ] = precedence_decision

    return output


def _safe_governance_metadata(
    result: dict,
) -> dict:
    governance = result.get(
        "governance",
        {},
    )

    if not isinstance(
        governance,
        dict,
    ):
        return {}

    output = _safe_runtime_metadata(
        governance
    )

    for key in (
        "pre_generation_decision",
        "final_decision",
    ):
        value = governance.get(
            key
        )

        if isinstance(
            value,
            str,
        ):
            output[
                key
            ] = value

    return output


def _safe_assurance_metadata(
    result: dict,
) -> dict:
    assurance = result.get(
        "assurance",
        {},
    )

    if not isinstance(
        assurance,
        dict,
    ):
        return {}

    output: dict = {}

    for key in (
        "status",
        "final_assurance_decision",
    ):
        value = assurance.get(
            key
        )

        if isinstance(
            value,
            str,
        ):
            output[
                key
            ] = value

    for key in (
        "required_checks_complete",
        "authority_increased",
    ):
        value = assurance.get(
            key
        )

        if isinstance(
            value,
            bool,
        ):
            output[
                key
            ] = value

    return output


def _safe_final_metadata(
    result: dict,
) -> dict:
    output: dict = {}

    final_outcome = result.get(
        "final_outcome"
    )

    if isinstance(
        final_outcome,
        str,
    ):
        output[
            "final_outcome"
        ] = final_outcome

    status = result.get(
        "status"
    )

    if isinstance(
        status,
        str,
    ):
        output[
            "application_status"
        ] = status

    return output


def _safe_failure_metadata(
    result: dict,
) -> dict:
    failure = result.get(
        "failure",
        {},
    )

    if not isinstance(
        failure,
        dict,
    ):
        return {}

    output: dict = {}

    stage = failure.get(
        "stage"
    )

    if isinstance(
        stage,
        str,
    ):
        output[
            "failure_stage"
        ] = stage

    error_type = failure.get(
        "error_type"
    )

    if isinstance(
        error_type,
        str,
    ):
        output[
            "error_type"
        ] = error_type

    return output


def _metadata_for_stage(
    stage: str,
    result: dict,
) -> dict:
    if stage == "REQUEST_RECEIVED":
        governance = result.get(
            "governance",
            {},
        )

        if not isinstance(
            governance,
            dict,
        ):
            return {}

        return _safe_runtime_metadata(
            governance
        )

    if stage == "RETRIEVAL_COMPLETED":
        return _safe_retrieval_metadata(
            result
        )

    if stage == "PRE_GOVERNANCE_COMPLETED":
        return _safe_governance_metadata(
            result
        )

    if stage == "ASSURANCE_COMPLETED":
        return _safe_assurance_metadata(
            result
        )

    if stage == "FINAL_GOVERNANCE_COMPLETED":
        metadata = (
            _safe_governance_metadata(
                result
            )
        )

        metadata.update(
            _safe_final_metadata(
                result
            )
        )

        return metadata

    return {}


def build_pipeline_observability(
    result: dict,
) -> list[dict]:
    """Build a safe structured event trace from one RAG pipeline result."""

    result = _require_dictionary(
        result,
        "result",
    )

    request_id = _require_non_empty_string(
        result.get(
            "request_id"
        ),
        "result.request_id",
    )

    execution_trace = result.get(
        "execution_trace"
    )

    if not isinstance(
        execution_trace,
        list,
    ):
        raise ValueError(
            "result.execution_trace must be a list."
        )

    trace = ObservabilityTrace(
        request_id
    )

    for index, stage in enumerate(
        execution_trace
    ):
        stage = _require_non_empty_string(
            stage,
            (
                "execution_trace"
                f"[{index}]"
            ),
        )

        event_type = _STAGE_EVENT_TYPES.get(
            stage,
            EVENT_STAGE,
        )

        status = (
            STATUS_STARTED
            if stage
            == "REQUEST_RECEIVED"
            else STATUS_COMPLETED
        )

        trace.record(
            event_type=event_type,
            stage=stage,
            status=status,
            metadata=_metadata_for_stage(
                stage,
                result,
            ),
        )

    failure = result.get(
        "failure"
    )

    if isinstance(
        failure,
        dict,
    ):
        failure_stage = failure.get(
            "stage",
            "UNKNOWN_FAILURE",
        )

        if not isinstance(
            failure_stage,
            str,
        ) or not failure_stage.strip():
            failure_stage = (
                "UNKNOWN_FAILURE"
            )

        trace.record(
            event_type=EVENT_FAILURE,
            stage=failure_stage,
            status=STATUS_FAILED,
            metadata=_safe_failure_metadata(
                result
            ),
        )

    elif result.get(
        "final_outcome"
    ) is not None:
        final_stage_present = any(
            event.get(
                "stage"
            )
            == "FINAL_GOVERNANCE_COMPLETED"
            for event
            in trace.to_list()
        )

        if not final_stage_present:
            trace.record(
                event_type=EVENT_FINAL,
                stage="FINAL_OUTCOME",
                status=STATUS_COMPLETED,
                metadata=_safe_final_metadata(
                    result
                ),
            )

    return trace.to_list()