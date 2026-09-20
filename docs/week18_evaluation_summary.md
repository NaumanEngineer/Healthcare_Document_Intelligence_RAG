\# Week 18 Evaluation Summary



\## Project



Healthcare Document Intelligence / RAG Assistant



\## Week 18 Objective



Week 18 evaluated whether retrieval quality, lifecycle governance, abstention, and human-review routing could be improved beyond the Week 17 baseline.



The work compared multiple retrieval strategies and introduced explicit operational safety controls.



\---



\# Retrieval Methods Evaluated



Four retrieval approaches were tested:



1\. Semantic retrieval

2\. BM25 keyword retrieval

3\. Hybrid retrieval

4\. RRF-only hybrid retrieval



The benchmark used 14 controlled evaluation cases covering:



\- operational escalation;

\- workforce pressure;

\- bed capacity;

\- winter pressure;

\- business continuity;

\- governance;

\- lifecycle conflicts;

\- cross-document reasoning;

\- clinical out-of-scope requests;

\- unsupported current external information.



\---



\# Final Retrieval Results



| Method | Top-1 | Top-k | Abstention | Active-only |

|---|---:|---:|---:|---:|

| Semantic | 0.70 | 0.90 | 1.00 | 1.00 |

| BM25 | 0.20 | 0.40 | 1.00 | 1.00 |

| Hybrid | 0.70 | 0.90 | 1.00 | 1.00 |

| RRF-only | 0.40 | 0.50 | 1.00 | 1.00 |



\---



\# Key Retrieval Findings



\## Semantic retrieval remained the strongest baseline



Semantic retrieval achieved:



\- 70% Top-1 success;

\- 90% Top-k success.



This confirmed that semantic similarity remained effective for the synthetic operational-policy corpus.



\---



\## BM25 was useful but substantially weaker overall



BM25 achieved:



\- 20% Top-1 success;

\- 40% Top-k success.



Keyword retrieval sometimes captured exact terminology that semantic retrieval missed, but it was not strong enough to replace semantic retrieval.



\---



\## Original hybrid retrieval did not improve aggregate accuracy



Hybrid retrieval achieved the same aggregate result as semantic retrieval:



\- 70% Top-1;

\- 90% Top-k.



This showed that adding retrieval methods does not automatically improve system quality.



The experiment therefore did not justify claiming that hybrid retrieval was superior.



\---



\## RRF-only fusion performed worse



Removing the post-fusion reranker reduced performance to:



\- 40% Top-1;

\- 50% Top-k.



This showed that the existing reranking stage was contributing useful retrieval quality.



\---



\# Abstention Finding



The initial retrieval system had:



\- 0% abstention success.



Out-of-scope questions still returned semantically related documents.



Examples included:



\- medication prescribing;

\- antibiotic dosing;

\- current NHS England leadership information.



A simple similarity threshold was not sufficient because an unsupported question could still have a similarity score close to a valid operational question.



The solution was a deterministic query-scope gate.



After introducing the scope gate:



\- abstention success increased to 100%;

\- semantic retrieval accuracy remained unchanged;

\- Active-only retrieval remained 100%.



This demonstrated that retrieval relevance and evidence sufficiency are different controls.



\---



\# Lifecycle Governance



All evaluated retrieval methods achieved:



\- 100% Active-only compliance.



Draft, Superseded, and Archived evidence was not treated as normal authoritative evidence.



This is important because document relevance alone does not establish document authority.



\---



\# Human Review Layer



A governance decision layer was added with three possible outcomes:



\## AUTO\_ANSWER



Used when:



\- the question is in scope;

\- evidence is Active;

\- top semantic similarity is sufficiently strong;

\- the score gap provides reasonable separation;

\- no cross-document or lifecycle warning is present.



\## REVIEW\_REQUIRED



Used when:



\- the question is in scope;

\- relevant evidence exists;

\- confidence is insufficient for automatic answering;

\- cross-document reasoning is required;

\- lifecycle or authority ambiguity exists.



\## ABSTAIN



Used when:



\- the question is out of scope;

\- evidence is unavailable;

\- the request requires unsupported clinical advice;

\- the request requires unsupported external current information.



\---



\# Final Human-Review Distribution



Across 14 evaluation cases:



| Outcome | Cases |

|---|---:|

| AUTO\_ANSWER | 3 |

| REVIEW\_REQUIRED | 8 |

| ABSTAIN | 3 |



The AUTO\_ANSWER cases were:



\- Q003 — bed-capacity escalation guidance;

\- Q005 — business continuity during service disruption;

\- Q006 — winter-pressure operational guidance.



These cases had clear operational scope and sufficiently strong top evidence.



\---



\# Auditability



A structured audit-record model was introduced to capture:



\- query ID;

\- question;

\- timestamp;

\- retrieval method;

\- scope decision;

\- scope reason;

\- retrieved evidence;

\- document status;

\- document version;

\- retrieval scores;

\- governance decision;

\- decision reason;

\- reviewer status;

\- reviewer action fields.



This supports traceability and later human oversight.



\---



\# Main Engineering Lesson



The strongest Week 18 finding was:



> Better retrieval alone is not enough for a governed healthcare AI system.



A safer architecture separates:



1\. query scope;

2\. retrieval;

3\. lifecycle eligibility;

4\. evidence sufficiency;

5\. human-review routing;

6\. answer generation;

7\. auditability.



\---



\# Current Architecture



User Question  

↓  

Scope Gate  

↓  

Semantic / Keyword / Hybrid Retrieval  

↓  

Lifecycle Filtering  

↓  

Reranking  

↓  

Evidence Assessment  

↓  

AUTO\_ANSWER / REVIEW\_REQUIRED / ABSTAIN  

↓  

Grounded Answer or Human Review  

↓  

Audit Record



\---



\# Limitations



This evaluation uses a small synthetic corpus and a limited 14-case benchmark.



The confidence thresholds are prototype values calibrated against the current evaluation set.



They should not be treated as clinically or operationally validated production thresholds.



Further work should include:



\- larger evaluation datasets;

\- expert review;

\- adversarial testing;

\- score calibration;

\- evidence conflict detection;

\- citation verification;

\- real NHS document structures;

\- external validation;

\- monitoring for model and corpus drift.



\---



\# Portfolio Conclusion



Week 18 moved the project from a basic RAG retrieval prototype toward a governed operational evidence assistant.



The system now demonstrates:



\- semantic retrieval;

\- BM25 retrieval;

\- hybrid retrieval;

\- controlled RRF experimentation;

\- lifecycle-aware retrieval;

\- scope-based abstention;

\- human-review routing;

\- evidence confidence rules;

\- structured auditability;

\- transparent benchmark reporting.



The project deliberately prioritises traceability, evidence quality, and human accountability over unsupported automation.

