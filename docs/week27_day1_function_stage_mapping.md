# Week 27 Day 1 — Existing Function-to-Stage Mapping

## Purpose

Map the existing implementation to the ten canonical Week 27 application
stages. This is an implementation inventory and Day 2 composition boundary,
not an implementation of the application orchestrator.

Inspection baseline: branch `main`, HEAD
`b94f6d588d5052353ae0e52abc89fc04517e2b2c`.
The two supplied Week 27 design documents were already untracked at inspection.
They are preserved without changes. No Python files are changed by this mapping.

Read first:

- `docs/week27_day1_canonical_pipeline_decision.md`
- `docs/week27_day1_application_contract.md`

The current application-contract file ends after the minimum `question` input
example, inside an unclosed code fence. It does not yet specify complete
dependency, output, or failure schemas. This mapping records actual subsystem
contracts; it does not pretend the unfinished application contract defines them.

Classification:

- **A — Reusable runtime function:** a callable suitable for composition into
  the prototype request path, subject to its existing contract. This is not a
  claim of production deployment or clinical validation.
- **B — Benchmark/evaluation only:** dataset, expected-outcome, report, or
  collection orchestration. Keep outside a single application request.
- **C — Legacy/demo:** preserve for compatibility; excluded from the canonical path.
- **D — THIN WEEK 27 INTEGRATION REQUIRED:** application composition or contract
  adaptation has no complete existing implementation.

The protected rule throughout is:

> ASSURANCE MAY PRESERVE OR REDUCE AUTHORITY.
> ASSURANCE MUST NEVER INCREASE AUTHORITY.

Governance states remain `AUTO_ANSWER`, `REVIEW_REQUIRED`, and `ABSTAIN`.
Response types `ANSWER`, `REVIEW`, and `ABSTENTION`, assurance decisions
`PASS`, `REVIEW_REQUIRED`, and `ABSTAIN`, detector labels, and benchmark
`PASS`/`FAIL` are different contracts. They must not be interchanged implicitly.

## Canonical Runtime Map

Paths in this document are repository-relative. Stages describe responsibilities,
not ten independent calls: the evidence packet already composes stages 3–5,
and controlled execution already composes model input, prompt, and validation.

| Stage | Responsibility | Existing Module | Existing Function | Runtime Status |
|---|---|---|---|---|
| 1 | Input validation | `src/retrieval/query_scope.py`; `src/retrieval/hybrid_search.py` | `normalise_query()`; `validate_hybrid_query()` | A: subsystem validators; D: request/dependency validation and failure envelope |
| 2 | Governed retrieval | `src/retrieval/retrieval_orchestrator.py` | `orchestrate_retrieval()` | A; D only for application dependency/configuration wiring |
| 3 | Structured evidence | `src/evidence/evidence_from_retrieval.py` | `build_evidence_from_retrieval()` | A; already invoked conditionally by stage 4 |
| 4 | Evidence packet | `src/evidence/evidence_packet.py` | `build_evidence_packet()` | A; canonical aggregate and preferred external boundary |
| 5 | Pre-generation governance | `src/governance/retrieval_review_integration.py`; `src/governance/review_decision.py`; `src/evidence/evidence_precedence.py`; `src/generation/answer_contract.py` | `decide_retrieval_governance_outcome()`; `decide_review_outcome()`; `assess_evidence_precedence()`; `build_answer_contract()` | A; D: compose precedence restrictions with packet governance before generation |
| 6 | Answer context | `src/generation/answer_context.py` | `build_answer_context()` | A; D only to supply coherent packet/contract state |
| 7 | Controlled model execution | `src/generation/model_execution.py`; `src/generation/governed_prompt.py`; `src/generation/controlled_model_generation.py` | `execute_governed_model()`; `build_governed_prompt()`; `build_model_generation_input()`; `validate_model_generation_output()` | A; D: provider selection and application exception boundary |
| 8 | Deterministic fallback | `src/generation/grounded_answer.py`; `src/generation/generation_fallback.py` | `build_grounded_response()`; `resolve_generation_with_fallback()` | A; D: select and retain the response that will actually be assured |
| 9 | Post-generation assurance | `src/generation/claim_citation_linker.py`; `src/governance/citation_verification.py`; reusable `src/evaluation/` modules listed below | `build_claim_citation_links()`; `verify_claim_citation()`; `verify_answer_citations()`; assurance functions below | A components; D: response/claim/evidence adapters and request-level assurance composition |
| 10 | Final governance | `src/governance/review_decision.py`; `src/evaluation/week26_system_safety_invariants.py`; `src/evaluation/week26_fail_closed_assurance.py` | `decide_post_generation_outcome()`; `authority_not_increased()`; `audit_system_safety_invariants()`; `safe_audit_system_safety()` | A components; D: combine all applicable restrictions and enforce the final result |

