"""Thin request adapters around the existing Week 25/26 assurance controls.

No benchmark runners, generated source metadata, or new support detectors.
Detailed claim/evidence text stays local; public check records contain no text.
"""

from copy import deepcopy
import json
import re

from src.generation.claim_citation_linker import build_claim_citation_links
from src.evaluation.citation_assurance import build_citation_assurance
from src.governance.citation_verification import verify_answer_citations
from src.evaluation.hallucination_resistance import audit_answer_hallucination_resistance
from src.evaluation.multi_source_claim_verification import (
    RELATIONSHIP_CLAIM_TERMS, verify_multi_source_relationship_claim,
)
from src.evaluation.relationship_aware_groundedness import assess_relationship_aware_groundedness
from src.evaluation.semantic_precision_audit import SUPPORT_ORDER, audit_semantic_precision
from src.evaluation.version_temporal_assurance import assess_version_temporal_assurance
from src.evaluation.evidence_prompt_injection import assess_evidence_prompt_injection
from src.evaluation.abstention_safety import audit_abstention_safety
from src.evaluation.week26_fail_closed_assurance import safe_audit_system_safety
from src.evaluation.week26_system_safety_invariants import authority_not_increased
from src.governance.review_decision import decide_post_generation_outcome


COMPONENTS = (
    "claim_linkage", "citation_assurance", "citation_verification",
    "hallucination_resistance", "semantic_precision", "multi_source",
    "temporal_version", "prompt_injection", "abstention_safety", "system_safety",
)
AUTHORITY = {"ABSTAIN": 0, "REVIEW_REQUIRED": 1, "PASS": 2}
GOVERNANCE_TO_ASSURANCE = {
    "AUTO_ANSWER": "PASS", "REVIEW_REQUIRED": "REVIEW_REQUIRED", "ABSTAIN": "ABSTAIN",
}
# Only the mature deterministic builder's exact fixed communication templates
# are non-material. An arbitrary model summary is always a material claim.
DETERMINISTIC_NOTICES = {
    "Approved evidence is available to answer the management question.",
    "Use the approved evidence above as the basis for the operational response.",
    "The upstream governance decision requires human review before an authoritative "
    "answer or operational recommendation is issued.",
}
CITATION_MARKER = re.compile(r"\[(E[1-9][0-9]*)\]")


class AssuranceIntegrationError(RuntimeError):
    """A safe failure stage with partial, text-free assurance records."""

    def __init__(self, stage, summary):
        super().__init__(f"{stage} did not complete safely.")
        self.stage = stage
        self.summary = summary


def _require(condition):
    if not condition:
        raise ValueError("Malformed or incomplete assurance contract.")


def _decision(result, choices=AUTHORITY):
    _require(isinstance(result, dict))
    value = result.get("decision")
    _require(isinstance(value, str) and value in choices)
    return value


def _rows(result, expected_ids, statuses, field="status"):
    rows = result.get("claim_results")
    _require(isinstance(rows, list) and type(result.get("claim_count")) is int
             and result["claim_count"] == len(expected_ids))
    _require([row.get("claim_id") for row in rows if isinstance(row, dict)] == expected_ids)
    _require(all(row.get(field) in statuses for row in rows))
    return rows


def _record(summary, name, stage, operation, validate, *, required=True):
    summary[name] = {"state": "FAILED", "required": required, "reason": "Check did not complete."}
    try:
        result = operation()
        validate(result)
        summary[name] = {"state": "EXECUTED", "required": required}
        if "decision" in result:
            summary[name]["decision"] = result["decision"]
        return result
    except Exception as exc:
        summary[name]["error_type"] = type(exc).__name__
        raise AssuranceIntegrationError(stage, summary) from exc


def _exclude(summary, name, reason, *, required=False):
    summary[name] = {"state": "NOT_APPLICABLE", "required": required, "reason": reason}


