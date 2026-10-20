"""Canonical Week 27 application pipeline.

Session 6 scope:

Question
-> application request validation
-> governed retrieval
-> canonical Evidence Packet
-> coherent pre-generation governance
-> existing Answer Contract and Answer Context
-> deterministic response and optional controlled model execution
-> one selected response candidate
-> request-level assurance and final governance
-> structured application result

Only the exact assured candidate may be released as ANSWER. Other outcomes
withhold candidate text and preserve the original authority ceiling.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from src.application.assurance import (
    AssuranceIntegrationError, assure_selected_response, finalize_request_governance,
)
from src.application.contracts import (
    OUTCOME_ABSTAIN,
    OUTCOME_ANSWER,
    OUTCOME_REVIEW_REQUIRED,
    RAGRequest,
    RAGResult,
    STATUS_COMPLETED,
    build_failed_closed_result,
    build_request_id,
)
from src.evidence.evidence_packet import (
    build_evidence_packet,
)
from src.evidence.evidence_precedence import (
    BLOCK_COMBINATION,
    REVIEW_BEFORE_COMBINATION,
    SAFE_TO_COMBINE,
)
from src.generation.answer_contract import build_answer_contract
from src.generation.answer_context import build_answer_context
from src.generation.generation_fallback import resolve_generation_with_fallback
from src.generation.grounded_answer import build_grounded_response
from src.generation.model_execution import execute_governed_model
from src.governance.review_decision import ABSTAIN, AUTO_ANSWER, REVIEW_REQUIRED
from src.retrieval.retrieval_orchestrator import (
    orchestrate_retrieval,
)


STAGE_REQUEST_RECEIVED = "REQUEST_RECEIVED"
STAGE_INPUT_VALIDATED = "INPUT_VALIDATED"
STAGE_RETRIEVAL_COMPLETED = "RETRIEVAL_COMPLETED"
STAGE_EVIDENCE_PACKET_BUILT = "EVIDENCE_PACKET_BUILT"
STAGE_PRE_GOVERNANCE_COMPLETED = "PRE_GOVERNANCE_COMPLETED"
STAGE_ANSWER_CONTRACT_BUILT = "ANSWER_CONTRACT_BUILT"
STAGE_ANSWER_CONTEXT_BUILT = "ANSWER_CONTEXT_BUILT"
STAGE_DETERMINISTIC_RESPONSE_BUILT = "DETERMINISTIC_RESPONSE_BUILT"
STAGE_MODEL_EXECUTION_COMPLETED = "MODEL_EXECUTION_COMPLETED"
STAGE_RESPONSE_SELECTED = "RESPONSE_SELECTED"
STAGE_ASSURANCE_COMPLETED = "ASSURANCE_COMPLETED"
STAGE_FINAL_GOVERNANCE_COMPLETED = "FINAL_GOVERNANCE_COMPLETED"

DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
CONTROLLED_PROVIDER = "CONTROLLED_PROVIDER"


def compose_pre_generation_governance(evidence_packet: dict) -> dict:
    """Apply existing precedence restrictions without upgrading governance.

    BLOCK_COMBINATION requires human conflict resolution, as in the existing
    manager evidence brief. It never permits automatic answer generation.
    Original packet assessments are copied for audit, not mutated.
    """
    if not isinstance(evidence_packet, dict):
        raise ValueError("evidence_packet must be a dictionary.")

    governance = evidence_packet.get("governance")
    precedence = evidence_packet.get("precedence_assessment")
    if not isinstance(governance, dict):
        raise ValueError("packet governance must be a dictionary.")
    if not isinstance(precedence, dict):
        raise ValueError("packet precedence must be a dictionary.")

    decision = governance.get("decision")
    if not isinstance(decision, str) or decision not in {
        AUTO_ANSWER, REVIEW_REQUIRED, ABSTAIN,
    }:
        raise ValueError("Unknown or malformed packet governance decision.")
    precedence_decision = precedence.get("decision")
    if not isinstance(precedence_decision, str) or precedence_decision not in {
        SAFE_TO_COMBINE, REVIEW_BEFORE_COMBINATION, BLOCK_COMBINATION,
    }:
        raise ValueError("Unknown or malformed packet precedence decision.")

    _require_non_empty_string(governance.get("reason"), "governance.reason")
    document_ids = _require_list(
        governance.get("document_ids"), "governance.document_ids",
    )
    for document_id in document_ids:
        _require_non_empty_string(document_id, "governance document_id")

    # These are the mature governance flags, not a new confidence algorithm.
    if governance.get("may_generate_answer") is not (decision == AUTO_ANSWER):
        raise ValueError("Governance generation permission contradicts decision.")
    if governance.get("requires_human_review") is not (decision == REVIEW_REQUIRED):
        raise ValueError("Governance review requirement contradicts decision.")
    if "reason" in precedence:
        _require_non_empty_string(precedence["reason"], "precedence.reason")

    effective = deepcopy(governance)
    reduction_reason = None
    if decision == AUTO_ANSWER and precedence_decision != SAFE_TO_COMBINE:
        reduction_reason = (
            "Evidence combination is blocked pending human conflict resolution."
            if precedence_decision == BLOCK_COMBINATION
            else "Evidence precedence requires human review before combination."
        )
        effective.update(
            decision=REVIEW_REQUIRED,
            reason=reduction_reason,
            may_generate_answer=False,
            requires_human_review=True,
        )

    return {
        "original_pre_generation": deepcopy(governance),
        "effective_pre_generation": effective,
        "precedence": deepcopy(precedence),
        "authority_reduced": effective["decision"] != decision,
        "reduction_reason": reduction_reason,
    }


def _require_list(
    value: Any,
    name: str,
) -> list:
    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"{name} must be a list."
        )

    return value


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _validate_runtime_dependencies(
    *,
    chunks: list,
    embedded_chunks: list,
    embedding_model: Any,
    embedding_model_name: str,
) -> None:
    """Validate only application-level dependency presence and shape.

    Lower-level retrieval validation remains authoritative for subsystem
    details such as retrieval sizes, thresholds and model compatibility.
    """

    _require_list(
        chunks,
        "chunks",
    )

    _require_list(
        embedded_chunks,
        "embedded_chunks",
    )

    if embedding_model is None:
        raise ValueError(
            "embedding_model is required."
        )

    _require_non_empty_string(
        embedding_model_name,
        "embedding_model_name",
    )


def _map_governance_to_application_outcome(
    governance_decision: str,
) -> str:
    """Map a governance ceiling; release still requires completed assurance."""

    if governance_decision == "ABSTAIN":
        return OUTCOME_ABSTAIN

    if governance_decision == AUTO_ANSWER:
        return OUTCOME_ANSWER
    if governance_decision == REVIEW_REQUIRED:
        return OUTCOME_REVIEW_REQUIRED

    raise ValueError("Unknown final governance decision.")


def _summarize_selected_response(selected_response: dict, answer_context: dict) -> dict:
    """Check the composition envelope, without replacing model validation.

    Keep the exact candidate intact for request-level assurance. Unreleased
    candidates contribute only identity/permission summaries to the result.
    """
    if not isinstance(selected_response, dict):
        raise ValueError("selected_response must be a dictionary.")
    for key in ("packet_id", "governance_decision", "response_type"):
        if selected_response.get(key) != answer_context[key]:
            raise ValueError(f"Selected response {key} does not match Answer Context.")
    if selected_response.get("requires_human_review") is not answer_context["requires_human_review"]:
        raise ValueError("Selected response review requirement does not match Answer Context.")
    sections = selected_response.get("sections")
    if not isinstance(sections, dict) or not sections:
        raise ValueError("Selected response must contain non-empty structured sections.")
    if not set(sections) <= set(answer_context["allowed_sections"]):
        raise ValueError("Selected response contains sections outside the governed context.")
    citations = _require_list(selected_response.get("citations_used"), "citations_used")
    if answer_context["governance_decision"] == ABSTAIN and citations:
        raise ValueError("Selected abstention must not contain citations.")
    return {
        "packet_id": selected_response["packet_id"],
        "governance_decision": selected_response["governance_decision"],
        "response_type": selected_response["response_type"],
        "requires_human_review": selected_response["requires_human_review"],
        "generation_status": selected_response.get("generation_status"),
        "model_generation_status": selected_response.get("model_generation_status"),
        "citation_count": len(citations),
    }


def _build_evidence_summary(
    evidence_packet: dict,
) -> dict:
    """Build the compact application-level evidence summary."""

    retrieval = evidence_packet.get(
        "retrieval",
        {},
    )

    evidence_sufficiency = evidence_packet.get(
        "evidence_sufficiency",
        {},
    )

    precedence = evidence_packet.get(
        "precedence_assessment",
        {},
    )

    return {
        "evidence_count": evidence_packet.get(
            "evidence_count",
            0,
        ),
        "document_ids": list(
            evidence_packet.get(
                "document_ids",
                [],
            )
        ),
        "retrieval_route": retrieval.get(
            "route"
        ),
        "retrieval_stop_reason": retrieval.get(
            "stop_reason"
        ),
        "evidence_sufficient": (
            evidence_sufficiency.get(
                "sufficient"
            )
            if isinstance(
                evidence_sufficiency,
                dict,
            )
            else None
        ),
        "lifecycle_summary": evidence_packet.get(
            "lifecycle_summary",
            {},
        ),
        "provenance_summary": evidence_packet.get(
            "provenance_summary",
            {},
        ),
        "precedence_decision": (
            precedence.get(
                "decision"
            )
            if isinstance(
                precedence,
                dict,
            )
            else None
        ),
    }


def run_rag_pipeline(
    *,
    question: str,
    chunks: list,
    embedded_chunks: list,
    embedding_model: Any,
    embedding_model_name: str,
    semantic_k: int = 10,
    keyword_k: int = 10,
    final_k: int = 3,
    semantic_min_similarity: float | None = None,
    keyword_min_score: float | None = None,
    min_rrf_score: float | None = None,
    rrf_k: int = 60,
    max_related_chunks: int = 2,
    execution_mode: str = DETERMINISTIC_ONLY,
    model_provider: Any = None,
    query_date: str | None = None,
) -> dict:
    """Run the current Week 27 canonical application path.

    Release the selected candidate only after required assurance succeeds.
    Missing trusted date metadata restricts authority rather than being invented.
    """

    execution_trace: list[str] = [
        STAGE_REQUEST_RECEIVED,
    ]

    safe_question = (
        question
        if isinstance(
            question,
            str,
        )
        and question.strip()
        else "INVALID_REQUEST"
    )

    try:
        request = RAGRequest(
            question=question
        )

        if not isinstance(execution_mode, str) or execution_mode not in {
            DETERMINISTIC_ONLY, CONTROLLED_PROVIDER,
        }:
            raise ValueError("Unknown execution_mode.")
        if execution_mode == CONTROLLED_PROVIDER and model_provider is None:
            raise ValueError("model_provider is required in CONTROLLED_PROVIDER mode.")
        if query_date is not None:
            if not isinstance(query_date, str) or date.fromisoformat(query_date).isoformat() != query_date:
                raise ValueError("query_date must use YYYY-MM-DD format.")

        _validate_runtime_dependencies(
            chunks=chunks,
            embedded_chunks=embedded_chunks,
            embedding_model=embedding_model,
            embedding_model_name=embedding_model_name,
        )

        execution_trace.append(
            STAGE_INPUT_VALIDATED
        )

    except Exception as exc:
        return build_failed_closed_result(
            question=safe_question,
            stage="INPUT_VALIDATION",
            error=exc,
            execution_trace=execution_trace,
        )

    try:
        retrieval_output = orchestrate_retrieval(
            query=request.question,
            chunks=chunks,
            embedded_chunks=embedded_chunks,
            model=embedding_model,
            embedding_model=embedding_model_name,
            semantic_k=semantic_k,
            keyword_k=keyword_k,
            final_k=final_k,
            semantic_min_similarity=semantic_min_similarity,
            keyword_min_score=keyword_min_score,
            min_rrf_score=min_rrf_score,
            rrf_k=rrf_k,
            max_related_chunks=max_related_chunks,
        )

        execution_trace.append(
            STAGE_RETRIEVAL_COMPLETED
        )

    except Exception as exc:
        return build_failed_closed_result(
            question=request.question,
            stage="RETRIEVAL",
            error=exc,
            execution_trace=execution_trace,
        )

    try:
        evidence_packet = build_evidence_packet(
            request.question,
            retrieval_output,
        )

        execution_trace.append(
            STAGE_EVIDENCE_PACKET_BUILT
        )

    except Exception as exc:
        return build_failed_closed_result(
            question=request.question,
            stage="EVIDENCE_PACKET",
            error=exc,
            execution_trace=execution_trace,
        )

    preparation_stage = "PRE_GENERATION_GOVERNANCE"
    governance_audit: dict = {}
    assurance: dict = {}
    try:
        if not isinstance(evidence_packet, dict):
            raise ValueError("evidence_packet must be a dictionary.")
        # Preserve raw assessments even if validation/composition later fails.
        governance_audit = {
            "original_pre_generation": deepcopy(evidence_packet.get("governance")),
            "precedence": deepcopy(evidence_packet.get("precedence_assessment")),
        }
        governance_audit.update(compose_pre_generation_governance(evidence_packet))
        effective = governance_audit["effective_pre_generation"]
        governance_audit["pre_generation"] = deepcopy(
            governance_audit["original_pre_generation"]
        )
        final_outcome = _map_governance_to_application_outcome(effective["decision"])
        governance_audit["application_release_ceiling"] = final_outcome
        governance_audit["authority_increased"] = False
        execution_trace.append(STAGE_PRE_GOVERNANCE_COMPLETED)

        # Both mature builders must see the same effective, packet-bound state.
        preparation_packet = deepcopy(evidence_packet)
        preparation_packet["governance"] = deepcopy(effective)
        preparation_stage = "ANSWER_CONTRACT"
        answer_contract = build_answer_contract(preparation_packet)
        execution_trace.append(STAGE_ANSWER_CONTRACT_BUILT)

        preparation_stage = "ANSWER_CONTEXT"
        answer_context = build_answer_context(preparation_packet, answer_contract)
        execution_trace.append(STAGE_ANSWER_CONTEXT_BUILT)

        # Compact preparation summaries intentionally exclude evidence text.
        governance_audit["answer_contract"] = {
            key: answer_contract[key]
            for key in (
                "packet_id", "governance_decision", "response_type",
                "may_generate_answer", "requires_human_review",
            )
        }
        governance_audit["answer_context"] = {
            key: answer_context[key]
            for key in (
                "packet_id", "governance_decision", "response_type",
                "generation_permitted", "requires_human_review", "precedence_decision",
            )
        }
        governance_audit["answer_context"].update(
            evidence_count=len(answer_context["evidence_context"]),
            citation_count=len(answer_context["citation_index"]),
        )

        preparation_stage = "DETERMINISTIC_RESPONSE"
        deterministic_response = build_grounded_response(answer_contract, answer_context)
        execution_trace.append(STAGE_DETERMINISTIC_RESPONSE_BUILT)

        generation_audit = {
            "execution_mode": execution_mode,
            "final_response_source": DETERMINISTIC_ONLY,
            "model_execution_status": None,
            "fallback_used": False,
            "provider_name": None,
            "model_name": None,
            "failure_type": None,
            "failure_reason": None,
            "fallback_reason": None,
            "provider_execution": "SKIPPED_WITH_REASON",
            "provider_skip_reason": (
                "ABSTAIN requires deterministic abstention."
                if effective["decision"] == ABSTAIN
                else "DETERMINISTIC_ONLY mode does not execute a provider."
            ),
            "selected_response_released": False,
        }
        governance_audit["generation"] = generation_audit
        selected_response = deterministic_response
        if execution_mode == CONTROLLED_PROVIDER and effective["decision"] != ABSTAIN:
            preparation_stage = "MODEL_EXECUTION"
            generation_audit.update(
                final_response_source=None,
                provider_execution="FAILED",
                provider_skip_reason=None,
            )
            execution_result = execute_governed_model(answer_context, model_provider)
            execution_trace.append(STAGE_MODEL_EXECUTION_COMPLETED)
            generation_audit.update(
                model_execution_status=execution_result["execution_status"],
                provider_name=execution_result["provider_name"],
                model_name=execution_result["model_name"],
                failure_type=execution_result["failure_type"],
                failure_reason=execution_result["failure_reason"],
                provider_execution="EXECUTED",
                provider_skip_reason=None,
            )
            preparation_stage = "FALLBACK_RESOLUTION"
            resolution = resolve_generation_with_fallback(execution_result, deterministic_response)
            generation_audit.update(
                final_response_source=resolution["final_response_source"],
                fallback_used=resolution["fallback_used"],
                fallback_reason=resolution["fallback_reason"],
            )
            preparation_stage = "RESPONSE_SELECTION"
            selected_response = resolution["final_response"]

        preparation_stage = "RESPONSE_SELECTION"
        generation_audit["selected_response"] = _summarize_selected_response(
            selected_response, answer_context,
        )
        execution_trace.append(STAGE_RESPONSE_SELECTED)

        preparation_stage = "CLAIM_ADAPTATION"
        selected_snapshot = deepcopy(selected_response)
        assurance = assure_selected_response(
            selected_response, answer_context, preparation_packet,
            deterministic_response=deterministic_response, query_date=query_date,
            retrieval_results=retrieval_output.get("results", []),
        )
        execution_trace.append(STAGE_ASSURANCE_COMPLETED)
        preparation_stage = "FINAL_GOVERNANCE"
        final_governance = finalize_request_governance(
            effective, assurance, request_id=build_request_id(request.question),
            fallback_used=generation_audit["fallback_used"],
        )
        if selected_response != selected_snapshot:
            raise ValueError("Assurance changed the selected response.")
        final_outcome = _map_governance_to_application_outcome(final_governance["decision"])
        if (
            final_governance.get("requires_human_review") is not (final_outcome == OUTCOME_REVIEW_REQUIRED)
            or final_governance.get("may_return_answer") is not (final_outcome == OUTCOME_ANSWER)
        ):
            raise ValueError("Final governance flags contradict the final response outcome.")
        if final_outcome == OUTCOME_ANSWER and (
            effective["decision"] != AUTO_ANSWER
            or selected_response["governance_decision"] != AUTO_ANSWER
            or assurance.get("required_checks_complete") is not True
            or assurance.get("final_assurance_decision") != "PASS"
        ):
            raise ValueError("Final response and governance do not permit answer release.")
        governance_audit.update(final_governance)
        governance_audit["final_decision"] = final_governance["decision"]
        governance_audit["application_release_ceiling"] = final_outcome
        execution_trace.append(STAGE_FINAL_GOVERNANCE_COMPLETED)

        preparation_stage = "APPLICATION_RESULT"
        if final_outcome == OUTCOME_ANSWER:
            response = selected_response
            generation_audit["selected_response_released"] = True
        elif final_outcome == OUTCOME_ABSTAIN and effective["decision"] == ABSTAIN:
            response = selected_response
            generation_audit["selected_response_released"] = True
        elif final_outcome == OUTCOME_ABSTAIN:
            response = {
                "unable_to_answer_safely": (
                    "The governed evidence path does not permit an answer."
                ),
                "reason": "Final governance requires abstention.",
                "missing_information": "Sufficient approved evidence is required.",
                "what_is_needed_to_continue": (
                    "Provide sufficient approved evidence or an in-scope question."
                ),
            }
        else:
            response = {
                "evidence_summary": (
                    "Governed evidence and a generation candidate have been prepared."
                ),
                "why_human_review_is_required": (
                    "Request-level governance or assurance requires human review. "
                    "The selected candidate has not been released."
                ),
                "review_focus": "Review the governance and precedence assessments.",
                "evidence_gaps_or_uncertainty": (
                    "Review the recorded restrictions before any operational use."
                ),
            }

        result = RAGResult(
            request_id=build_request_id(request.question),
            question=request.question,
            status=STATUS_COMPLETED,
            final_outcome=final_outcome,
            response=response,
            governance=governance_audit,
            assurance=assurance,
            evidence_summary=_build_evidence_summary(evidence_packet),
            execution_trace=execution_trace,
            failure=None,
        ).to_dict()
        # Preserve object identity across selection, assurance, and release.
        if generation_audit["selected_response_released"]:
            result["response"] = selected_response
        return result

    except Exception as exc:
        if isinstance(exc, AssuranceIntegrationError):
            preparation_stage = exc.stage
        failure_result = build_failed_closed_result(
            question=request.question,
            stage=preparation_stage,
            error=exc,
            execution_trace=execution_trace,
        )
        failure_result["governance"].update(governance_audit)
        failure_result["governance"]["application_release_ceiling"] = OUTCOME_ABSTAIN
        failure_result["governance"]["final_decision"] = ABSTAIN
        failure_result["governance"]["may_return_answer"] = False
        failure_result["governance"]["requires_human_review"] = False
        if "generation" in governance_audit:
            governance_audit["generation"]["selected_response_released"] = False
        failure_summary = exc.summary if isinstance(exc, AssuranceIntegrationError) else assurance
        if failure_summary:
            failure_result["assurance"].update(failure_summary)
            failure_result["assurance"].update(
                status="FAILED", final_assurance_decision="ABSTAIN",
                required_checks_complete=False, authority_increased=False,
            )
        return failure_result