## Stage 1 — Input Validation

**Existing module/functions:** `src/retrieval/query_scope.py`:
`normalise_query(query: str) -> str`; `assess_query_scope(query: str) -> dict`.
`normalise_query()` rejects non-string and blank questions and returns lowercase,
whitespace-normalised text. `assess_query_scope()` uses that validation internally
and returns scope, `allowed`, reason, and matching terms. Scope assessment belongs
to stage 2; do not run it again merely to populate an application trace.

`src/retrieval/hybrid_search.py::validate_hybrid_query(query, semantic_k,
keyword_k, final_k, rrf_k) -> None` supplies existing retrieval parameter
validation inside the retrieval path, raising for invalid input. Later stages also
validate their own mappings, identity, and permission flags. Private helpers
such as `_require_mapping()` are local implementation details, not a shared
application validation API.

**Runtime suitability:** A for the public subsystem functions; no existing
function validates the whole application request and runtime dependencies.

**Composition:** D — **THIN WEEK 27 INTEGRATION REQUIRED** for the request mapping,
required `question`, dependency/configuration checks, and consistent failure
result. Keep the original question for retrieval and audit; normalised text is
not a replacement for the user's original wording. Reuse downstream validators
rather than copying all their rules into a new validator.

**Safety constraint:** invalid input must not reach a provider or become an
automatic-answer permission. No application validation function is claimed to
exist yet.

## Stage 2 — Governed Retrieval

**Existing function:**
`src/retrieval/retrieval_orchestrator.py::orchestrate_retrieval()`.

**Inputs:** `query`, `chunks`, `embedded_chunks`, embedding `model`,
`embedding_model`; retrieval sizes `semantic_k`, `keyword_k`, `final_k`;
semantic/keyword/RRF thresholds, `rrf_k`, `max_related_chunks`, and `query_refiner`.

**Outputs:** a mapping with `results` and `audit`. The audit contains scope,
selected route, routing decision, route audit, final evidence sufficiency,
retrieval-call counts, and stop reason; in-scope retrieval also records the
initial evidence assessment. Out-of-scope output has empty results and
`final_evidence=None`.

**Existing call chain:** `assess_query_scope()` → `hybrid_search()` →
`assess_evidence_sufficiency()` → `diagnose_retrieval_route()` → at most one
enhancement via `expand_results_with_relationships()`,
`continue_bounded_agentic_retrieval()`, or
`continue_hybrid_search_evidence_rescue()`. Final sufficiency refers to the
original question. Initial hybrid retrieval explicitly uses `relevance_scorer=None`.

**Runtime suitability:** A. A thin application call is needed to supply prepared
corpus/model dependencies and collect the result; no second retrieval controller
is needed. Do not invoke every enhancement sequentially or alter ranking policy
as part of Day 2 composition.

**Safety constraint:** preserve scope, lifecycle eligibility, bounded call counts,
and final sufficiency. Retrieval does not decide permission to issue an answer.

## Stage 3 — Structured Evidence

**Existing function:**
`src/evidence/evidence_from_retrieval.py::build_evidence_from_retrieval(retrieval_output)`.

**Inputs:** stage 2 mapping; requires list `results`, dictionary `audit`, a
nonblank `selected_route`, and a dictionary `final_evidence`.

**Outputs:** `list[dict]` of structured evidence objects, constructed by
`src/evidence/evidence_object.py::build_evidence_objects()` with the selected
retrieval route. Insufficient final evidence returns `[]`. Malformed contracts
raise rather than silently creating evidence.

**Runtime suitability:** A. Reuse through stage 4; no independent conversion
wrapper is needed. The packet calls this function only when scope is allowed
and final evidence is sufficient. Calling it directly on the out-of-scope
retrieval result would raise because `final_evidence` is `None`.

