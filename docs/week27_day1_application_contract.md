# Week 27 Day 1 — Canonical Application Contract

## Purpose and authority

Theme: **End-to-End RAG Polish**.

This contract defines the future application layer using the authoritative
`week27_day1_canonical_pipeline_decision.md` and
`week27_day1_function_stage_mapping.md` in this directory.

The application schemas and policies below are design requirements, not claims
of an implemented orchestrator. Existing function names refer to the actual
implementations catalogued in the mapping. Missing composition remains
**THIN WEEK 27 INTEGRATION REQUIRED**; no new runtime functions are invented here.

The mapping's note about an incomplete application contract describes the state
before this repair. Its findings about existing functions remain authoritative.

> Compose mature components; do not duplicate them.

## 1. Application boundary

One operational-policy question enters and one structured governed result leaves.
The application coordinates prepared data, retrieval, evidence, governance,
controlled generation, assurance and final response selection. Its audit explains
every restriction and failure affecting answer authority.

Ingestion, cleaning, chunking, embedding preparation and storage setup remain
upstream responsibilities. Runtime consumes their prepared outputs. It does not
create another retrieval architecture, evidence schema, model-output validator,
or replacement for Weeks 25–26 assurance.

## 2. Canonical request

The minimum request is:

```json
{
  "question": "What does the approved escalation policy require?"
}
```

`question` must be a nonblank string. Preserve the original string in the result
and audit; any normalised working representation is separate. Retrieval and
packet construction must use a consistent question representation.

An optional `request_id` may be supplied as a nonblank string. Unknown request
fields are rejected rather than interpreted as configuration. Credentials,
provider objects, corpus data, expected benchmark labels, decisions and assurance
bypass flags are not question-request fields.

## 3. Runtime dependencies

Supply dependencies separately from the serialisable request:

| Dependency | Required contract |
|---|---|
| `chunks` | Prepared canonical chunk records with identity, source metadata, lifecycle and provenance |
| `embedded_chunks` | Prepared embeddings with the compatibility/freshness information expected by existing retrieval |
| `model` | Embedding-model dependency required by the existing retrieval implementation |
| `embedding_model` | Nonblank identifier consistent with the prepared embeddings |
| `provider` | Required in provider mode; existing `ModelProvider` contract: `provider_name`, `model_name`, `generate(prompt)` |
| `config` | Validated explicit application configuration defined below |

The embedding model and generation provider are distinct. Deterministic generation
does not remove retrieval's embedding dependencies. Retain full trusted source
and retrieval metadata for assurance; reduced model context is not its substitute.

## 4. Conceptual run_rag_pipeline interface

This is a future design interface only. It is not an existing or newly implemented
function:

```python
def run_rag_pipeline(
    request: dict,
    *,
    chunks: list[dict],
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    config: dict,
    provider=None,
) -> dict:
    ...
```

Its implementation will be a thin composition and exception boundary. Internal
adapters required by the mapping remain integration work; this document does not
pretend they already exist or assign invented existing-function names to them.

## 5. Ten canonical execution stages

| Stage | Responsibility | Existing functions / composition boundary |
|---|---|---|
| 1 | Input validation | `normalise_query()` and existing subsystem validators; request/dependency wrapper required |
| 2 | Governed retrieval | `orchestrate_retrieval()` |
| 3 | Structured evidence | `build_evidence_from_retrieval()` through the canonical packet |
| 4 | Evidence Packet | `src/evidence/evidence_packet.py::build_evidence_packet()` |
| 5 | Pre-generation governance | Packet's `decide_retrieval_governance_outcome()` and `assess_evidence_precedence()`; restriction composition required |
| 6 | Answer context | `build_answer_contract()` then `build_answer_context()` |
| 7 | Controlled model execution | `execute_governed_model()` in provider mode |
| 8 | Deterministic response/fallback | `build_grounded_response()` and, after provider execution, `resolve_generation_with_fallback()` |
| 9 | Post-generation assurance | Existing claim, citation, faithfulness and safety functions; request adapters/composition required |
| 10 | Final governance | `decide_post_generation_outcome()` plus all applicable restrictions and Week 26 authority/invariant checks |

