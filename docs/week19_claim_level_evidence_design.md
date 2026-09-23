# Week 19 Claim-Level Evidence Design

## Problem Statement

The concept-first checker establishes topic coverage, not full request support. Once recognised concepts match retrieved evidence, material requirements expressed outside those concepts can escape evaluation: a prohibition, a precedence rule, a financial penalty, a numerical threshold, or a current-information requirement.

Q063, Q064, Q065 and Q067 passed the topic check despite unsupported parts of their requests. All four were initially marked SUFFICIENT, so Hybrid Rescue was not attempted. This design addresses completeness of evidence requirements without changing retrieval ranking.

## Required Distinction

| Requirement | Question to answer |
| --- | --- |
| Topic coverage | Does evidence address the relevant subject? |
| Claim coverage | Does evidence support each specific fact or requested action, rather than merely mention the topic? |
| Relationship coverage | Does evidence establish the asserted relationship, including direction, negation, conditions and precedence? |
| Quantitative requirement coverage | Does evidence supply the requested value, units, applicable population and conditions? An unrelated number is not support. |
| Current/external information requirement | Is an authoritative source available for the requested time and jurisdiction? Static policy does not establish today's position. |
| Lifecycle/authority requirement | Is the evidence eligible, approved, applicable and authoritative for this requirement? Topic relevance does not confer authority. |

## Query Decomposition Model

Query → identify requested subclaims → classify each subclaim → map each subclaim to evidence requirements → test retrieved evidence against each requirement → aggregate to final sufficiency decision

Start with transparent rules for conjunctions and request clauses, named documents, negation, precedence wording, quantitative qualifiers and temporal qualifiers. Preserve exact query spans. A single clause may generate several requirements: an exact national penalty today requires both quantitative support and current authoritative information.

Separate user assertions from facts established by evidence. Preserve qualifiers such as all, must, prohibits, replaces, exact and today; reducing them to a topic would recreate the current failure. If decomposition cannot account for a material clause, record it as unresolved rather than silently dropping it.

Each subclaim records:

| Field | Meaning |
| --- | --- |
| subclaim_id | Stable identifier within the case, such as Q065-S2. |
| text | Exact query span or a faithful normalisation retaining material qualifiers. |
| type | One of the types below; split a clause into linked requirements when necessary. |
| required_evidence | Specific fact, relationship, value or procedure needed, including source, time and authority constraints. |
| evidence_found | Evidence references with document ID, version, status, chunk/page and relevant passage; an empty list if none is found. |
| supported | True only when the requirement is established; false for missing, contradicted or unresolved support. |
| reason | Auditable explanation distinguishing missing evidence, contradiction, ambiguity, stale information and ineligible authority. |

Subclaim types:

- topic_fact
- relationship_claim
- quantitative_claim
- current_external_claim
- lifecycle_authority_claim
- procedural_claim
- contradiction_or_precedence_claim

All substantive user requests and premises necessary to answer them are material. Deterministic checks should use explicit patterns and evidence anchors, not topic overlap as a proxy for entailment. This is a bounded research design, not a claim of general natural-language understanding.

## Aggregation Rule

If any material subclaim is unsupported, overall evidence = INSUFFICIENT. A supported clause must not conceal an unsupported clause. Unresolved decomposition also prevents a SUFFICIENT decision.

A possible future exception is an explicit, authoritative correction of a false user premise. It would require identifying the false premise, citing evidence that directly corrects it, and declining to answer any remaining unsupported request. The original premise must not be relabelled as supported.

This exception is documented only: do not implement it or change benchmark outcomes in this step. Absence of supporting evidence alone is not proof that a premise is false.

## Q063 Walkthrough

Query: DOC-003 requires operational staffing redeployment while DOC-011 supposedly prohibits all redeployment. Which conflicting mandatory instruction takes precedence?

| Subclaim | Type | Evidence assessment |
| --- | --- | --- |
| DOC-003 requires staffing redeployment | procedural_claim | DOC-003 supports reviewing redeployment opportunities and says contingency actions may include authorised redeployment. This supports redeployment as an option, not the query's unconditional mandatory wording. The claim as asserted is unsupported. |
| DOC-011 prohibits all redeployment | contradiction_or_precedence_claim | The corpus's DOC-011 says leadership should review redeployment options. It does not establish the claimed prohibition. The saved returned set did not include DOC-011, so that set cannot supply its direct corrective evidence. |
| One conflicting mandatory instruction takes precedence | contradiction_or_precedence_claim | No such conflict or precedence rule is established in the corpus. General governance guidance is not a specific precedence rule. |

Overall: INSUFFICIENT for the requested adjudication. Workforce topic coverage does not substantiate the asserted conflict. A future correction would need the applicable passages and careful handling of the difference between reviewing an option and mandating an action.

## Q064 Walkthrough