**Safety constraint:** preserve `evidence_id`, `document_id`, `chunk_id`, `page`,
version, status, source fields, retrieval scores/role/route, and ingestion lineage.
Do not duplicate conversion outside the packet or manufacture usable evidence
for an insufficient query.

## Stage 4 — Evidence Packet

**Existing function:**
`src/evidence/evidence_packet.py::build_evidence_packet(question, retrieval_output)`.

**Inputs:** a nonblank question and the retrieval output mapping.

**Outputs:** `packet_id`, `question`, `retrieval`, `evidence_sufficiency`, grouped
`evidence`, `evidence_count`, `document_ids`, `provenance`, `provenance_summary`,
`precedence_assessment`, `missing_evidence`, `lifecycle_summary`, `governance`,
and `audit_summary`.

It already calls the stage 3 bridge when appropriate,
`src/evidence/provenance.py::build_provenance_records()`,
`assess_evidence_precedence()`, and `decide_retrieval_governance_outcome()`.

**Runtime suitability:** A; use this public aggregate once. D is limited to
application-level orchestration/error handling and consistent treatment of the
returned restrictions. Do not rebuild evidence, provenance, or governance in a
second packet format. The older generation formatter has a different packet API.

**Safety constraint:** precedence assessment and governance are separate packet
fields. Their coexistence does not prove the precedence restriction has already
been applied to generation permission.

## Stage 5 — Pre-Generation Governance

| Existing module/function | Inputs | Outputs |
|---|---|---|
| `src/governance/retrieval_review_integration.py::decide_retrieval_governance_outcome()` | `question`, `retrieval_output` | Governance decision/reason, review/generation flags, document IDs, retrieval route/stop reason |
| `src/governance/review_decision.py::decide_review_outcome()` | `question`, `scope_assessment`, `results` | `decision`, `reason`, `requires_human_review`, `may_generate_answer`, `document_ids` |
| `src/evidence/evidence_precedence.py::assess_evidence_precedence()` | `evidence_objects` | `SAFE_TO_COMBINE`, `BLOCK_COMBINATION`, or `REVIEW_BEFORE_COMBINATION`, with lifecycle and relationship details |
| `src/generation/answer_contract.py::build_answer_contract()` | `evidence_packet` | Packet-bound answer contract: governance, response type/sections, generation and review flags, citation/safety requirements |

**Runtime suitability:** A. The packet already invokes the retrieval-governance
bridge and precedence assessor. The bridge makes scope and final sufficiency
authoritative before delegating to `decide_review_outcome()` for lifecycle,
cross-document intent, similarity, and separation rules. Call the bridge through
the packet rather than bypassing it with `decide_review_outcome()` alone.

**Composition:** D — **THIN WEEK 27 INTEGRATION REQUIRED** to carry all applicable
precedence restrictions into a coherent pre-generation state before building
the answer contract. `build_answer_contract()` reads packet governance; it does
not itself combine `precedence_assessment` with that governance. Preserve the
original decisions in the audit and propagate any reduction consistently through
packet, contract, and context identity checks. Do not edit only one downstream
flag or silently treat `SAFE_TO_COMBINE` as permission to answer.

**Safety constraint:** insufficient evidence stays `ABSTAIN`; review cannot
become automatic answering because of a high retrieval score or a safe
combination label. Absence of an established conflict is not proof that no
conflict exists. Reuse the relationship/precedence controls without rewriting them.

## Stage 6 — Answer Context

**Existing functions:**
`src/generation/answer_contract.py::build_answer_contract(evidence_packet)` then
`src/generation/answer_context.py::build_answer_context(evidence_packet, answer_contract)`.

**Inputs:** the coherent governed packet and its answer contract.

**Outputs:** `context_version`, `packet_id`, `question`, `governance_decision`,
`response_type`, `allowed_sections`, `generation_permitted`,
`requires_human_review`, `precedence_decision`, `evidence_context`,
`citation_index`, `uncertainty_context`, and `safety_constraints`.

**Runtime suitability:** A. It checks shared packet/governance identity, requires
approved evidence for a non-abstaining response, and supplies no substantive
evidence or citations for abstention. D only for the application's sequencing
and dependency wiring; do not construct a parallel answer-context format.

**Safety constraint:** context carries precedence but does not independently
enforce its consequences. A nonblank question or populated citation index cannot
override the earlier generation decision.

## Stage 7 — Controlled Model Execution