These are logical stages, not ten independent calls. The packet composes stages
3–5; controlled execution composes input/prompt construction and model-output
validation. Do not duplicate internal calls to create separate trace events.
Evidence-safety checks belong to assurance but must execute before provider
exposure, as described below.

## 6. Input validation behaviour

Validate the request mapping, question, optional request ID, dependencies, mode,
and configuration before expensive execution. Reuse
`src/retrieval/query_scope.py::normalise_query()` for its string/blank-input rules
while preserving the original question.

`src/retrieval/hybrid_search.py::validate_hybrid_query()` already validates query
and positive integer retrieval sizes/RRF constant. Other existing validators
retain their own rules; do not copy or weaken them in an application validator.

Malformed requests/configuration produce the fail-closed result defined below
without a provider call. Scope rejection is a valid governed abstention, distinct
from malformed input or an execution exception.

## 7. Governed retrieval

Call `src/retrieval/retrieval_orchestrator.py::orchestrate_retrieval()` once with
the question, prepared corpus/embeddings, embedding dependencies and configuration.
Preserve scope assessment, initial hybrid retrieval, sufficiency, deterministic
routing, at most one bounded enhancement, and final assessment against the
original question. Do not chain enhancement routes in the application.

Consume `results` and `audit` together. An out-of-scope result has empty results
and `final_evidence=None`; do not manufacture evidence for it. Existing initial
hybrid retrieval explicitly passes `relevance_scorer=None`. This contract does not
claim that an application reranker option already exists or is enabled.

## 8. Structured evidence behaviour

`src/evidence/evidence_from_retrieval.py::build_evidence_from_retrieval()` converts
final sufficient results into canonical evidence objects while preserving route.
Insufficient evidence produces no structured evidence; malformed contracts raise.

Use the bridge through the packet's scope/sufficiency guards. Calling it directly
on out-of-scope output would fail because `final_evidence` is not a dictionary.
Do not separately reconstruct objects or create competing identities.

Preserve `EVIDENCE::<chunk_id>`, document/chunk/page identity, source fields,
version, lifecycle, extraction status and ingestion lineage. Do not invent source
metadata, effective dates, replacement relationships or citation sources.

## 9. Canonical Evidence Packet

Use `src/evidence/evidence_packet.py::build_evidence_packet(question, retrieval_output)`.
It assembles packet identity, retrieval metadata, sufficiency, grouped evidence,
provenance, lifecycle, precedence, missing evidence, governance and audit details.
It already invokes conversion, provenance, precedence and retrieval-governance
functions. Preserve their outputs for downstream composition.

The older `src/generation/evidence_formatter.py::build_evidence_packet()` is a
different API and is not this canonical boundary.

## 10. Pre-generation governance

The packet invokes
`src/governance/retrieval_review_integration.py::decide_retrieval_governance_outcome()`.
That bridge honours scope/final sufficiency before delegating to
`src/governance/review_decision.py::decide_review_outcome()`.

`src/evidence/evidence_precedence.py::assess_evidence_precedence()` separately
provides `SAFE_TO_COMBINE`, `BLOCK_COMBINATION` or `REVIEW_BEFORE_COMBINATION`.
Packet construction does not automatically combine that field with generation
permission. Thin composition must enforce blocking/review restrictions before
generation. A safe-combination label is not permission to answer or proof of an
undocumented relationship.

Retain original assessments and reduced decisions separately in the audit.
Derive coherent working packet/contract/context copies; do not change only one
permission flag or lose original decisions. Insufficiency remains `ABSTAIN`;
review cannot become automatic answering. Other restrictions may reduce authority
further.

## 11. Answer contract and answer context

Call `src/generation/answer_contract.py::build_answer_contract(evidence_packet)`
then `src/generation/answer_context.py::build_answer_context(evidence_packet, answer_contract)`.

