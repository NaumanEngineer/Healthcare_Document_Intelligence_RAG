\# Week 20 Day 2 — RAG, Retrieval and Evidence Architecture Review



\## Objective



Review whether the Week 19 retrieval architecture should be kept, simplified, upgraded or replaced.



The review focuses on:



\- semantic retrieval;

\- BM25 / keyword retrieval;

\- hybrid retrieval;

\- RRF;

\- Hybrid Rescue;

\- reranking;

\- agentic retrieval;

\- long-context reasoning;

\- relationship-aware retrieval;

\- graph-style evidence structures;

\- Microsoft Data Formulator as a structured-data exploration candidate.



The goal is not to replace working components simply because newer techniques exist.



The goal is to identify changes that improve:



\- retrieval quality;

\- evidence provenance;

\- lifecycle safety;

\- cross-document reasoning;

\- operational usefulness;

\- cost;

\- maintainability;

\- auditability.



\---



\## Architecture v1 Retrieval Baseline



Current retrieval flow:



Question

→ Semantic Retrieval

\+ BM25 Keyword Retrieval

→ Hybrid / RRF Combination

→ Hybrid Rescue

→ Active-Document Filtering

→ Evidence Sufficiency

→ Answer Generation

→ Citation and Governance Checks



Controlled synthetic benchmark baseline:



Hybrid Rescue:

\- Top-1 accuracy: 82.22%

\- Top-k accuracy: 82.22%

\- Abstention accuracy: 100%

\- Active-document compliance: 100%



These results are controlled synthetic benchmark results and should not be presented as production NHS performance.



\---



\## Current Retrieval Strengths



The existing stack already provides:



1\. Semantic flexibility

2\. Exact-term recovery

3\. Hybrid ranking

4\. Targeted rescue for known misses

5\. Active-document filtering

6\. Evidence sufficiency checks

7\. Provenance for later citation verification



This remains the Architecture v1 comparison baseline.



\---



\## Semantic Retrieval



Decision:



KEEP



Reason:



Semantic retrieval remains useful when user language differs from policy wording.



Example:



Question:

"What happens when staffing becomes critically unsafe?"



Document:

"Escalation is required when staffing resilience falls below safe operational levels."



Keyword-only search may miss this relationship.



\---



\## BM25 / Keyword Retrieval



Decision:



KEEP



Reason:



Exact policy terms, document identifiers, thresholds and mandatory wording remain important.



Examples:



\- OPEL 4

\- DOC-011

\- major incident

\- must escalate



Keyword retrieval therefore remains complementary to semantic retrieval.



\---



\## Hybrid Retrieval / RRF



Decision:



KEEP



Reason:



The NHS evidence environment contains both:



\- conceptual language;

\- exact policy terminology.



Hybrid retrieval continues to provide a strong balance between semantic and lexical matching.



The current architecture should not revert to vector-only retrieval.



\---



\## Hybrid Rescue



Decision:



KEEP FOR NOW



Reason:



Hybrid Rescue was introduced to recover specific known failure patterns without globally changing ranking behaviour.



It materially improved the controlled synthetic benchmark.



However, Week 20 should treat it as a candidate for future simplification if stronger reranking or iterative retrieval can deliver the same benefit more generally.



Future question:



Can a modern reranker or agentic retrieval process replace some hand-built rescue logic?



\---



\## Dedicated Reranking



Decision:



UPGRADE CANDIDATE



Potential flow:



Initial retrieval

→ candidate set

→ reranker

→ top evidence



Potential value:



\- better distinction between superficially similar policy chunks;

\- stronger ranking of governing clauses;

\- lower noise in evidence packages.



Reranking should be benchmarked against the existing Hybrid Rescue baseline before adoption.



\---



\## Agentic Retrieval



Decision:



STRONG UPGRADE CANDIDATE



Agentic retrieval allows the system to:



search

→ inspect

→ refine query

→ follow document references

→ search again

→ build evidence set



This is particularly useful for complex NHS questions such as:



"Which policy applies here, and does another document override or constrain it?"



A single retrieval pass may not discover all required evidence.



Agentic retrieval should remain bounded by:



\- lifecycle filtering;

\- source restrictions;

\- evidence sufficiency;

\- auditability.



The retrieval agent should not be allowed to invent relationships or authoritative policy status.



\---



\## Long Context



Decision:



UPGRADE AS A COMPLEMENT



Long context should not automatically replace RAG.



Preferred architecture:



Controlled retrieval

→ lifecycle-safe selected evidence

→ larger context window

→ cross-document reasoning

→ deterministic assurance



Role separation:



RAG:

find the right evidence.



Long context:

reason across a larger selected evidence set.



Governance:

verify whether the resulting claims are safe and supported.



\---



\## What Long Context Should Not Replace



KEEP:



\- lifecycle filtering;

\- version control;

\- provenance;

\- citation verification;

\- evidence sufficiency;

\- high-risk claim checks;

\- human review;

\- abstention.



Large context capacity does not establish whether evidence is current, authoritative or sufficient.



\---



\## Relationship-Aware Retrieval



Decision:



STRONG UPGRADE CANDIDATE



Current Week 19 capability already validates relationships such as:



\- CONFLICT

\- COMPLEMENTS

\- REPLACES

\- TAKES\_PRECEDENCE



Current limitation:



These relationships are mainly evaluated after documents have already been retrieved.



Future enhancement:



Hybrid retrieval

→ retrieve relevant document

→ inspect verified document relationships

→ expand to connected documents

→ lifecycle filtering

→ reranking

→ evidence package



This may improve complex policy retrieval where one governing document references, replaces or constrains another.



\---



\## Full GraphRAG



Decision:



DO NOT ADOPT NOW