| Existing module/function | Inputs | Outputs |
|---|---|---|
| `src/generation/controlled_model_generation.py::build_model_generation_input()` | `answer_context` | Validated/copied identity, governance, permissions, allowed sections, approved evidence, citation index, uncertainty and safety constraints |
| `src/generation/governed_prompt.py::build_governed_prompt()` | `answer_context` | Identity/governance fields, `prompt`, `model_input`, `prompt_status=READY` |
| `src/generation/model_execution.py::execute_governed_model()` | `answer_context`, `provider` implementing `ModelProvider` | Identity, provider/model names, `execution_status`, fallback/failure fields, `validated_output`, `raw_output` |
| `src/generation/controlled_model_generation.py::validate_model_generation_output()` | `model_input`, `model_output` | Validated identity/governance/response type, review flag, generation status, sections, citations, safety notes and `validation_status` |

**Runtime suitability:** A. Use `execute_governed_model()` as the aggregate:
it calls the prompt builder, which calls the input builder, then validates the
provider's structured result. Do not call all four functions again independently.
The provider protocol is `generate(prompt: str) -> Any` with `provider_name`
and `model_name` attributes.

**Composition:** D for provider dependency injection, allowed execution modes,
and the outer application exception boundary. Provider exceptions, non-dict
output, and output-validation exceptions become `FAILED`/`REJECTED` execution
records. Prompt construction and provider metadata validation happen before
those catches; they can still raise to the application.

**Safety constraint:** `ACCEPTED` means the model output passed its structural
contract, not citation or factual assurance. `REVIEW_REQUIRED` permits only a
non-authoritative review summary; `ABSTAIN` permits no substantive evidence or
citations in model input. Provider execution is not universally skipped merely
because `generation_permitted=False`; state-specific restrictions remain binding.

## Stage 8 — Deterministic Fallback

**Existing functions:**
`src/generation/grounded_answer.py::build_grounded_response(answer_contract, answer_context)`
and `src/generation/generation_fallback.py::resolve_generation_with_fallback(execution_result, deterministic_response)`.

**Inputs:** approved contract/context for deterministic construction; execution
record and matching deterministic response for fallback resolution.

**Outputs:** deterministic response with packet/governance/type, generation
status, review flag, sections, citations, and safety summary; resolver output
with `final_response_source` (`MODEL` or `DETERMINISTIC_FALLBACK`), `final_response`,
fallback reason/flag, provider/model details, and execution status.

**Runtime suitability:** A. The resolver selects accepted `validated_output`
or the supplied deterministic response and checks shared identity. It does not
construct the fallback itself. D for orchestrating construction, selection, and
the explicit deterministic-only mode if supported by the future application.
Do not invent a successful execution record to disguise an unexecuted provider.

**Safety constraint:** fallback is still subject to stages 9–10. Never assure
only the fallback and then issue different model text. Failed generation does
not grant additional authority, and the selected response formats are not
guaranteed interchangeable for claim extraction.

## Stage 9 — Assurance

**Runtime suitability:** the functions below are A candidates for request-level
composition, even though many live under `src/evaluation/`. Their module
location does not make them benchmark runners. They require explicit adapters
and applicability checks; none alone implements the complete application stage.

### Claim extraction, citation support, and high-risk checks

