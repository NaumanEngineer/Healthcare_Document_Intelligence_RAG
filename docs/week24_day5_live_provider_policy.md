\# Week 24 Day 5 — Controlled Live Provider Policy



\## Purpose



This policy defines how a real model provider may participate in the governed healthcare communication pipeline.



The live provider is a language-generation component.



It is not an authority engine.



It must not decide:



\- governance

\- evidence sufficiency

\- response type

\- human-review requirements

\- abstention

\- citation authority

\- evidence precedence

\- operational decisions



\---



\# Core Principle



The live model may improve language.



It must never increase authority.



\---



\# Position in the Pipeline



The controlled live provider sits after:



Question

→ Scope Gate

→ Evidence Sufficiency

→ Structured Evidence

→ Provenance

→ Precedence

→ Governance

→ Answer Contract

→ Answer Context

→ Governed Prompt



The provider therefore receives an already-governed task.



It does not decide whether the task is safe to answer.



\---



\# Provider Responsibilities



The provider may:



\- improve readability

\- improve structure

\- summarise supplied evidence

\- produce management-friendly wording

\- explain uncertainty

\- format approved evidence clearly



The provider must use only the supplied governed prompt.



\---



\# Provider Prohibitions



The provider must not:



\- use outside knowledge as evidence

\- invent facts

\- invent documents

\- invent citations

\- add new evidence

\- change packet identity

\- change governance state

\- change response type

\- remove human review

\- weaken abstention

\- override evidence precedence

\- infer authority not present in the supplied evidence



\---



\# Evidence Boundary



Evidence supplied inside the governed prompt is the complete evidence boundary for generation.



The provider must not treat its pretraining knowledge as additional evidence.



If information is missing, the provider must preserve the existing uncertainty or abstention state.



\---



\# Citation Boundary



The provider may only use citation IDs supplied in the governed citation index.



Examples:



E1

E2

E3



Unknown citations must cause output rejection.



The system must not silently repair unknown citations.



\---



\# Governance Preservation



The provider must preserve:



AUTO\_ANSWER

→ ANSWER



REVIEW\_REQUIRED

→ REVIEW



ABSTAIN

→ ABSTENTION



The provider cannot upgrade:



REVIEW\_REQUIRED

→ AUTO\_ANSWER



or:



ABSTAIN

→ ANSWER



\---



\# Human Review Preservation



If the upstream system requires human review, the live model must preserve that requirement.



It must not:



\- imply approval

\- imply final authority

\- remove review warnings

\- present a review summary as a final decision



\---



\# Abstention Preservation



When the response type is ABSTENTION:



the provider must not produce a substantive answer.



It must not expose:



\- hidden evidence

\- citations

\- inferred answers

\- speculative recommendations



It may only explain:



\- why the system cannot answer safely

\- what evidence is missing

\- what safe next action is required



\---



\# Provider Interface



The live provider should implement the same provider contract used by the controlled execution layer.



The interface should expose:



\- provider\_name

\- model\_name

\- generate(prompt)



This preserves provider neutrality.



\---



\# Configuration



Provider configuration should be external to source code.



Configuration may include:



\- model name

\- API endpoint

\- timeout

\- temperature

\- token limit



Secrets must never be committed to Git.



API keys must come from secure environment configuration.



\---



\# Determinism



Where supported, generation should use conservative settings.



Initial live-provider configuration should prefer:



\- low temperature

\- bounded output

\- structured output

\- no automatic retries



The goal is controlled communication rather than creativity.



\---



\# Output Structure



The provider must return structured output compatible with the existing Week 24 validation contract.



Free-form output should not be trusted automatically.



Malformed output should be rejected.



Rejected output should use deterministic fallback.



\---



\# Failure Handling



Provider failures must not interrupt the governed workflow.



Examples:



\- authentication failure

\- network failure

\- provider unavailable

\- malformed response

\- invalid JSON

\- schema mismatch

\- governance mismatch

\- citation violation



All such failures should result in:



MODEL FAILURE OR REJECTION

→ DETERMINISTIC FALLBACK



\---



\# No Automatic Retry Initially



The initial live-provider implementation should not automatically retry failed requests.



Reasons:



\- retries increase cost

\- retries complicate auditability

\- retries may produce inconsistent outputs

\- retries can hide provider instability



Retry policy may be introduced later as a separately governed feature.



\---



\# Timeout



A provider request should eventually have an explicit execution timeout.



Timeouts must be treated as provider failure.



Timeout implementation should be tested separately before production use.



\---



\# Audit Metadata



Each live execution should record:



\- provider\_name

\- model\_name

\- execution\_status

\- fallback\_used

\- fallback\_reason

\- governance\_decision

\- packet\_id



Future metrics may include:



\- latency

\- input tokens

\- output tokens

\- estimated cost

\- rejection rate

\- fallback rate



\---



\# Economic Measurement



The live provider should not be justified by novelty.



Its value should be measured.



Future evaluation should compare:



deterministic communication

vs

model-assisted communication



Possible measures:



\- drafting time

\- editing time

\- reviewer time

\- citation correction rate

\- briefing preparation time

\- response quality

\- fallback rate

\- cost per accepted response



Economic claims should remain prospective until measured.



\---



\# Safety Boundary



The live provider is an optional language layer.



The assurance architecture remains authoritative.



The system should remain safe even if the live provider is unavailable.



\---



\# Day 5 Principle



> The provider may generate language. The assurance layer decides whether that language is allowed to survive.