Preserve shared packet identity, governance, response type, allowed sections,
generation/review flags, evidence context, citation index, uncertainty, precedence
and safety constraints. Non-abstaining contexts require approved evidence;
abstaining contexts provide no substantive evidence or citations to a model.

Do not create another answer-context schema. Carrying precedence in context does
not itself enforce the restriction: effective governance must already reflect it.

## 12. Controlled model execution

In provider mode, use
`src/generation/model_execution.py::execute_governed_model(answer_context, provider)`.
It reuses existing `build_governed_prompt()`, `build_model_generation_input()` and
`validate_model_generation_output()`; do not introduce another output validator.

Retain `ACCEPTED`, `REJECTED` or `FAILED`, provider/model identity, validated output
and failure details. Acceptance establishes structural validity, not factual
support or permission to issue the answer.

Provider/output errors handled internally become structured execution records.
Prompt construction and provider metadata checks can still raise outside those
catches. The application must provide an outer exception boundary. Raw prompts
and rejected provider output are not public response fields.

## 13. Explicit provider/deterministic execution modes

`config.generation.mode` has two application values:

| Mode | Behaviour |
|---|---|
| `DETERMINISTIC` | Use the governed deterministic response; never call the generation provider; record provider execution as `SKIPPED_WITH_REASON` |
| `PROVIDER` | Require an explicit provider and pre-exposure safety approval; execute the existing controlled model path when governance/mode policy permit |

Default to `DETERMINISTIC`. Live generation requires explicit startup configuration.
Do not silently switch modes because a dependency is missing. Semantic citation
rescue is a separately configured model operation; deterministic generation alone
does not imply that rescue is enabled or disabled.

For `REVIEW_REQUIRED`, a provider may produce only a non-authoritative review
summary, and only with explicit `allow_review_summary=True`. Otherwise select a
deterministic review response and explain the provider skip. A false generation
permission never permits authoritative instructions.

For `ABSTAIN`, application policy skips the provider and uses deterministic
abstention. The existing execution function does not itself universally skip
provider calls on a false generation flag; this is application composition policy.

## 14. Deterministic generation and fallback

`src/generation/grounded_answer.py::build_grounded_response(answer_contract, answer_context)`
builds the existing deterministic answer/review/abstention response.

After provider execution, use
`src/generation/generation_fallback.py::resolve_generation_with_fallback(execution_result, deterministic_response)`.
It selects accepted validated model output or the supplied deterministic response
and checks matching identity/governance/type. It neither constructs nor assures
the fallback itself.

Preserve returned source `MODEL` or `DETERMINISTIC_FALLBACK`. Deliberate
deterministic mode records application source `DETERMINISTIC` without fabricating
a model execution record merely to call the resolver.

Provider failure/rejection remains visible in the failure record and trace.
Application policy allows only an assured restricted review fallback or abstention
after that failure, never silent recovery to `ANSWER`. The resolver alone does
not impose this restriction. Rebuild/reduce any fallback created under an earlier
ceiling coherently, then assure its final form before returning it.

## 15. Week 25/26 request-level assurance boundary

Reuse the public controls identified in the function-stage mapping:

| Responsibility | Existing functions |
|---|---|
| Claim/citation linkage | `build_claim_citation_links()` |
| Citation source/completeness | `build_citation_assurance()` and its underlying `audit_answer_citation_completeness()` |
| Citation support | `verify_claim_citation()` / `verify_answer_citations()` |
| High-risk mismatch | `detect_high_risk_mismatch()`, already called within relevant support checks |
| Multi-source relationships | `verify_multi_source_relationship_claim()` |
| Groundedness/overstatement | `audit_answer_hallucination_resistance()`, which reuses `audit_answer_groundedness()` and `audit_answer_overstatement()` |
| Relationship-aware support | `assess_relationship_aware_groundedness()` |
| Semantic precision | `audit_semantic_precision()` |
| Temporal/version safety | `assess_version_temporal_assurance()` |
| Evidence injection | `assess_evidence_prompt_injection()` |
| Abstention text | `audit_abstention_safety()` |
| Authority/invariants | `authority_not_increased()`, `audit_system_safety_invariants()`, `safe_audit_system_safety()` |

