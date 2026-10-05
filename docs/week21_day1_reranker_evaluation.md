\# Week 21 Day 1 — Dedicated Reranker Evaluation



\## Objective



Evaluate whether adding a dedicated relevance reranker after Hybrid retrieval improves the Healthcare Document Intelligence / RAG architecture sufficiently to justify adoption into Architecture v2.



The experiment was designed to answer:



\*\*Does a dedicated reranker improve evidence ranking without weakening lifecycle safety, abstention behaviour, maintainability or runtime efficiency?\*\*



\---



\# 1. Architecture Under Test



Baseline:



Question

→ Semantic + Keyword Retrieval

→ RRF Fusion

→ Lifecycle Filtering

→ Existing Selection

→ Evidence Sufficiency

→ Governance



Candidate Architecture:



Question

→ Semantic + Keyword Retrieval

→ RRF Fusion

→ Lifecycle Filtering

→ Dedicated Relevance Reranker

→ Existing RRF Threshold + Final Lifecycle Check + Top-k

→ Evidence Sufficiency

→ Governance



The dedicated reranker was implemented as an opt-in component.



Default Hybrid behaviour remained unchanged when the reranker was disabled.



\---



\# 2. Safety Design



The reranker was deliberately separated from governance.



It does not decide:



\- whether a source is current;

\- whether evidence is sufficient;

\- whether an answer should be released;

\- whether human review is required;

\- whether a high-risk claim is safe;

\- whether a citation supports an answer.



Its responsibility is limited to:



\*\*reordering already-retrieved Active candidates according to estimated query–passage relevance.\*\*



Lifecycle filtering occurs before reranking.



Final lifecycle validation remains after reranking.



\---



\# 3. Generic Reranker Interface



A new model-agnostic relevance function was added:



`rerank\_relevance(query, candidates, \*, scorer)`



The function:



\- receives already-retrieved candidates;

\- scores query/text pairs;

\- preserves original candidate metadata;

\- preserves existing retrieval scores and ranks;

\- adds `relevance\_score`;

\- adds `relevance\_rank`;

\- does not truncate the candidate set;

\- does not mutate caller-owned dictionaries;

\- fails explicitly on invalid scorer output.



The existing deterministic reranking functions were preserved.



\---



\# 4. Structural Validation



Before benchmarking, the reranker underwent dedicated validation.



Verified:



\- default Hybrid output remains unchanged when reranking is disabled;

\- original retrieval scores and ranks are preserved;

\- Draft records do not reach the scorer;

\- Superseded records do not reach the scorer;

\- Archived records do not reach the scorer;

\- final lifecycle revalidation remains;

\- `min\_rrf\_score` continues to operate on `rrf\_score`;

\- `final\_k` remains controlled by the existing final selection stage;

\- reranking does not truncate candidates;

\- equal-score behaviour is deterministic;

\- invalid scorer output fails explicitly;

\- no silent fallback occurs after scorer failure.



Structural validation verdict:



\*\*SAFE TO BENCHMARK\*\*



\---



\# 5. Reranker Candidate



Selected model:



`cross-encoder/ms-marco-MiniLM-L6-v2`



Reason for selection:



\- designed for query–passage ranking;

\- compatible with the existing sentence-transformers environment;

\- suitable for local CPU inference;

\- no external frontier-model API required.



No additional Python packages were installed.



Model cache size observed during the experiment:



approximately 91.8 MB.



Model revision used:



`233902d25c440f23af6f7d6e94d2946bac0bee0a`



\---



\# 6. Benchmark Integrity



The benchmark was intentionally kept frozen.



The following were NOT changed:



\- evaluation questions;

\- expected relevant documents;

\- relevance labels;

\- corpus;

\- lifecycle rules;

\- evidence-sufficiency rules;

\- candidate depths;

\- RRF constants;

\- retrieval thresholds;

\- hand-coded aliases.



Dataset and corpus hashes were checked before and after benchmarking.



No benchmark tuning was performed before the first comparison.



\---



\# 7. Fresh Benchmark Results



| Method | Top-1 | Top-k | Abstention | Active Compliance | Relative Retrieval Runtime |

|---|---:|---:|---:|---:|---:|

| Semantic | 77.78% | 77.78% | 100% | 100% | 0.89× |

| Keyword | 57.78% | 73.33% | 100% | 100% | 0.08× |

| Hybrid | 77.78% | 77.78% | 100% | 100% | 1.00× |

| RRF-only | 75.56% | 77.78% | 100% | 100% | 0.96× |

| Hybrid Rescue | \*\*82.22%\*\* | \*\*82.22%\*\* | 100% | 100% | 1.70× |

| Hybrid + Reranker | 66.67% | \*\*82.22%\*\* | 100% | 100% | \*\*11.34×\*\* |



All methods evaluated 75 cases.



Top-1 and Top-k metrics used 45 labelled cases.



Abstention evaluation used 26 designated cases.



These results are controlled synthetic benchmark results and must not be presented as production NHS performance.



\---



\# 8. Runtime Observation



Complete benchmark runtime:



67.46 seconds.



Reranker-method retrieval time:



29.86 seconds.



Mean retrieval time per executed reranker query:



approximately 474 ms.