def _adapt_claims(selected, context, deterministic):
    """Build a separate canonical linkage view; never modify selected sections."""
    sections = selected["sections"]
    trusted_deterministic = selected == deterministic
    structured = isinstance(sections.get(
        "evidence_based_explanation" if context["response_type"] == "ANSWER" else "evidence_summary",
        [],
    ), list)
    if structured:
        linkage = build_claim_citation_links(selected, context)
        claims = deepcopy(linkage["claims"])
    else:
        # Existing linkage record contract, adapted for actual scalar model text.
        linkage = {key: selected[key] for key in ("packet_id", "governance_decision", "response_type")}
        claims = []

    covered = {claim["section"] for claim in claims}
    for section, value in sections.items():
        if section == "sources":
            _require(trusted_deterministic)
            continue
        if section in covered:
            continue
        if trusted_deterministic and section == "review_focus":
            _require(value == {"precedence_decision": context["precedence_decision"], "question": context["question"]})
            continue
        if trusted_deterministic and section in {"caveats", "evidence_gaps_or_uncertainty"}:
            _require(value == context["uncertainty_context"])
            if not any(value.values()):
                continue
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, str):
                text = item
                ids = CITATION_MARKER.findall(text)
            elif isinstance(item, dict):
                _require(set(item) <= {"evidence_text", "citation_id", "citation_ids", "document_id"})
                text = item.get("evidence_text")
                ids = item.get("citation_ids", [item["citation_id"]] if "citation_id" in item else [])
                _require(isinstance(ids, list))
                if "citation_id" in item:
                    _require(item["citation_id"] in ids)
            else:
                raise ValueError("Selected claim shape cannot be adapted.")
            _require(isinstance(text, str) and bool(text.strip()))
            _require(all(isinstance(cid, str) and cid for cid in ids))
            claims.append({
                "claim_id": f"C{len(claims) + 1}", "claim_text": text,
                "section": section, "citation_ids": list(dict.fromkeys(ids)),
                "support_status": "SUPPORTED" if ids else "UNSUPPORTED",
            })

    for claim in claims:
        text = claim["claim_text"]
        # Only citation syntax is removed from the audit view, not assertions.
        inline_ids = CITATION_MARKER.findall(text)
        claim["citation_ids"] = list(dict.fromkeys(claim["citation_ids"] + inline_ids))
        claim["claim_text"] = CITATION_MARKER.sub("", text).strip()
        _require(bool(claim["claim_text"]))
        if not trusted_deterministic:
            # Scalar/list-item model claims must be individually attributable.
            # Reject multi-sentence prose rather than guessing citation scope.
            _require(len(re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", claim["claim_text"])) == 1)
        non_material = trusted_deterministic and text in DETERMINISTIC_NOTICES
        claim["support_status"] = "NON_SUBSTANTIVE" if non_material else (
            "SUPPORTED" if claim["citation_ids"] else "UNSUPPORTED"
        )
    linkage["claims"] = claims
    return linkage


def _approved_sources(packet, context, retrieval_results):
    sources = {}
    for group in ("supporting", "relationship_evidence", "context"):
        for item in packet["evidence"].get(group, []):
            _require(isinstance(item, dict))
            key = item["evidence_id"]
            _require(key not in sources)
            sources[key] = item
    citations = {}
    identities = set()
    for citation in context["citation_index"]:
        cid = citation["citation_id"]
        identity = (citation["document_id"], citation["chunk_id"])
        _require(cid not in citations and identity not in identities)
        evidence = sources[citation["evidence_id"]]
        for field in ("evidence_id", "document_id", "chunk_id", "page", "source_file", "version", "status"):
            _require(evidence[field] == citation[field])
        approved = next(item for item in context["evidence_context"] if item["evidence_id"] == evidence["evidence_id"])
        _require(approved["evidence_text"] == evidence["evidence_text"])
        joined = deepcopy(evidence)
        _require("text" not in evidence or evidence["text"] == evidence["evidence_text"])
        # The mature citation verifier reads `text`; canonical evidence stores
        # `evidence_text`. Alias the same source content, never a model claim.
        joined["text"] = evidence["evidence_text"]
        raw = [r for r in retrieval_results if (r.get("document_id"), r.get("chunk_id")) == identity]
        _require(len(raw) <= 1)
        if raw:
            _require("text" not in raw[0] or raw[0]["text"] == evidence["evidence_text"])
            for field in ("version", "source_file", "page", "status", "effective_date"):
                if field in raw[0] and field in joined:
                    _require(raw[0][field] == joined[field])
            for field in ("superseded_date", "replaces_document_id", "replaced_by_document_id"):
                if field in raw[0]:
                    if field in joined:
                        _require(joined[field] == raw[0][field])
                    joined[field] = raw[0][field]
        citations[cid] = joined
        identities.add(identity)
    return citations


def assure_selected_response(selected_response, answer_context, evidence_packet, *,
                            deterministic_response, query_date=None, retrieval_results=()):
    """Assure this exact candidate using existing controls and explicit adapters."""
    summary = {name: {"state": "SKIPPED_WITH_REASON", "required": True,
                      "reason": "Earlier stages have not completed."} for name in COMPONENTS}
    snapshot = deepcopy(selected_response)
    decision = answer_context["governance_decision"]
    restrictions = [GOVERNANCE_TO_ASSURANCE[decision]]
    summary["response_identity"] = {key: selected_response[key] for key in (
        "packet_id", "governance_decision", "response_type",
    )}
    summary["authority_increased"] = False
    stage = "CLAIM_ADAPTATION"
    active = "claim_linkage"
    try:
        if decision == "ABSTAIN":
            for name in COMPONENTS[:-1]:
                _exclude(summary, name, "No substantive answer is permitted.")
            # Read-only alias view of the mature deterministic abstention shape.
            # Serialize all actual missing-evidence values so no advice is hidden.
            sections = dict(selected_response["sections"])
            if "missing_information" not in sections and "missing_evidence" in sections:
                sections["missing_information"] = json.dumps(sections["missing_evidence"], ensure_ascii=False)
            active, stage = "abstention_safety", "SAFETY_ASSURANCE"
            result = _record(summary, active, stage,
                lambda: audit_abstention_safety(sections),
                lambda r: (_decision(r, {"SAFE_ABSTENTION", "DIRECTIVE_LEAKAGE", "AUTHORITY_LEAKAGE",
                    "UNSUPPORTED_CERTAINTY", "ACTION_ASSUMPTION", "INVALID_ABSTENTION_STRUCTURE"}),
                    _require(type(r.get("safe")) is bool), _require(type(r.get("structure_valid")) is bool)))
            _require(result["safe"] and result["structure_valid"] and result["decision"] == "SAFE_ABSTENTION")
        else:
            linkage = _record(summary, active, stage,
                lambda: _adapt_claims(selected_response, answer_context, deterministic_response),
                lambda r: _require(isinstance(r.get("claims"), list)))
            claims = linkage["claims"]
            material = [c for c in claims if c["support_status"] != "NON_SUBSTANTIVE"]
            _require(bool(material))
            summary[active]["claim_count"] = len(claims)
            active, stage = "citation_assurance", "CITATION_ASSURANCE"
            sources = _approved_sources(evidence_packet, answer_context, retrieval_results)
            _require(set(selected_response["citations_used"]) <= set(sources))
            _require(all(set(c["citation_ids"]) <= set(selected_response["citations_used"]) for c in material))
            evidence_by_claim = {c["claim_id"]: [sources[cid] for cid in c["citation_ids"]] for c in material}
            completeness = _record(summary, active, stage,
                lambda: build_citation_assurance(linkage, answer_context),
                lambda r: (_decision(r), _require(r.get("packet_id") == answer_context["packet_id"]),
                    _rows(r["citation_completeness"], [c["claim_id"] for c in claims],
                          {"COMPLETE", "INCOMPLETE", "UNCITED", "INVALID_CITATION", "NOT_REQUIRED"})))
            restrictions.append(completeness["decision"])
            verifier_claims = []
            for claim in material:
                # Every cited source is checked; none is silently dropped.
                for cid in claim["citation_ids"] or [None]:
                    verifier_claims.append({"claim_id": f"{claim['claim_id']}::{cid}",
                        "claim_text": claim["claim_text"],
                        "citation": None if cid is None else {key: sources[cid][key] for key in ("document_id", "chunk_id")}})
            active = "citation_verification"
            verification = _record(summary, active, stage,
                lambda: verify_answer_citations(verifier_claims, list(sources.values()), semantic_rescue=False),
                lambda r: (_decision(r), _rows(r, [c["claim_id"] for c in verifier_claims], SUPPORT_ORDER)))
            restrictions.append(verification["decision"])
            summary[active]["semantic_rescue"] = "SKIPPED_WITH_REASON"
            summary[active]["reason"] = "Session 6 uses deterministic support checks; no implicit model loading."

            active, stage = "hallucination_resistance", "FAITHFULNESS_ASSURANCE"
            faithfulness = _record(summary, active, stage,
                lambda: audit_answer_hallucination_resistance(claims, evidence_by_claim,
                    non_substantive_claim_ids=[c["claim_id"] for c in claims if c not in material],
                    upstream_governance_decision=decision),
                lambda r: (_decision(r), _rows(r, [c["claim_id"] for c in claims],
                    {"CLEAR", "HALLUCINATION_RISK", "REVIEW_AUTHORITY_INCREASE", "ABSTENTION_VIOLATION", "NOT_APPLICABLE"}),
                    _require(type(r.get("abstention_violation_detected")) is bool),
                    _require(type(r.get("review_authority_increase_detected")) is bool)))
            restrictions.append(faithfulness["decision"])
            grounded_rows = faithfulness["groundedness_audit"]["claim_results"]
            _require(all(type(r.get("high_risk_guard_triggered")) is bool for r in grounded_rows))
            summary[active]["unsupported_high_risk_claim"] = any(r["high_risk_guard_triggered"] for r in grounded_rows)
            summary[active]["authority_increase_detected"] = faithfulness["review_authority_increase_detected"]
            active = "semantic_precision"
            precision = []
            role_risk = False
            for claim in material:
                evidence = evidence_by_claim[claim["claim_id"]]
                if not evidence:
                    continue  # Uncited claims already restrict citation assurance.
                statuses = [r["status"] for r in verification["claim_results"]
                            if r["claim_id"].startswith(claim["claim_id"] + "::")]
                existing = min(statuses, key=SUPPORT_ORDER.get)
                result = _record(summary, active, stage,
                    lambda c=claim, e=evidence, s=existing: audit_semantic_precision(
                        claim_id=c["claim_id"], claim_text=c["claim_text"], evidence_items=e, existing_support_status=s),
                    lambda r, c=claim, s=existing: (_require(r.get("claim_id") == c["claim_id"]),
                        _decision(r, {"CLEAR", "MODAL_STRENGTHENING", "IMMEDIACY_STRENGTHENING",
                            "ROLE_RESPONSIBILITY_UNSUPPORTED", "AUTHORITY_ATTRIBUTION_UNSUPPORTED", "MULTIPLE_PRECISION_RISKS"}),
                        _require(type(r.get("support_reduced")) is bool),
                        _require(r.get("revised_support_status") in SUPPORT_ORDER),
                        _require(SUPPORT_ORDER[r["revised_support_status"]] <= SUPPORT_ORDER[s])))
                precision.append(result["revised_support_status"])
                role_risk = role_risk or result.get("role_responsibility_unsupported", False) or result.get("authority_attribution_unsupported", False)
            if precision:
                summary[active]["support_statuses"] = precision
                summary[active]["role_hallucination_detected"] = bool(role_risk)
                if any(s != "SUPPORTED" for s in precision):
                    restrictions.append("REVIEW_REQUIRED")
            else:
                _exclude(summary, active, "No matching cited evidence for precision auditing.")

            active, stage = "multi_source", "SAFETY_ASSURANCE"
            multi_results = []
            for claim in material:
                evidence = evidence_by_claim[claim["claim_id"]]
                asserts_relationship = any(re.search(r"\b" + re.escape(term) + r"\b", claim["claim_text"], re.I)
                    for terms in RELATIONSHIP_CLAIM_TERMS.values() for term in terms)
                if len(evidence) < 2:
                    # Required relation/source metadata is missing. Do not let
                    # one matching quotation stand in for a governed source set.
                    _require(not asserts_relationship)
                    continue
                docs = {e["document_id"] for e in evidence}
                established = [check for check in evidence_packet["precedence_assessment"].get("relationship_checks", [])
                    if check.get("decision") == "RELATIONSHIP_SUPPORTED"
                    and docs <= set(check.get("document_ids", []))
                    and check.get("relationship_type") in RELATIONSHIP_CLAIM_TERMS
                    and any(re.search(r"\b" + re.escape(term) + r"\b", claim["claim_text"], re.I)
                            for term in RELATIONSHIP_CLAIM_TERMS[check["relationship_type"]])]
                if established:
                    relation = established[0]["relationship_type"]
                    checked = _record(summary, active, stage,
                        lambda: verify_multi_source_relationship_claim(claim, answer_context["citation_index"],
                            sources, evidence_packet["precedence_assessment"], relationship_type=relation,
                            required_citation_ids=claim["citation_ids"]),
                        lambda r: _require(r.get("status") in SUPPORT_ORDER))
                    if checked["status"] != "SUPPORTED":
                        restrictions.append("REVIEW_REQUIRED")
                relation_state = "SAME_DOCUMENT_CONTEXT" if len(docs) == 1 and len({e["version"] for e in evidence}) == 1 else None
                if established:
                    relation_state = "EXPLICIT_CONFLICT" if relation == "CONFLICT" else "VERSION_SUCCESSION"
                result = _record(summary, active, stage,
                    lambda: assess_relationship_aware_groundedness(claim_id=claim["claim_id"], claim_text=claim["claim_text"],
                        evidence_items=evidence, relationship=relation_state),
                    lambda r: (_require(r.get("groundedness_status") in {"GROUNDED_SINGLE_SOURCE", "GROUNDED_MULTI_SOURCE",
                        "PARTIALLY_GROUNDED", "UNGROUNDED", "CONFLICT_BLOCKED", "RELATIONSHIP_UNVERIFIED"}),
                        _require(type(r.get("lifecycle_valid")) is bool)))
                multi_results.append(result["groundedness_status"])
                if result["groundedness_status"] not in {"GROUNDED_SINGLE_SOURCE", "GROUNDED_MULTI_SOURCE"}:
                    restrictions.append("REVIEW_REQUIRED")
            if multi_results:
                summary[active]["statuses"] = multi_results
            else:
                _exclude(summary, active, "No material claim depends on multiple cited sources.")

            active = "temporal_version"
            if query_date is None or not all(e.get("effective_date") for e in sources.values()):
                summary[active] = {"state": "SKIPPED_WITH_REASON", "required": True,
                    "reason": "Trusted query_date and effective_date are required; none are invented."}
                restrictions.append("REVIEW_REQUIRED")
            else:
                temporal = _record(summary, active, stage,
                    lambda: assess_version_temporal_assurance(evidence_items=list(sources.values()), query_date=query_date),
                    lambda r: (_decision(r, {"SAFE_FOR_CURRENT_USE", "NOT_SAFE_FOR_CURRENT_USE", "REVIEW_REQUIRED"}),
                        _require(isinstance(r.get("temporal_results"), list))))
                if temporal["decision"] != "SAFE_FOR_CURRENT_USE":
                    restrictions.append("REVIEW_REQUIRED")
            active = "prompt_injection"
            injection = _record(summary, active, stage,
                lambda: assess_evidence_prompt_injection(list(sources.values())),
                lambda r: (_decision(r, {"NO_INJECTION_DETECTED", "INJECTION_DETECTED", "GOVERNANCE_OVERRIDE_ATTEMPT",
                    "CONFLICT_SUPPRESSION_ATTEMPT", "AUTHORITY_OVERRIDE_ATTEMPT", "RESPONSE_OVERRIDE_ATTEMPT"}),
                    _require(type(r.get("injection_detected")) is bool),
                    _require((r["decision"] == "NO_INJECTION_DETECTED") == (not r["injection_detected"]))))
            summary[active]["pre_exposure"] = False
            summary[active]["limitation"] = "Post-generation check; provider exposure is not injection-hardened by this result."
            if injection["injection_detected"]:
                restrictions.append("REVIEW_REQUIRED")
            _exclude(summary, "abstention_safety", "Selected response is not an abstention.")

        _require(selected_response == snapshot)
        summary["final_assurance_decision"] = min(restrictions, key=AUTHORITY.get)
        summary["status"] = "COMPLETED"
        summary["required_checks_complete"] = all(
            not summary[n]["required"] or summary[n]["state"] == "EXECUTED"
            for n in COMPONENTS if n != "system_safety"
        )
        return summary
    except AssuranceIntegrationError:
        raise
    except Exception as exc:
        summary[active] = {"state": "FAILED", "required": True, "error_type": type(exc).__name__}
        raise AssuranceIntegrationError(stage, summary) from exc


def finalize_request_governance(effective, assurance, *, request_id, fallback_used=False):
    """Intersect every restriction with upstream authority, then audit invariants."""
    try:
        _require(set(COMPONENTS) <= set(assurance))
        mandatory = ("abstention_safety",) if effective["decision"] == "ABSTAIN" else (
            "claim_linkage", "citation_assurance", "citation_verification",
            "hallucination_resistance", "temporal_version", "prompt_injection",
        )
        _require(all(assurance[n].get("required") is True for n in mandatory))
        for name in COMPONENTS[:-1]:
            record = assurance[name]
            _require(record.get("state") in {"EXECUTED", "NOT_APPLICABLE", "SKIPPED_WITH_REASON", "FAILED"})
            _require(type(record.get("required")) is bool)
            _require(record["state"] != "FAILED")
            if record["required"] and record["state"] != "EXECUTED":
                _require(name == "temporal_version" and record["state"] == "SKIPPED_WITH_REASON")
        citation = assurance["citation_verification"].get("decision", "ABSTAIN")
        post = decide_post_generation_outcome(effective, {"decision": citation})
        _require(post.get("decision") in GOVERNANCE_TO_ASSURANCE)
        proposed = min((GOVERNANCE_TO_ASSURANCE[effective["decision"]],
                        GOVERNANCE_TO_ASSURANCE[post["decision"]],
                        assurance["final_assurance_decision"]), key=AUTHORITY.get)
        if not assurance["required_checks_complete"] or fallback_used:
            proposed = min((proposed, "REVIEW_REQUIRED"), key=AUTHORITY.get)
        signals = {
            "prompt_injection_detected": assurance["prompt_injection"].get("decision") not in {None, "NO_INJECTION_DETECTED"},
            "conflict_blocked": "CONFLICT_BLOCKED" in assurance["multi_source"].get("statuses", []),
            "unsafe_temporal_evidence": assurance["temporal_version"].get("decision") == "NOT_SAFE_FOR_CURRENT_USE",
            "unsupported_high_risk_claim": assurance["hallucination_resistance"].get("unsupported_high_risk_claim", False),
            "authority_increase_detected": assurance["hallucination_resistance"].get("authority_increase_detected", False),
            "role_hallucination_detected": assurance["semantic_precision"].get("role_hallucination_detected", False),
            "abstention_violation_detected": False,
        }
        result = _record(assurance, "system_safety", "FINAL_GOVERNANCE",
            lambda: safe_audit_system_safety({"case_id": request_id,
                "upstream_decision": GOVERNANCE_TO_ASSURANCE[effective["decision"]],
                "final_decision": proposed, "signals": signals}),
            lambda r: (_require(r.get("assurance_completed") is True),
                _require(r.get("authority_increased") is False),
                _require(r.get("final_decision") == proposed),
                _require(r.get("underlying_result", {}).get("status") == "INVARIANT_PASS"),
                _require(r["underlying_result"].get("failed_invariants") == []),
                _require(set(r["underlying_result"].get("checks", {})) == {
                    "authority_not_increased", "unsafe_signal_not_passed", "upstream_abstain_preserved",
                    "review_not_upgraded_to_pass", "abstention_violation_preserves_abstain",
                    "prompt_injection_not_passed", "conflict_not_passed", "unsafe_temporal_evidence_not_passed",
                    "unsupported_high_risk_claim_not_passed",
                }),
                _require(all(v is True for v in r["underlying_result"]["checks"].values()))))
        _require(authority_not_increased(before=GOVERNANCE_TO_ASSURANCE[effective["decision"]], after=proposed))
        assurance["system_safety"]["invariant_status"] = result["underlying_result"]["status"]
        assurance["final_assurance_decision"] = proposed
        assurance["required_checks_complete"] = all(
            not assurance[n]["required"] or assurance[n]["state"] == "EXECUTED" for n in COMPONENTS
        )
        return {"decision": {"PASS": "AUTO_ANSWER", "REVIEW_REQUIRED": "REVIEW_REQUIRED", "ABSTAIN": "ABSTAIN"}[proposed],
            "requires_human_review": proposed == "REVIEW_REQUIRED", "may_return_answer": proposed == "PASS",
            "post_generation": post, "authority_increased": False}
    except AssuranceIntegrationError:
        raise
    except Exception as exc:
        raise AssuranceIntegrationError("FINAL_GOVERNANCE", assurance) from exc