Use the actual module/signature contracts in the mapping. Reuse aggregate
sub-results rather than rerunning their underlying checks. Detector labels are
not governance decisions.

Do not call `run_assurance_suite()`, `run_week26_assurance_suite()` or
`run_week26_operational_assurance_gate()` for one application question. These
load benchmarks/baselines, compare expected outcomes and write reports. A suite
pass does not validate a new answer; benchmark labels cannot supply runtime truth.

## 16. Assurance applicability states

Each configured check has an application execution/applicability state separate
from its detector result:

| State | Meaning | Authority consequence |
|---|---|---|
| `EXECUTED` | Applicable check completed with a usable structured result | Interpret the actual result; completion is not permission |
| `NOT_APPLICABLE` | Preconditions are demonstrably absent | Record reason/evidence for exclusion; never treat as `PASS` |
| `SKIPPED_WITH_REASON` | Policy skip or blocked by an earlier failure | Record reason; cannot satisfy an applicable required check |
| `FAILED` | Exception, unavailable dependency, malformed output or inability to complete | Required-check failure fails closed to `ABSTAIN` |

A completed detector finding unsupported content is `EXECUTED` with an adverse
result. Missing evidence for a material claim is not grounds to make citation
assurance inapplicable. An empty claim set cannot establish a passing answer.

Requiredness follows the versioned policy and actual response/evidence. A caller
cannot disable required checks to obtain an answer. Optional skips provide no
positive support. Stages blocked after failure remain visible in the trace.

## 17. Actual selected-response claim assurance

The response actually returned must be the response actually assured. Associate
assurance with response revision/content identity and source so one candidate's
results cannot be attached to another.

The existing linker expects deterministic structured claim items. Accepted model
sections do not necessarily have that shape. Thin adaptation must preserve actual
selected text, claim boundaries and attached citations or reject the incompatible
response under the explicit fallback policy. Never replace model claims with
source quotations merely to obtain a passing audit.

Audit all material assertions, including summaries, implications and operational
recommendations. The linker's deterministic `NON_SUBSTANTIVE` treatment of some
sections must not exempt arbitrary model-written content.

Resolve `citation_ids` through the approved index. Adapt the original verifier's
singular document/chunk `citation` contract without dropping sources from
multi-source claims. Required citation sets and relationships must derive from
trusted runtime evidence, not model declarations or benchmark expected labels.
Reject ambiguous duplicate source identities before lookup.

Assure the selected deterministic fallback too. If final restrictions replace
response text, assure that replacement under its reduced coherent contract.
Allow only one reduced replacement attempt; inability to assure it safely yields
`response=null` and `ABSTAIN`, without extra retrieval/provider retries.

## 18. Evidence safety before provider exposure

Run applicable evidence-injection and temporal/version checks and enforce
lifecycle/precedence restrictions before unsafe evidence reaches a provider.
Retain and reuse their results in request-level assurance. A later issue gate
cannot undo provider exposure.

Detected injection blocks provider exposure for that evidence. If a safe evidence
set cannot be established within existing contracts, abstain; do not silently
remove sources while retaining the original sufficiency approval.

Use full trusted evidence for date/version checks. Model-context evidence omits
`effective_date`; canonical evidence objects do not automatically retain arbitrary
supersession/replacement fields. Join available metadata only by validated source
identity. Missing metadata remains unknown and restricts authority; do not invent
dates or document relationships. Use the explicit resolved `query_date`.

Translate relationship vocabularies explicitly using established evidence.
`CONFLICT` / `COMPLEMENTS` are not automatically interchangeable with the
relationship-groundedness API's `EXPLICIT_CONFLICT` / `COMPLEMENTARY_EVIDENCE`.