Query: The severe weather plan allegedly replaces all business continuity arrangements, while the winter pressure plan forbids that replacement. Which conflicting rule should operational teams enforce?

| Subclaim | Type | Evidence assessment |
| --- | --- | --- |
| Severe-weather guidance replaces existing arrangements | relationship_claim | Unsupported as asserted. DOC-009 explicitly says the plan complements, rather than replaces, winter-pressure and business-continuity arrangements. |
| Relationship to business continuity | relationship_claim | A complementary relationship is supported by DOC-009; the claimed replacement relationship is contradicted. |
| The winter-pressure plan prohibits that replacement | contradiction_or_precedence_claim | DOC-002 contains no stated prohibition of this kind. Absence does not establish an opposite rule. |
| Which conflicting rule takes precedence | contradiction_or_precedence_claim | The alleged conflict and requested precedence are not established. |

Overall: INSUFFICIENT for the requested conflict adjudication. All three topics are present, but the claimed policy relationships are unsupported or fabricated. DOC-009 provides direct evidence for a potential future false-premise correction; topic coverage alone does not justify that outcome.

## Q065 Walkthrough

Query: What ambulance handover indicators should be monitored, and what exact national financial penalty applies to each delayed transfer today?

| Subclaim | Type | Evidence assessment |
| --- | --- | --- |
| Ambulance-handover monitoring indicators | topic_fact | Supported by DOC-008: delayed-handover counts, duration, department capacity, assessment space and downstream bed flow. |
| Exact national financial penalty per delayed transfer | quantitative_claim | Unsupported. No applicable penalty, amount, units or conditions are supplied by the corpus. |
| The penalty applies today | current_external_claim | Requires current authoritative external information. Static operational guidance does not establish applicability today. |

Overall: INSUFFICIENT. Supporting the indicators does not support the financial or temporal requirements.

## Q067 Walkthrough

Query: During an infection surge, what effects on operational bed flexibility should be assessed and what exact numerical isolation-capacity trigger mandates opening another ward?

| Subclaim | Type | Evidence assessment |
| --- | --- | --- |
| Infection-surge operational effects | topic_fact | Supported by DOC-010, including demand, staff absence, isolation requirements and patient-flow disruption. |
| Effects on bed flexibility | topic_fact | Supported by DOC-010's reduced-bed-flexibility discussion, with general capacity context in DOC-004. |
| Exact numerical isolation-capacity trigger | quantitative_claim | Unsupported. Neither source supplies the requested numerical threshold. |
| A condition mandating another ward to open | procedural_claim | Unsupported. General capacity planning and approved escalation capacity do not establish this mandatory action or its trigger. |

Overall: INSUFFICIENT. The first two subclaims are supported; the last two are not.

## Relationship to Scope Gate

Scope decides whether a question is permitted. Claim-level evidence decides whether all requested information is supported. An operational question can pass scope and still require abstention.

Q065 shows why current/external requirements must also be represented explicitly as evidence requirements, even when scope wording does not catch them. This does not authorise an evidence check to override an explicit scope rejection.

## Relationship to Hybrid Rescue

Hybrid Rescue should run only after the initial assessment identifies missing support that could plausibly be recovered from eligible local corpus evidence. Recovery should be assessed against the missing subclaims, not simply additional topic matches.

Distinguish not retrieved from known absent. A bounded local search may investigate uncertain availability, but inherently current/external requirements cannot be satisfied by static local documents. Known corpus gaps must remain unsupported. Rescue must not invent evidence, infer missing numbers or rules, or weaken authority constraints. Reassess all material requirements after rescue so newly added evidence does not hide a remaining gap.

This document does not change rescue eligibility or implementation.

## Benchmark Implications

Q063–Q064 expose an ambiguity: retrieving evidence that corrects a false premise is not necessarily unsafe. Empty-versus-nonempty retrieval scoring cannot distinguish endorsing an invented conflict from accurately correcting it. Retrieval output also does not prove what an eventual answer would assert.

Future outcome labels could distinguish:

- ANSWER_SUPPORTED: all material requested claims have adequate authoritative support.
- CORRECT_FALSE_PREMISE: authoritative evidence directly corrects a material false premise, with remaining unsupported requests explicitly declined.
- ABSTAIN_INSUFFICIENT: the request is permitted but necessary support is missing or unresolved.
- ABSTAIN_OUT_OF_SCOPE: the request is disallowed.
- REVIEW_CONFLICT: a genuine unresolved conflict between applicable authoritative sources needs human review.

Reference labels must distinguish actual document conflicts from invented conflict claims. Corrective outcomes need claim-level evidence and answer review, not an inference from retrieved document IDs. Existing benchmark labels and scoring remain unchanged.

## Engineering Principle

"Evidence sufficiency should be evaluated at the level of requested claims and relationships, not only at the level of detected topics."

## Next Implementation Step

Implement deterministic query decomposition for claim-level evidence requirements on the four known failure cases first, without changing retrieval ranking.