Reason:



A full graph architecture introduces:



\- graph infrastructure;

\- entity extraction;

\- relationship extraction;

\- graph maintenance;

\- additional evaluation;

\- higher implementation complexity.



Current project needs do not yet justify that complexity.



\---



\## Lightweight Relationship Metadata



Decision:



UPGRADE CANDIDATE



Preferred first step:



Add verified relationship metadata to documents.



Example:



{

&#x20; "document\_id": "DOC-003",

&#x20; "relationships": \[

&#x20;   {

&#x20;     "type": "COMPLEMENTS",

&#x20;     "target\_document\_id": "DOC-009"

&#x20;   },

&#x20;   {

&#x20;     "type": "REFERENCES",

&#x20;     "target\_document\_id": "DOC-011"

&#x20;   }

&#x20; ]

}



Relationship metadata should come from:



\- explicit policy wording;

\- verified metadata;

\- human curation;

\- deterministic extraction followed by validation.



High-risk relationships such as:



\- REPLACES

\- TAKES\_PRECEDENCE

\- CONFLICT



must not be inferred casually from semantic similarity.



\---



\## Microsoft Data Formulator Review



Classification:



PILOT / BORROW DESIGN



Not:



\- a replacement for SQL;

\- a replacement for PostgreSQL;

\- a replacement for Power BI;

\- a core production dependency at this stage.



Potential value:



\- rapid exploratory analysis;

\- conversational structured-data investigation;

\- faster chart creation;

\- branching analytical workflows;

\- lower time-to-insight.



\---



\## Data Thread Design Pattern



Strong design idea:



Main operational question

→ workforce branch

→ bed-pressure branch

→ incident branch

→ external-pressure branch

→ evidence-backed synthesis



This aligns well with the Week 20 architecture principle:



one strong orchestrator

\+

bounded analytical workstreams

\+

governed evidence.



The Data Thread concept may be more valuable as a design pattern than the Data Formulator product itself.



\---



\## Data Formulator Pilot Questions



Future pilot should test:



1\. Which Trust has deteriorated most over the last seven days?

2\. Is staffing pressure associated with higher OPEL levels?

3\. Which dates combine high A\&E breach, bed pressure and incident activity?



Compare against SQL + Power BI using:



\- time to first useful insight;

\- correctness;

\- follow-up flexibility;

\- visual quality;

\- repeatability;

\- auditability;

\- governed metric consistency;

\- analyst time saved.



\---



\## Governed Metric Requirement



Structured-data exploration must not invent NHS metric definitions.



Examples such as:



\- bed occupancy;

\- A\&E breach;

\- staffing pressure;

\- OPEL level



must retain governed definitions.



The exploratory AI layer may help investigate the data.



It should not redefine the meaning of governed operational metrics.



\---



\## Day 2 Decision Table



| Capability | Decision |

|---|---|

| Semantic retrieval | KEEP |

| BM25 / keyword retrieval | KEEP |

| Hybrid / RRF | KEEP |

| Hybrid Rescue | KEEP FOR NOW |

| Dedicated reranker | UPGRADE CANDIDATE |

| Agentic iterative retrieval | STRONG UPGRADE CANDIDATE |

| Long-context reasoning | ADD AS COMPLEMENT |

| Lifecycle filtering | KEEP |

| Evidence sufficiency | KEEP |

| Relationship-aware retrieval | STRONG UPGRADE CANDIDATE |

| Lightweight relationship metadata | UPGRADE CANDIDATE |

| Full GraphRAG stack | DO NOT ADOPT NOW |

| Data Formulator | PILOT |

| Data Thread design | BORROW |

| SQL | KEEP |

| PostgreSQL | KEEP |

| Power BI | KEEP |



\---



\## Architecture v2 Retrieval Direction



Question

↓

Intent / Complexity Assessment

↓

Hybrid Retrieval

↓

Optional Reranking

↓

Optional Agentic Retrieval for Complex Questions

↓

Relationship-Aware Expansion

↓

Lifecycle Filtering

↓

Selected Evidence Package

↓

Long-Context Reasoning Where Justified

↓

Deterministic Assurance

↓

AUTO\_ANSWER / REVIEW\_REQUIRED / ABSTAIN



\---



\## Economic Interpretation



The objective is not simply higher retrieval scores.



The business goal is to reduce:



\- analyst searching time;

\- manual document follow-up;

\- repeated policy checking;

\- unnecessary report preparation;

\- risk of using obsolete or incomplete evidence.



Future evaluation should measure:



\- retrieval accuracy;

\- analyst minutes saved;

\- policy-search time saved;

\- number of manual document lookups avoided;

\- cost per governed query;

\- false acceptance rate;

\- human-review rate.



\---



\## Key Architecture Principle



The Week 20 retrieval direction is:



\*\*Do not replace a strong hybrid retrieval foundation. Add smarter behaviour around it.\*\*



The likely next step is:



hybrid retrieval

\+

reranking

\+

bounded iterative retrieval

\+

relationship awareness

\+

selective long context

\+

deterministic assurance



\---



\## Day 2 Conclusion



The existing retrieval architecture is not obsolete.



The next major improvement is likely to come from:



\- smarter ranking;

\- iterative retrieval;

\- relationship-aware evidence expansion;

\- selective use of long context.



The assurance layer remains essential.



\---



\## Next Review



Day 3 will focus on:



\- Microsoft Fabric;

\- Azure AI services;

\- data architecture;

\- deployment patterns;

\- enterprise identity and access;

\- monitoring;

\- integration between structured operational data and the governed AI layer.



The central question will be:



\*\*Which parts of the project should remain local/open-source, and which should move toward enterprise-grade Microsoft infrastructure?\*\*