## 19. Final governance and authority rule

> Assurance may preserve or reduce authority.
> Assurance must never increase authority.

Map the governance ceiling explicitly into assurance vocabulary:

| Governance ceiling | Assurance ceiling |
|---|---|
| `AUTO_ANSWER` | `PASS` |
| `REVIEW_REQUIRED` | `REVIEW_REQUIRED` |
| `ABSTAIN` | `ABSTAIN` |

The existing authority order is `ABSTAIN < REVIEW_REQUIRED < PASS`.
A final assurance `PASS` can return to automatic-answer permission only within
an upstream `AUTO_ANSWER` ceiling after every required applicable control succeeds.

Reuse `decide_post_generation_outcome()` for its pre-generation/citation gate,
then apply all stricter restrictions. It does not combine every assurance layer
and can preserve upstream review before considering later citation abstention;
application composition must still honour stricter later restrictions.

Validate complete, typed risk signals and decision strings, then audit the
proposed result through `safe_audit_system_safety()`. Inspect the underlying
invariant status and failed checks, not just completion or normal boundary
status. The existing auditor/wrapper can retain the supplied decision even while
reporting invariant failure; the application must enforce abstention for failed
required invariants. The wrapper also does not prove that all detectors ran.

Resolve restrictions to the lowest supported authority. Unknown required results,
failed required assurance and integration errors fail closed. Keep an outer
exception boundary around the existing wrappers; normal return alone cannot
grant automatic-answer permission.

## 20. Final application outcomes

| `final_outcome` | Required meaning |
|---|---|
| `ANSWER` | Final governance is `AUTO_ANSWER` and all required applicable assurance permits issue |
| `REVIEW_REQUIRED` | Human review is required; return only an assured non-authoritative review/evidence summary |
| `ABSTAIN` | No substantive answer may be issued; return safe abstention or no response payload |

Review or abstention must never retain hidden authoritative advice in sections,
caveats, source excerpts framed as instructions, or rejected model attachments.
Do not relabel an unsafe answer and return its text. Public summaries and traces
must not leak content suppressed from the response.

## 21. Canonical top-level result

Every result includes these keys, including early failures:

```text
{
  request_id: nonblank string,
  question: original string or null for invalid non-string input,
  status: "COMPLETED" | "FAILED",
  final_outcome: "ANSWER" | "REVIEW_REQUIRED" | "ABSTAIN",
  response: selected assured structured response | null,
  governance: governance audit mapping,
  assurance: assurance result mapping,
  evidence_summary: evidence summary mapping,
  execution_trace: ordered trace records,
  failure: failure mapping | null
}
```

`status` describes application execution, not answer permission. Normal scope
rejection/insufficiency can be `COMPLETED` with `ABSTAIN`. A safely handled provider
failure can be `COMPLETED` with an assured restricted fallback and a non-null
failure record. Required assurance/integration failure is `FAILED` with `ABSTAIN`.
No failed result may have outcome `ANSWER`.

## 22. Request identity

Generate a unique invocation `request_id` when none is supplied. Propagate it
through trace, governance, assurance and failure records. A caller-supplied ID is
correlation information, not authorization or an idempotency guarantee. For an
invalid supplied ID, generate an internal correlation ID for the failure result.

Keep invocation identity separate from the existing question-derived `packet_id`,
source/evidence IDs and citation IDs. Identical questions can share packet identity
while representing separate invocations. Response revision/content identity
distinguishes selected candidates within a request.

## 23. Response contract

`response` preserves the selected existing structured contract: `packet_id`,
`governance_decision`, `response_type`, `requires_human_review`, `sections`,
`citations_used`, and source-specific generation/validation fields. Model and
deterministic generation-status fields remain distinct; do not forge either.
Claim adapters provide access to these formats without replacing model validation.