Mean scorer time:



approximately 432 ms.



Scorer calls:



63\.



Candidates scored:



847\.



These timings represent one controlled run.



They are not a formal repeated performance study.



\---



\# 9. Case-Level Findings



Compared with ordinary Hybrid retrieval:



\## Top-1 Improvements



\- Q001

\- Q009

\- Q075



\## Top-1 Regressions



\- Q002

\- Q003

\- Q010

\- Q011

\- Q026

\- Q038

\- Q048

\- Q071



\## Top-k Improvements



\- Q028

\- Q047

\- Q068

\- Q075



\## Top-k Regressions



\- Q011

\- Q026



Hybrid Rescue continued to outperform the reranked path on important multi-document evidence cases such as:



\- Q027

\- Q044



In those cases, coverage-oriented rescue supplied the required evidence set while reranking did not.



Hybrid Rescue also avoided the Q011 and Q026 coverage regressions.



\---



\# 10. Key Technical Insight



The experiment shows that:



\*\*Relevance ranking and evidence coverage are not the same problem.\*\*



The cross-encoder became better at placing some individually relevant chunks into the evidence set.



However, that did not consistently produce the best complete evidence package.



For this NHS policy-intelligence architecture, some questions require:



\- multiple documents;

\- relationship evidence;

\- complementary policy evidence;

\- coverage of several query concepts.



Hybrid Rescue is explicitly designed around evidence coverage.



The cross-encoder is primarily optimising query–passage relevance.



That helps explain why Top-k improved while Top-1 deteriorated and some multi-document cases remained better served by Hybrid Rescue.



\---



\# 11. Safety Result



All tested retrieval methods maintained:



\- 100% abstention correctness;

\- 100% Active-document compliance.



The reranker therefore did not weaken the tested lifecycle or abstention controls.



The problem is not safety failure.



The problem is insufficient retrieval benefit relative to:



\- poorer Top-1 performance;

\- significantly greater runtime;

\- additional model complexity.



\---



\# 12. Regression Testing



After benchmark integration:



\*\*375 tests passed\*\*



No benchmark dataset changes were required to achieve this result.



\---



\# 13. Architecture Decision



Final classification:



\## NO CLEAR BENEFIT



Do NOT:



\- make the dedicated reranker the default retrieval path;

\- replace ordinary Hybrid retrieval with the reranker;

\- replace Hybrid Rescue;

\- tune the benchmark simply to justify the reranker.



KEEP:



\- generic `rerank\_relevance()` capability;

\- scorer abstraction;

\- tests;

\- benchmark runner;

\- benchmark outputs;

\- case-level analysis.



The implementation remains useful as:



\- an experimental retrieval capability;

\- a future model-comparison interface;

\- a possible selective tool for specific query classes;

\- a benchmarkable Architecture v2 component.



\---



\# 14. Architecture v2 Update



Previous Week 20 assumption:



Dedicated reranking = strong upgrade candidate.



Updated evidence-based decision:



\*\*Dedicated reranking = EXPERIMENTAL / DEFER DEFAULT ADOPTION\*\*



Current retrieval direction:



Hybrid Retrieval

→ Hybrid Rescue where evidence coverage is insufficient

→ future bounded agentic retrieval

→ future relationship-aware retrieval



A dedicated reranker may later be reconsidered if:



\- a substantially better reranking model is available;

\- query-class routing makes selective use economical;

\- candidate-set design improves;

\- latency is materially reduced;

\- agentic retrieval changes the candidate distribution.



No such change is justified from the current benchmark.



\---



\# 15. Economic Interpretation



Ordinary Hybrid retrieval runtime:



1.00× baseline.



Hybrid Rescue:



1.70×.



Hybrid + Reranker:



11.34×.



The reranker therefore introduces a significant compute/latency penalty without improving the strongest existing controlled retrieval score.



This fails the Week 20 economic principle:



\*\*New technology should earn its complexity.\*\*



The correct decision is to retain the capability for experimentation without imposing its cost on every query.



\---



\# 16. Important Engineering Lesson



The purpose of Architecture v2 is not to maximise the number of advanced AI components.



It is to produce:



\*\*better evidence with equal or stronger governance at economically sensible cost.\*\*



A component that is newer or more sophisticated is not automatically an architectural improvement.



This experiment demonstrates evidence-based architecture governance:



Hypothesis

→ Safe implementation

→ Frozen benchmark

→ Measurement

→ Case-level investigation

→ Cost comparison

→ Architecture decision



\---



\# 17. Final Day 1 Decision



Dedicated cross-encoder reranker:



\*\*SAFE\*\*

but

\*\*NOT ADOPTED AS DEFAULT\*\*



Hybrid Rescue remains the strongest retrieval method in the current controlled benchmark:



Top-1: 82.22%  

Top-k: 82.22%  

Abstention: 100%  

Active compliance: 100%



The reranker remains available as an opt-in experimental capability.



\---



\# 18. Next Step



Week 21 Day 2:



\## Bounded Agentic Retrieval



Central question:



\*\*Can a bounded retrieval agent improve difficult evidence searches by deciding when to search again, refine the query or follow related evidence — without sacrificing determinism, governance or cost control?\*\*

