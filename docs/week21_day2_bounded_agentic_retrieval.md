\# Week 21 Day 2 — Bounded Agentic Retrieval Evaluation



\## Purpose



This experiment tested whether a bounded retrieval-feedback loop could improve

evidence coverage without weakening the deterministic safety and governance

controls already present in the Healthcare Document Intelligence / RAG system.



The central question was:



> Can the system detect a recoverable evidence gap, perform one targeted second

> retrieval, and improve evidence coverage while still assessing the final

> evidence set against the original user question?



The design deliberately avoided autonomous multi-step agents.



The prototype was constrained to a maximum of two retrieval calls.



\---



\## Architecture



The bounded retrieval path was designed as:



Question

→ Query Scope

→ Hybrid Retrieval

→ Evidence Sufficiency

→ Missing-Topic Diagnosis

→ Optional Focused Query Refinement

→ Second Hybrid Retrieval

→ Deterministic Evidence Merge

→ Evidence Sufficiency Against Original Question

→ Existing Governance Stack



The second retrieval round is allowed only when a deterministic evidence gap

can be identified.



The controller does not:



\- generate an answer;

\- bypass lifecycle controls;

\- change governance thresholds;

\- approve unsupported evidence;

\- search indefinitely;

\- compare ranking scores directly across different queries;

\- treat retrieved evidence as sufficient merely because it came from a second

&#x20; search.



\---



\## New Components



\### Evidence Topic Diagnostics



A deterministic diagnostic helper was added to the evidence-sufficiency layer.



It exposes:



\- query topics;

\- matched topics;

\- missing topics;

\- evidence terms.



This allows the retrieval controller to identify a recoverable evidence gap

without parsing human-readable reason strings.



\---



\### Deterministic Query Refinement



A query-refinement module was introduced.



The first version retained the complete original question and appended a phrase

such as:



> Focus specifically on severe weather.



Behavioural testing showed that this often returned the same evidence as the

initial Hybrid search.



The initial behavioural run produced:



\- 14 two-round cases;

\- 0 evidence-coverage improvements;

\- 0 cases becoming sufficient after refinement.



Therefore the first refinement strategy was rejected.



\---



\## Query Refiner v2



The second version changed the strategy.



Instead of repeating the full original question, the second retrieval query is

a short deterministic retrieval-oriented phrase for the missing controlled

concept.



Example:



Original question:



> How should severe weather pressure and ambulance handover disruption be

> considered together?



Initial Hybrid evidence covered:



\- ambulance\_handover



but missed:



\- severe\_weather



The second retrieval query became:



> severe weather operational plan



The final evidence was still assessed against the original multi-topic

question.



This preserves the original evidence requirement while reducing retrieval

competition from concepts that are already covered.



Uncontrolled lexical fragments such as:



\- exact

\- applied

\- advance

\- explicitly



are not used as second-round search targets.



\---



\## Safety Controls



The bounded controller enforces the following controls.



\### Maximum Retrieval Rounds



The prototype supports:



\- 1 retrieval call; or

\- maximum 2 retrieval calls.



It cannot continue searching indefinitely.



\### Scope Control



The original query is checked by the existing query-scope gate.



A refined query must also remain within the permitted scope.



\### Lifecycle Revalidation



Evidence entering the merged evidence set is revalidated.



Only retrieval-eligible Active evidence may survive.



\### Original-Question Reassessment



Evidence obtained using a focused second query is not assessed against that

focused query.



The final evidence set is always reassessed against the original user

question.



This is the main control against query drift.



\### Deterministic Evidence Acceptance



A second-round candidate is accepted only when:



1\. topic coverage becomes a strict superset of the previous coverage; and

2\. previously supported claims remain supported.



If there is no deterministic improvement, the original evidence is preserved.



\### Bounded Evidence Size



The final evidence set cannot exceed the existing `final\_k` limit.



\---



\## Testing



The initial implementation introduced tests for:



\- deterministic query refinement;

\- missing-topic behaviour;

\- maximum retrieval rounds;

\- lifecycle filtering;

\- duplicate evidence;

\- evidence-set size;

\- original-question reassessment;

\- hard-blocked claims;

\- refiner failure;

\- retrieval failure;

\- empty initial retrieval;

\- deterministic audit behaviour.



After Refiner v2 was introduced, the query-refinement test suite passed:



\- 20 tests passed.



The full project regression after the final implementation passed:



\- 421 tests passed.



No regression was detected.



\---



\## Behavioural Validation



The first behavioural validation exposed a weakness in Refiner v1.



Results:



\- 45 cases stopped because initial evidence was sufficient;

\- 12 queries were out of scope;

\- 14 cases triggered a second retrieval;

\- 0 cases improved evidence coverage;

\- 0 cases became sufficient after refinement;

\- 0 unsafe lifecycle results;

\- 0 oversized evidence sets.



This result showed that the architecture was safe but the refinement strategy

was ineffective.



\---



\## Refiner v2 Behaviour



Refiner v2 was tested using focused concept searches.



A focused query for:



> severe weather operational plan



retrieved the Severe Weather Operational Plan as the highest-ranked evidence.



Focused searches for unsupported domains such as:



\- cyber-security;

\- electronic patient record recovery;

\- medical oxygen supply failure;



did not locate dedicated supporting evidence in the current synthetic corpus.



These cases therefore remained unsupported rather than being artificially

classified as sufficient.



\---