| Governance | Existing response type |
|---|---|
| `AUTO_ANSWER` | `ANSWER` |
| `REVIEW_REQUIRED` | `REVIEW` |
| `ABSTAIN` | `ABSTENTION` |

Follow existing answer/model contracts for allowed sections and citations.
Abstention contains no substantive evidence or citations and uses
`unable_to_answer_safely`, `reason`, `missing_information` and
`what_is_needed_to_continue`. Pass the flat abstention `sections` mapping to
`audit_abstention_safety()`.

Reduced final text requires coherent governance/type/review flags and fresh
applicable assurance. If no safe payload can be constructed or assured, use
`response=null`; failure information explains the abstention without returning
rejected content. An answer or review summary requires a non-null assured payload.

## 24. Governance audit contract

`governance` contains:

- Request ID, packet ID when available, and resolved policy/configuration identity.
- Original packet governance and precedence assessments.
- Effective pre-generation decision and explicit restriction reasons.
- Citation/post-generation result and all other applicable authority restrictions.
- Proposed/enforced final decisions, assurance-vocabulary mappings, authority
  levels and invariant results.
- Final `requires_human_review` and `may_return_answer` consistent with the outcome.

Retain original and reduced assessments separately. Do not overwrite historical
approvals or confuse original approval with final issue permission.

## 25. Assurance result contract

`assurance` contains request/packet identity, assessed response source/revision/
content identity, policy identity, required-check coverage, check records, risk
signals and aggregate authority restriction.

Each check record contains its stable check name; actual module/function when
executed; `required`; applicability/execution `state`; exclusion/skip reason;
claim/evidence/response references; original detector result; explicit authority
interpretation; and safe completion/failure details.

Retain aggregate sub-results without rerunning equivalent checks. Required-check
coverage must be complete before `ANSWER`. `NOT_APPLICABLE` and
`SKIPPED_WITH_REASON` never count as successful detector results. Aggregate
assurance `PASS`, when used, remains subject to the upstream authority ceiling
and is distinct from benchmark-suite success.

## 26. Evidence summary contract

`evidence_summary` is a view of the existing packet, not a new evidence schema.
Include packet identity, retrieval route, scope/sufficiency, evidence count,
document/evidence/chunk IDs, provenance/citation references, lifecycle, precedence
and missing-evidence summaries.

Use canonical `document_id`, `chunk_id`, `page`, `source_file`, `version`, `status`
and dates where available. Preserve trusted metadata internally for assurance;
unavailable values remain unknown/null. Before packet construction, use empty
references/counts and explicit unavailability reasons. Public summaries must not
expose unsafe excerpts or hidden advice after review/abstention.

## 27. Execution trace

`execution_trace` is an ordered event list containing request identity, stage
number/name, actual callable where applicable, execution state, reason,
input/output references, decision changes and response revision. Include mode,
provider/model identifiers, generation source, fallback, retrieval route/stop
reason and effective configuration without secrets.

Use UTC timestamps or elapsed durations consistently when recorded. Mark stages
not reached as `SKIPPED_WITH_REASON`. Trace composed stages without invoking
functions twice. Exclude raw prompts, rejected output, unsafe evidence and secrets
from the public trace; internal audit retention is a separate deployment concern.

## 28. Fail-closed failure contract

`failure` is null without execution failures. Otherwise include request ID,
stable error `code`, failing `stage`, safe `message`, relevant check/source
references, and explicit `recovery_action`. Capture additional relevant failures
in details rather than silently losing later required-check failures.

Recovery actions identify restricted review fallback or abstention, not restored
answer authority. Malformed requests/configuration, broken retrieval/packet
contracts, unusable required claim adaptation, required-check failure and failed
invariants must be handled explicitly. If a required operation cannot complete
safely, return `FAILED`, `ABSTAIN`, no unsafe response and a failure/trace record.

Missing metadata found by a successfully executed assessment is a visible adverse
finding, never approval. An exception during that assessment is execution failure.
The outer boundary also handles errors raised before existing internal catches.
Neutral failure information is permitted when `response=null`.