| Existing module/function | Inputs | Outputs / safety constraint |
|---|---|---|
| `src/generation/claim_citation_linker.py::build_claim_citation_links()` | `grounded_response`, `answer_context` | Identity, `claims`, citation IDs, linkage counts and unsupported claims; validates known IDs and shared state. Linkage `SUPPORTED` is not verified semantic support. |
| `src/evaluation/citation_assurance.py::build_citation_assurance()` | `claim_linkage`, `answer_context`; optional `required_citations_by_claim` | Source validation, nested `citation_completeness`, decision and safety summary; calls completeness audit itself. |
| `src/evaluation/citation_completeness.py::audit_claim_citation_completeness()` | Claim, `citation_index`; optional required IDs and `material` | Completeness status, attached/missing/invalid citations. Presence/completeness does not establish entailment. |
| `src/evaluation/citation_completeness.py::audit_answer_citation_completeness()` | Claims, citation index; optional required-citation mapping, non-substantive IDs and upstream governance | Answer decision, material counts and per-claim completeness. Prefer the integrated citation-assurance wrapper when its inputs are available. |
| `src/governance/citation_verification.py::verify_claim_citation()` | Claim containing `citation` identity; cited evidence or `None`; support/semantic-rescue options | Support `status`, reason, lexical/guard/rescue details as applicable. Identity and lifecycle checks precede high-risk guarding and any support acceptance. |
| `src/governance/citation_verification.py::verify_answer_citations()` | Claims in verifier format, evidence list, same threshold/rescue options | `decision`, `reason`, `claim_count`, `claim_results`; empty claims produce `ABSTAIN`. It calls the single-claim verifier. |
| `src/governance/high_risk_claim_guard.py::detect_high_risk_mismatch()` | Nonblank `claim_text`, `evidence_text` | `guard_triggered`, reasons and unsupported numbers/actors/actions. Already reused inside citation and groundedness checks; do not run a replacement guard. |
| `src/evaluation/multi_source_claim_verification.py::verify_multi_source_relationship_claim()` | Claim, citation index, `evidence_by_citation_id`, precedence assessment; explicit `relationship_type`, `required_citation_ids` | Support status plus relationship/source details. Requires at least two required citations, Active matching evidence, and established precedence/relationship; a pile of citations is not a relationship proof. |

### Groundedness, semantic, temporal, and adversarial checks

| Existing module/function | Inputs | Outputs / safety constraint |
|---|---|---|
| `src/evaluation/groundedness_audit.py::audit_claim_groundedness()` | Claim and evidence list; `material`, groundedness threshold | `GROUNDED`, `PARTIALLY_GROUNDED`, `UNGROUNDED`, or `NOT_APPLICABLE`, lexical support and high-risk details. |
| `src/evaluation/groundedness_audit.py::audit_answer_groundedness()` | Claims, `evidence_by_claim_id`; non-substantive IDs, upstream decision and threshold | Per-claim audit, counts and local decision; not a complete final governance reducer. |
| `src/evaluation/overstatement_audit.py::audit_claim_overstatement()` | Claim/evidence list; `material`, `minimum_material_overlap` | `PRESERVED`, `OVERSTATEMENT_DETECTED`, or `NOT_APPLICABLE`, overlap and overstatement types. |
| `src/evaluation/overstatement_audit.py::audit_answer_overstatement()` | Claims, evidence-by-claim mapping; non-substantive IDs and upstream decision | Per-claim results, overstatement count and local decision. |
| `src/evaluation/hallucination_resistance.py::audit_answer_hallucination_resistance()` | Claims, evidence-by-claim mapping; non-substantive IDs and required `upstream_governance_decision` | Combined groundedness/overstatement audits, risk flags and governance-preserving decision. Reuses both preceding answer auditors; avoid running them twice for the same purpose. |
| `src/evaluation/relationship_aware_groundedness.py::assess_source_support()` | `claim_text`, evidence item | `SourceSupportResult` with source identity, support, lifecycle validity and reason; conservative source-level helper, not a replacement citation verifier. |
| `src/evaluation/relationship_aware_groundedness.py::assess_relationship_aware_groundedness()` | Keyword-only claim ID/text, evidence list, explicit `relationship`; optional `material` | `groundedness_status`, source results, relationship/composition details and reason. Derive relationship from validated evidence, not benchmark labels or model assertions. |
| `src/evaluation/semantic_precision_audit.py::audit_semantic_precision()` | Keyword-only claim ID/text, evidence list, `existing_support_status` | `revised_support_status`, `support_reduced`, modal/role/immediacy flags. Can reduce or preserve existing support, never upgrade it. |
| `src/evaluation/version_temporal_assurance.py::assess_temporal_validity()` | Evidence; explicit `query_date` | Evidence temporal state and dates/reason. Requires a real request/runtime date, not a benchmark answer. |
| `src/evaluation/version_temporal_assurance.py::assess_version_relationship()` | `older`, `newer` evidence mappings | Version relationship and explanatory fields; version labels alone do not establish replacement authority. |
| `src/evaluation/version_temporal_assurance.py::assess_version_temporal_assurance()` | Keyword-only evidence list and `query_date` | `SAFE_FOR_CURRENT_USE`, `NOT_SAFE_FOR_CURRENT_USE`, or `REVIEW_REQUIRED`, temporal/version results and current/historical IDs. Calls the two preceding helpers. |
| `src/evaluation/evidence_prompt_injection.py::inspect_evidence_for_prompt_injection()` | One evidence mapping | Injection/control-override flags and detector label for that source. |
| `src/evaluation/evidence_prompt_injection.py::assess_evidence_prompt_injection()` | Evidence list | Aggregated flags, affected evidence IDs, detector label and reason; uses the per-item inspector. Empty evidence gives `NOT_APPLICABLE`, not approval. |
| `src/evaluation/abstention_safety.py::audit_abstention_safety()` | Flat abstention section mapping or `None` | Detector decision, `safe`, structure validity, missing/blank sections and leakage flags. Pass the response's `sections`, not its outer response envelope. `None` gives `safe=False`. |