\## Successful Multi-Document Recovery



Two controlled evaluation cases demonstrated genuine evidence recovery.



\### Q027



Original question concerned:



\- severe weather; and

\- ambulance handover disruption.



Initial Hybrid retrieval covered only:



\- ambulance\_handover.



The bounded second search used:



> severe weather operational plan



It retrieved:



\- `DOC-009-V1.0-P002-C001`



This evidence replaced:



\- `DOC-013-V1.0-P001-C001`



The final evidence set covered:



\- ambulance\_handover;

\- severe\_weather.



The final evidence assessment became sufficient.



\---



\### Q044



The same bounded pattern recovered the missing severe-weather evidence for a

question combining:



\- forecast monitoring during severe weather; and

\- ambulance handover liaison.



The second retrieval again added relevant Severe Weather Operational Plan

evidence and produced a sufficient final evidence set.



\---



\## Formal 75-Case Benchmark



The final comparison contained seven retrieval methods:



1\. Semantic

2\. Keyword

3\. Hybrid

4\. RRF-only

5\. Hybrid Rescue

6\. Hybrid + Reranker

7\. Hybrid Agentic



Results:



| Method | Top-1 | Top-k | Abstention | Active-only |

|---|---:|---:|---:|---:|

| Semantic | 77.78% | 77.78% | 100% | 100% |

| Keyword | 57.78% | 73.33% | 100% | 100% |

| Hybrid | 77.78% | 77.78% | 100% | 100% |

| RRF-only | 75.56% | 77.78% | 100% | 100% |

| Hybrid Rescue | 82.22% | 82.22% | 100% | 100% |

| Hybrid + Reranker | 66.67% | 82.22% | 100% | 100% |

| Hybrid Agentic | 82.22% | 82.22% | 100% | 100% |



Hybrid Agentic therefore matched the strongest deterministic rescue method on

both Top-1 and Top-k performance while preserving:



\- 100% abstention success;

\- 100% Active-only safety.



\---



\## Case-Level Comparison



Compared with ordinary Hybrid, Hybrid Agentic improved:



\- Q027;

\- Q044.



Ordinary Hybrid did not beat Hybrid Agentic on any case in the benchmark.



Compared with Hybrid Rescue:



\- neither method produced a case-level success that the other did not;

\- both produced identical Top-1 and Top-k aggregate performance.



Compared with the cross-encoder reranker, Hybrid Agentic won more Top-1 cases,

while the Top-k comparison was mixed.



\---



\## Runtime



Total method time in the 75-case benchmark was approximately:



\- Hybrid: 2.56 seconds;

\- Hybrid Agentic: 3.45 seconds;

\- Hybrid Rescue: 3.95 seconds;

\- Hybrid + Reranker: 28.85 seconds.



Hybrid Agentic was therefore slower than ordinary Hybrid, as expected because

some cases perform a second retrieval.



However, in this benchmark run it was faster than Hybrid Rescue and far faster

than the cross-encoder reranker.



These timings are controlled-development measurements only and should not be

presented as production latency.



\---



\## Interpretation



The experiment demonstrates that bounded retrieval feedback can recover

missing evidence in controlled multi-document cases without weakening

lifecycle or abstention controls.



However, Hybrid Agentic did not outperform Hybrid Rescue overall.



The two methods therefore should not currently be treated as replacements for

one another.



They address different retrieval failure patterns:



\### Hybrid Rescue



Useful when:



\- the original query is good;

\- evidence may already exist deeper in the same retrieval candidate pool;

\- broader same-query evidence coverage is required.



\### Hybrid Agentic



Useful when:



\- deterministic evidence diagnostics identify a specific missing concept;

\- the original multi-topic query causes an already-covered concept to dominate

&#x20; retrieval;

\- a focused second query can retrieve evidence for the missing concept.



\---



\## Architecture v2 Decision



The recommended experimental retrieval architecture is:



Question

→ Scope Gate

→ Hybrid

→ Evidence Sufficiency



If sufficient:

→ continue to governance.



If insufficient:

→ deterministic diagnosis.



Then:



\- recoverable missing concept → bounded focused retrieval;

\- same-query candidate coverage problem → Hybrid Rescue;

\- unsupported or unsafe requirement → stop / review / abstain.



All paths return to evidence sufficiency and the existing governance stack.



\---



\## Final Verdict



\*\*PASS — SAFE TO RETAIN AS AN EXPERIMENTAL ARCHITECTURE V2 CAPABILITY\*\*



Bounded Agentic Retrieval matched Hybrid Rescue at:



\- 82.22% Top-1;

\- 82.22% Top-k;

\- 100% abstention safety;

\- 100% Active-only safety.



It demonstrated targeted evidence recovery on Q027 and Q044.



It should not replace Hybrid Rescue yet.



The strongest current design is to retain both as controlled strategies and

later test a deterministic routing rule that chooses between them based on the

type of evidence gap.



\---



\## Portfolio-Safe Claim



A suitable project statement is:



> Built and evaluated a bounded agentic retrieval controller that detects

> deterministic evidence gaps, performs at most one targeted follow-up search,

> and reassesses evidence against the original question. On a 75-case

> synthetic healthcare benchmark it matched the strongest deterministic rescue

> baseline at 82.22% Top-1/Top-k accuracy while preserving 100% abstention and

> Active-only safety.



All benchmark data is synthetic and the results must not be presented as

production NHS performance.