## 29. No silent recovery to ANSWER

Caught exceptions, fallback selection, unavailable models, empty claims, skipped
checks, unknown labels and normal wrapper returns cannot restore `ANSWER`.
Provider failure/rejection restricts this request to review or abstention.
Required assurance or integration failure forces abstention. Record every
recovery/reduction and assure the actual final payload.

Deliberate deterministic mode can produce `ANSWER` only after the same governed
retrieval, evidence, applicable assurance and final authority checks. It is not
a disguised provider-failure fallback or a bypass around safety controls.

## 30. Explicit configuration contract

Configuration is a separate validated mapping with recorded contract/policy
version. Resolve defaults once at request start and record effective values.
Reject unknown keys and invalid types/ranges before provider use.

| Group | Fields and policy |
|---|---|
| Retrieval | Existing `semantic_k`, `keyword_k`, `final_k`, `rrf_k`, `semantic_min_similarity`, `keyword_min_score`, `min_rrf_score`, `max_related_chunks`; reuse existing defaults/validators and record resolved values |
| Generation | `mode=DETERMINISTIC` by default; explicit `PROVIDER`; `allow_review_summary=False` by default; failure policy fixed to restricted review fallback or abstention |
| Citation verification | Existing `support_threshold`, `semantic_rescue`, `semantic_rescue_threshold`; preserve threshold defaults and explicitly resolve rescue availability/cost policy |
| Evidence date | Resolved `query_date` in `YYYY-MM-DD`; default to the request's current UTC date from the application clock, recorded in the trace |
| Assurance | Versioned applicability/required-check policy, optional-check configuration and explicit detector-to-authority mappings; required checks cannot be disabled to obtain an answer |
| Execution/audit | Correlation policy, configuration identity and safe trace detail; no secret values |

Pass only supported arguments into existing functions. Do not pretend they accept
new reranker/retry/timeout options. Required dependency availability must agree
with resolved configuration; unavailability fails closed.

Semantic rescue follows citation identity, lifecycle and deterministic high-risk
guards. Disabling rescue does not make unresolved paraphrases supported. Secret
values remain in provider setup, never request, result or trace.

## 31. Application non-goals

This contract does not implement the orchestrator, a second retrieval controller,
evidence schema, model-output validator or assurance framework. It does not
replace Weeks 25–26, use benchmark expected labels as truth, invent metadata,
or bypass lifecycle, provenance, precedence, sufficiency or claim verification.

Preserve legacy `demo_pipeline.py`, `answer_generator.py` and their tests while
keeping them outside the canonical runtime. New ingestion/embedding architectures,
databases, autonomous tool agents, external services and deployment infrastructure
are outside this Day 1 repair.

## 32. Future CLI / FastAPI / Azure compatibility

The same future composition boundary should support a CLI, FastAPI adapter,
notebook or Azure-hosted service. Adapters supply dependencies/configuration and
translate transport errors while preserving governance semantics.

Return serialisable results without model objects or secrets. Keep process exits,
console formatting, HTTP handling, environment loading and deployment setup
outside core composition. Providers remain injected through the existing protocol.
This is a compatibility direction, not a claim of implemented transports or Azure
deployment.

## 33. Final Day 1 architecture decision

Adopt one thin application composition around the existing architecture:

```text
Request validation
  → existing retrieval orchestrator
  → canonical structured Evidence Packet
  → effective pre-generation governance and evidence-safety gates
  → existing answer contract/context
  → explicit controlled-provider or deterministic execution
  → existing deterministic fallback where required
  → assurance of the actual selected response
  → final authority restriction and Week 26 invariant enforcement
  → one structured governed result
```

Implement only the documented thin integration gaps when separately requested.
Preserve existing subsystem contracts and Weeks 25–26 assurance. Final outcomes
remain `ANSWER`, `REVIEW_REQUIRED` and `ABSTAIN`; review/abstention contain no hidden
authoritative advice, and failure never increases authority.