### Required request-level adapters

D — **THIN WEEK 27 INTEGRATION REQUIRED** for the following boundaries:

1. **Assure the selected text.** `build_claim_citation_links()` expects the
   deterministic response shape: list-valued evidence explanations with
   `evidence_text` and attached citation fields. The model-output validator
   accepts a section mapping without enforcing this claim-item shape for every
   answer/review section. Model acceptance does not guarantee linker compatibility.
   Define a bounded adapter or reject/fall back when it cannot preserve the
   actual model claims and their sources. Never substitute evidence text for an
   unverified model claim merely to obtain a passing audit.
2. **Cover all material output.** The linker labels management summary and
   operational implication as `NON_SUBSTANTIVE` in its deterministic ANSWER path.
   That classification cannot be assumed safe for arbitrary model-written text.
   Ensure every material assertion in the selected response is audited; do not
   exclude a new operational recommendation because its section has a familiar name.
3. **Resolve approved citations.** Linkage uses `citation_ids`; the original
   citation verifier consumes a singular `citation` with document/chunk identity.
   Resolve IDs through the approved context index and evidence only. Preserve
   every citation in a multi-source claim; use the relationship verifier when
   applicable rather than dropping all but the first citation. Reject ambiguous
   duplicate source identities before lookup rather than accepting last-write wins.
4. **Supply support contracts from runtime evidence.** Construct
   `evidence_by_citation_id`, `evidence_by_claim_id`, required-citation sets,
   materiality and explicit relationship inputs. The benchmark cases currently
   supply some of these fields. Expected benchmark labels must not become runtime
   truth. If a necessary relationship/support contract cannot be established,
   retain uncertainty and reduce authority.
   Keep full evidence separate from the reduced model context: answer-context
   evidence omits `effective_date`, while the evidence object retains it.
   The evidence-object builder reconstructs canonical fields and does not carry
   arbitrary `superseded_date`, `replaces_document_id`, or
   `replaced_by_document_id` fields forward. Where available, join these trusted
   fields from retained retrieval/source records by validated identity for
   temporal/version assurance; do not invent them. The relationship-groundedness
   API also expects labels such as `EXPLICIT_CONFLICT` or
   `COMPLEMENTARY_EVIDENCE`, rather than raw governance `CONFLICT` or
   `COMPLEMENTS`; that translation needs evidence-backed, explicit mapping.
5. **Schedule evidence checks before exposure.** Evidence injection and temporal
   checks are listed here as assurance components, but their relevant signals
   should also restrict generation before unsafe evidence reaches a provider.
   A later final-response gate cannot undo that earlier exposure. Reuse the same
   assessments instead of repeatedly running them.
6. **Handle applicability and vocabulary explicitly.** `NOT_APPLICABLE`,
   `SAFE_FOR_CURRENT_USE`, precision labels and groundedness labels are not
   governance decisions. Record why a check is applicable/skipped and propagate
   risk into stage 10. Missing required checks, exceptions or malformed results
   cannot be silently treated as `PASS`.

These adapters are composition of existing controls, not new entailment,
retrieval, or high-risk detection algorithms. Semantic rescue has model/runtime
cost and configuration requirements; retain its guard ordering and make its
execution policy visible rather than silently loading a model as a side effect
of unrelated application validation.

## Stage 10 — Final Governance

