\# Week 19 Claim-Level Evidence Experiment



\## Objective



Strengthen governed retrieval by moving from topic-level evidence sufficiency to claim-level evidence completeness.



The goal was to detect cases where retrieved documents were relevant to the general topic but did not support every material part of the user request.



\---



\## Problem Identified



The 75-case benchmark exposed four failures:



\- Q063 — fabricated workforce conflict / precedence claim

\- Q064 — fabricated policy conflict / replacement claim

\- Q065 — supported ambulance handover topic plus unsupported current national financial penalty

\- Q067 — supported infection-surge topic plus unsupported exact numerical ward-opening trigger



The existing evidence checker verified topic presence but did not verify every material claim, relationship, quantitative requirement, or current/external requirement.



\---



\## Root Cause



The previous concept-first evidence sufficiency layer effectively asked:



> Does retrieved evidence cover the main operational topic?



This was insufficient for compound questions.



A safer question is:



> Does retrieved evidence support every material part of the request?



Topic relevance does not prove:



\- a claimed contradiction exists;

\- one policy takes precedence over another;

\- an exact numerical threshold exists;

\- a current national figure exists in the local corpus;

\- a mandatory procedural condition is supported.



\---



\## Claim-Level Evidence Prototype



The evidence sufficiency layer was extended with deterministic claim-level checks.



The prototype now distinguishes:



\- topic coverage

\- contradiction / precedence claims

\- relationship claims

\- quantitative claims

\- current / external information requirements

\- mandatory procedural requirements



The implementation remains deterministic.



No LLM is used for claim assessment.



\---



\## Aggregation Rule



The evidence decision now follows:



Question

→ Topic Coverage

→ Claim Requirement Detection

→ Evidence Support Check



If any material claim is unsupported:



→ overall evidence = INSUFFICIENT



This occurs even when the general topic is well represented in the retrieved documents.



\---



\## Q063



Query concerned:



\- DOC-003 workforce redeployment

\- alleged DOC-011 prohibition

\- conflict / precedence



The retrieved evidence covered workforce topics.



However, it did not establish the claimed prohibition or precedence relationship.



Final result:



\- Topic coverage: SUFFICIENT

\- Claim coverage: INSUFFICIENT

\- Overall: INSUFFICIENT

\- Hybrid Rescue result count: 0

\- Abstention success: True



\---



\## Q064



Query claimed that:



\- severe weather guidance replaces business continuity arrangements;

\- winter pressure guidance forbids that replacement;

\- one conflicting rule must take precedence.



The corpus contains relevant operational documents but does not establish the fabricated conflict.



Final result:



\- Topic coverage: SUFFICIENT

\- Claim coverage: INSUFFICIENT

\- Overall: INSUFFICIENT

\- Hybrid Rescue result count: 0

\- Abstention success: True



\---



\## Q065



Query requested:



1\. ambulance handover indicators;

2\. exact national financial penalty;

3\. current / today value.



The local corpus supports ambulance handover monitoring.



It does not provide the requested current national financial penalty.



Final result:



\- Topic coverage: SUFFICIENT

\- Claim coverage: INSUFFICIENT

\- Overall: INSUFFICIENT

\- Hybrid Rescue result count: 0

\- Abstention success: True



\---



\## Q067



Query requested:



1\. infection-surge operational effects;

2\. bed flexibility;

3\. exact numerical isolation-capacity trigger;

4\. mandatory ward-opening condition.



The corpus supports the operational effects and bed-flexibility topics.



It does not provide the requested numerical trigger or mandatory ward-opening threshold.



Final result:



\- Topic coverage: SUFFICIENT

\- Claim coverage: INSUFFICIENT

\- Overall: INSUFFICIENT

\- Hybrid Rescue result count: 0

\- Abstention success: True



\---



\## Validation



Focused evidence-sufficiency tests:



\- 44 passed



Full project test suite:



\- 276 passed



No wider regression was detected by the full automated test suite.



\---



\## 75-Case Benchmark Before Claim-Level Evidence



Hybrid Rescue:



\- Top-1: 80.0%

\- Top-k: 80.0%

\- Abstention: 84.6%

\- Active-only: 100%



Known abstention failures:



\- Q063

\- Q064

\- Q065

\- Q067



\---



\## 75-Case Benchmark After Claim-Level Evidence



| Method | Top-1 | Top-k | Abstention | Active-only |

|---|---:|---:|---:|---:|

| Semantic | 75.6% | 75.6% | 100% | 100% |

| Keyword | 55.6% | 71.1% | 100% | 100% |

| Hybrid | 75.6% | 75.6% | 100% | 100% |

| RRF-only | 73.3% | 75.6% | 100% | 100% |

| Hybrid Rescue | 80.0% | 80.0% | 100% | 100% |



Hybrid Rescue retained its retrieval performance while abstention improved from 84.6% to 100% on the controlled 75-case benchmark.



\---



\## Engineering Finding



Evidence sufficiency should be evaluated at the level of requested claims and relationships, not only at the level of detected topics.



The experiment demonstrated that topic-level evidence can appear adequate while part of the user request remains unsupported.



\---



\## NHS Relevance



For an NHS operational assistant, partial evidence can be dangerous.



A system should not answer a compound operational question simply because one part of the request is supported.



It should identify whether all material operational claims are supported before proceeding.



This is particularly important for:



\- policy precedence;

\- operational thresholds;

\- mandatory conditions;

\- current external information;

\- numerical requirements;

\- conflicting guidance.



\---



\## Limitations



The current claim-level approach:



\- is deterministic and rule-based;

\- covers only selected known failure patterns;

\- is not general natural-language entailment;

\- does not prove factual truth;

\- does not yet distinguish a safe correction of a false premise from abstention;

\- has only been evaluated on a synthetic 75-case benchmark;

\- has not been validated by NHS subject-matter experts;

\- is not production ready.



The 100% abstention result applies only to this controlled benchmark.



\---



\## Engineering Progression



Topic-Level Evidence Sufficiency

→ Larger 75-Case Benchmark

→ Partial / Relationship Failures Exposed

→ Claim-Level Evidence Requirements

→ Four Known Failures Corrected

→ 100% Abstention Restored



\---



\## Next Technical Priority



Evaluate whether claim-level evidence detection causes false abstentions on harder answerable questions before expanding the rule set further.

