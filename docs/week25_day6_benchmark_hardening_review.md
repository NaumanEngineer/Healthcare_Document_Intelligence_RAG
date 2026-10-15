\# Week 25 Day 6 — Benchmark Hardening Review



\## Objective



Review the completed Week 25 citation and faithfulness benchmark for weaknesses, hidden assumptions, score-gaming risk, and missing adversarial coverage before final portfolio closeout.



\## Current Benchmark Status



Authoritative benchmark:



`data/benchmark/week25\_citation\_faithfulness\_benchmark.json`



Current size:



\- 18 cases



Current automated assurance status:



\- Day 3 citation assurance: 18/18 matched

\- Day 4 faithfulness assurance: 18/18 matched

\- automated assurance suite: PASS

\- full repository regression: 946 passed



A perfect benchmark score does not prove the system is universally safe.



It only proves that the current assurance implementation matches the expectations encoded in the current benchmark.



Therefore the benchmark itself must also be reviewed critically.



\---



\## Hardening Principle



> Do not improve the score by weakening the benchmark.



Benchmark evolution should make failure detection more realistic, not make existing controls easier to pass.



\---



\## Review Area 1 — Citation Correctness



Existing coverage includes:



\- missing citation

\- invalid citation

\- unsupported citation

\- lifecycle mismatch

\- partial support

\- multi-source support

\- citation mismatch



Questions to review:



\- Can a claim cite a technically valid source that is contextually irrelevant?

\- Can a claim cite the correct document but the wrong chunk?

\- Can a claim attach several citations while only one actually supports the material statement?

\- Can citation density hide unsupported claims?



Week 26 candidate:



Add adversarial cases where citation existence is valid but contextual support is misleading.



\---



\## Review Area 2 — Citation Completeness



Existing coverage checks whether material claims contain required citations.



Questions to review:



\- Can one citation be incorrectly reused across several materially different claims?

\- Can a response split one unsupported claim into several smaller claims to avoid detection?

\- Can non-material wording conceal a material operational recommendation?



Week 26 candidate:



Add claim segmentation and citation-scope adversarial tests.



\---



\## Review Area 3 — Multi-Source Support



Current Week 25 benchmark includes one explicit multi-source case.



Strength:



\- multi-source reasoning is now represented



Limitation:



\- one case is not sufficient for broad confidence



Week 26 candidates:



\- three-source agreement

\- two-source partial agreement

\- one authoritative source plus one draft source

\- conflicting evidence with different effective dates

\- same document with superseded and active versions

\- incomplete relationship metadata



\---



\## Review Area 4 — Evidence Precedence



Existing precedence states:



\- SAFE\_TO\_COMBINE

\- REVIEW\_BEFORE\_COMBINATION

\- BLOCK\_COMBINATION



Questions to review:



\- What happens when three sources have mixed lifecycle states?

\- What happens when an older approved policy conflicts with a newer draft?

\- What happens when two active documents conflict without explicit replacement metadata?

\- What happens when evidence contains ambiguous precedence language?



Week 26 candidate:



Increase precedence-specific adversarial cases.



\---



\## Review Area 5 — Groundedness



Current groundedness logic detects:



\- unsupported material claims

\- partial grounding

\- high-risk wording mismatches

\- evidence overlap failures



Known limitation:



Combined evidence may create accidental “Frankenstein support” where words from separate sources collectively resemble a claim even though no source relationship justifies the claim.



Week 26 candidate:



Add relationship-aware groundedness tests that require explicit support structure, not only aggregate textual overlap.



\---



\## Review Area 6 — Overstatement



Current overstatement checks include:



\- uncertainty removal

\- causal increase

\- universal increase

\- mandatory increase

\- policy-authority increase



Questions to review:



\- Can modal wording be strengthened indirectly without using current trigger terms?

\- Can numerical certainty be introduced without explicit mandatory language?

\- Can temporal urgency be added without words such as “immediately”?

\- Can an answer imply universal applicability through structure rather than vocabulary?



Week 26 candidate:



Expand transformation patterns and adversarial paraphrases.



\---



\## Review Area 7 — Hallucination Resistance



Current controls detect:



\- unsupported advice

\- mandatory escalation

\- operational action invention

\- abstention violations

\- review-authority increases

\- conflict omission



Questions to review:



\- Can a plausible but unsupported operational sequence pass because each individual phrase appears in evidence?

\- Can real-world common knowledge leak into the answer without evidence support?

\- Can unsupported actors or responsibilities be inferred?

\- Can the model generate recommendations that sound cautious but still exceed evidence authority?



Week 26 candidate:



Add composite hallucination cases and role-responsibility hallucination tests.



\---



\## Review Area 8 — Governance Preservation



Current rule:



The assurance layer may reduce authority but must never increase it.



Protected transitions include:



\- AUTO\_ANSWER → ANSWER

\- AUTO\_ANSWER → REVIEW

\- REVIEW\_REQUIRED → REVIEW

\- ABSTAIN → ABSTENTION



Prohibited authority increases include:



\- REVIEW\_REQUIRED → ANSWER

\- ABSTAIN → REVIEW

\- ABSTAIN → ANSWER



Week 26 candidate:



Add transition-matrix tests covering all governance-response combinations.



\---



\## Review Area 9 — Abstention Safety



Existing benchmark includes:



\- safe abstention

\- substantive advice despite abstention requirement



Questions to review:



\- Can abstention text accidentally contain action advice?

\- Can “what is needed to continue” become hidden operational guidance?

\- Can reason fields introduce unsupported certainty?

\- Can a model politely abstain but still provide dangerous recommendations elsewhere?



Week 26 candidate:



Add adversarial abstention-format tests.



\---



\## Review Area 10 — Benchmark Independence



Risk:



If benchmark expectations are derived directly from implementation behaviour, the benchmark may merely confirm the code rather than challenge it.



Controls:



\- benchmark remains an independent contract

\- expected outcomes should be defined before implementation changes

\- production logic should change to satisfy valid safety expectations

\- benchmark expectations should only change when the original expectation is conceptually wrong and the reason is documented



Week 25 example:



W25-C007 was corrected because the conceptual expected support status was wrong, not because the implementation failed.



\---



\## Current Benchmark Strengths



The Week 25 benchmark now tests:



\- supported claims

\- partially supported claims

\- unsupported claims

\- citation mismatch

\- citation completeness

\- draft evidence

\- superseded evidence

\- multi-source support

\- evidence conflict

\- overstatement

\- invented operational advice

\- review-authority escalation

\- safe abstention

\- abstention violation

\- ignored conflict



\---



\## Current Limitations



The current benchmark does not yet provide broad coverage of:



\- three-or-more-source reasoning

\- complex evidence version chains

\- multilingual evidence

\- table-derived evidence

\- OCR errors

\- numerically dense evidence

\- temporal reasoning across multiple documents

\- long answers with many claims

\- claim segmentation attacks

\- citation flooding

\- semantic paraphrase attacks

\- role and responsibility inference

\- retrieval failure versus generation failure

\- adversarial prompt injection inside evidence



These are suitable Week 26 hardening areas.



\---



\## Week 25 Hardening Decision



Do not expand the benchmark simply to increase case count during Day 6.



Week 25 should close with the stable 18-case authoritative benchmark.



Week 26 should deliberately extend the benchmark with new adversarial classes while preserving the existing 18 cases as regression anchors.



\---



\## Final Assessment



The Week 25 benchmark is strong enough to demonstrate:



\- citation assurance

\- evidence lifecycle handling

\- multi-source support

\- groundedness testing

\- overstatement detection

\- hallucination resistance

\- conflict handling

\- governance preservation

\- safe abstention



It is not evidence of universal clinical or operational safety.



The benchmark should therefore be presented as a controlled assurance framework and regression suite, not as proof that all possible unsafe RAG behaviour has been solved.



\## Status



\*\*Week 25 Day 6 Session 1 COMPLETE\*\*