| Existing module/function | Inputs | Outputs / actual behaviour |
|---|---|---|
| `src/governance/review_decision.py::decide_post_generation_outcome()` | `pre_generation_decision`, `citation_verification` mappings | `decision`, reason, review flag, `may_return_answer`, document IDs. Combines pre-generation and citation decisions only. |
| `src/evaluation/week26_system_safety_invariants.py::authority_level()` | Assurance decision string | Numeric order: `ABSTAIN=0`, `REVIEW_REQUIRED=1`, `PASS=2`; unknown labels raise. |
| `src/evaluation/week26_system_safety_invariants.py::authority_not_increased()` | Keyword-only `before`, `after` assurance decisions | Boolean comparison of existing authority levels. |
| `src/evaluation/week26_system_safety_invariants.py::audit_system_safety_invariants()` | Keyword-only `case_id`, `upstream_decision`, `final_decision`, `signals` | `INVARIANT_PASS`/`INVARIANT_FAIL`, original decisions/levels, checks and failed invariants. Audits a proposed decision; does not repair it. |
| `src/evaluation/week26_fail_closed_assurance.py::safe_audit_system_safety()` | Record with those four fields | Boundary status, `final_decision`, completion/authority flags, reason/error, underlying invariant result. Handled malformed inputs/evaluator failures return fail-closed `ABSTAIN`. |

**Runtime suitability:** A components, but D — **THIN WEEK 27 INTEGRATION
REQUIRED** for the final request-level authority decision and response assembly.
There is no complete public function that consumes every Week 25/26 assurance
result and issues the final application response.

Important limits visible in the code:

- `decide_post_generation_outcome()` preserves upstream `ABSTAIN` and returns
  upstream `REVIEW_REQUIRED` before inspecting the citation outcome. Thus an
  upstream review plus later abstaining signal does not itself become `ABSTAIN`.
  The application must still apply any stricter later restriction.
- The invariant auditor returns the supplied `final_decision` even when it
  reports `INVARIANT_FAIL`. The safe wrapper also retains that supplied decision
  for normally completed audits. `assurance_completed=True` and
  `boundary_status=NORMAL_ASSURANCE` are not permission to issue an answer.
- The safe wrapper validates the top-level record but does not establish that
  every required detector ran or that every signal is present and boolean.
  Some malformed decision values can also raise before its inner evaluator
  catch. The application still needs an outer failure boundary and validated
  signal completeness; an empty mapping is not evidence of completed assurance.

**Required composition:** preserve the pre-generation authority ceiling, combine
all applicable citation/groundedness/relationship/temporal/injection/abstention
restrictions, then audit the proposed result through the existing safe boundary.
Consume `underlying_result.status` and failed invariants; enforce `ABSTAIN` for
failed required assurance or integration failure. Never issue a candidate answer
just because a wrapper returned normally.

Translate `AUTO_ANSWER` to the assurance ceiling `PASS` explicitly when auditing,
and only map a successful final assurance result back within the original
governance ceiling. Keep `REVIEW_REQUIRED` and `ABSTAIN` unchanged or reduce
authority further. Reconcile the final displayed response and permission flags
with the final decision so suppressed advice is not still returned as an answer.
This does not require rewriting the existing invariant or governance algorithms.

## Legacy / Non-Canonical Paths

Classification C:

- `src/generation/demo_pipeline.py::run_demo()` uses
  `build_demo_evidence()` and `DemoLLMClient.generate()`. Evidence is hard-coded;
  the path uses the older generation formatter and answer QA rather than the
  canonical retrieval/packet/controlled-generation chain.
- `src/generation/answer_generator.py::generate_grounded_answer(question,
  evidence_packet, llm_client)` builds the older `build_grounded_prompt()`, calls
  `LLMClient.generate(system_prompt, user_prompt) -> str`, and validates a
  non-empty answer through `validate_generated_answer()`. Its result is
  `status`, `answer`, `citations`, `generation_used`. It is not the Week 24
  structured provider/output contract or the full Week 25/26 assurance path.
- `src/generation/evidence_formatter.py::build_evidence_packet()` is the older
  generation packet API. It must not be confused with
  `src/evidence/evidence_packet.py::build_evidence_packet()`.

Keep these files and their existing tests. Exclusion from the canonical path is
not authorization to remove them. `src/generation/grounded_answer.py` is a
different, reusable deterministic response builder, not this older string path.

## Week 25/26 Assurance Integration Boundary

Stage 9 lists the reusable content controls. Stage 10 lists the reusable authority
and fail-closed checks. Prefer their public aggregate functions where aggregates
already call the lower-level controls; preserve the lower-level audit results
without running equivalent checks twice.

Classification B — evaluation infrastructure, not per-question runtime calls:

| Existing module/function | Inputs / effects | Why excluded from runtime composition |
|---|---|---|
| `src/evaluation/run_week25_assurance_suite.py::run_assurance_suite()` | Loads/validates the Week 25 benchmark, executes Day 3/4 cases, compares results, writes JSON/Markdown reports | Measures known-case behaviour; includes expected-case alignment and dataset/report orchestration |
| `src/evaluation/run_week26_assurance_suite.py::run_week26_assurance_suite()` | Loads benchmark and stored baseline, runs dedicated benchmark controls, joins regression anchors, writes reports | A suite result is benchmark evidence, not validation of a new user's response |
| `src/evaluation/run_week26_operational_assurance_gate.py::run_week26_operational_assurance_gate()` | Runs adversarial, system-safety and failure-injection benchmarks; writes combined gate reports | A release/regression gate; does not accept one question/answer |
| Internal case adapters such as `src/evaluation/run_week25_benchmark_baseline.py::_run_case()` | Benchmark case and its expected/support metadata | Useful examples to inspect; not a production request contract to import blindly |
| `src/evaluation/validate_week25_benchmark.py::validate_benchmark()` and `src/evaluation/validate_week26_benchmark.py::validate_benchmark()` | Benchmark documents and their expected labels/schema | Validate evaluation datasets, not application requests |

`audit_case_collection()` in `week26_system_safety_invariants.py` and
`safe_audit_collection()` in `week26_fail_closed_assurance.py` are collection
utilities; a single question should normally use the corresponding single-record
functions. Their existence does not justify running a benchmark suite per request.

Preserve all benchmark runners, datasets, tests and Week 25/26 internals. Report
suite pass/fail separately from request-level support and authority decisions.
No suites or provider calls were run for this documentation task.

## Minimal New Week 27 Code Required

All items below are D — **THIN WEEK 27 INTEGRATION REQUIRED**. They describe
future responsibilities, not existing or newly implemented function names.

1. Request/dependency validation and one application failure/result envelope.
2. Sequential composition around the existing retrieval and packet aggregates;
   consistent pre-generation handling of precedence and other applicable risk.
3. Controlled provider/deterministic-mode selection and existing fallback wiring.
4. Bounded adapters for actual response claims, approved citations, materiality,
   multi-source support contracts, evidence relationships, and request date.
5. Request-level scheduling of existing assurance functions, explicit status and
   risk-signal mapping, and final authority reduction using the existing controls.
6. One audit trace recording original and reduced decisions, executed/skipped
   checks, failure reasons, retrieval route, source identity and generation source.

The missing complete application contract must be finished before claiming an
implementation conforms to it. Preserve that design file today. Do not introduce
another retriever, evidence schema, model validator, safety detector, benchmark
format, or general agent/tool framework merely to fill these composition gaps.

## Proposed Day 2 Build Boundary

The future application layer will need to:

1. Validate the request and supplied dependencies, retaining the original question.
2. Call `orchestrate_retrieval()` once.
3. Call the canonical evidence `build_evidence_packet()` once, allowing it to
   perform its existing evidence/provenance/precedence/governance calls.
4. Apply applicable evidence-safety and precedence restrictions before model
   exposure; keep packet, contract and context decisions coherent.
5. Call `build_answer_contract()` and `build_answer_context()`.
6. Construct `build_grounded_response()`; for an enabled provider mode call
   `execute_governed_model()` and `resolve_generation_with_fallback()`.
7. Adapt the selected response without losing its actual claims, then reuse
   `build_claim_citation_links()`, `build_citation_assurance()`, citation
   verification and the applicable assurance functions catalogued above.
8. Use `decide_post_generation_outcome()` within the wider final restriction
   composition; validate authority through `safe_audit_system_safety()` and
   inspect the underlying invariant result before issuing any response.
9. Return one final response/audit consistent with the final authority decision;
   fail closed on required-assurance or integration failure.

Future integration tests should cover automatic answer, review, abstention,
scope rejection, insufficient evidence, blocked precedence, incompatible model
claim shape, provider rejection/fallback, incomplete assurance, and invariant
failure without authority increase. Retain Week 25/26 regression gates as
separate checks. No Python orchestrator or tests are created on Day 1.
