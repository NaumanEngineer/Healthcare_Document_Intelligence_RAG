\# Week 19 Day 4 — Realistic Answer Grounding Evaluation



\## Objective



Evaluate the citation-verification layer against more realistic generated-answer failure modes rather than only clean unit-test examples.



The focus was on measuring:

\- false acceptances;

\- false rejections;

\- paraphrase handling;

\- invented numbers;

\- invented deadlines;

\- unsupported actors;

\- unsupported mandatory actions;

\- negation flips;

\- lifecycle-unsafe citations.



\---



\## Initial Realistic Evaluation



The first 10-case evaluation produced:



\- Correct: 8/10

\- Accuracy: 80.0%

\- False acceptances: 0

\- False rejections: 2



False rejections:

\- CIT007 — grounded paraphrase

\- CIT010 — corrective false premise



\---



\## Threshold Sweep



A lexical threshold sweep showed that lowering the support threshold below 0.60 improved paraphrase acceptance but introduced unsafe false acceptances.



At threshold 0.55:

\- accuracy improved;

\- but an unsupported 30-minute business continuity deadline was accepted.



Decision:

\- retain 0.60 lexical threshold;

\- do not trade safety for higher apparent accuracy.



\---



\## Semantic Similarity Experiment



Sentence-transformer semantic similarity improved paraphrase recognition but was not safe by itself.



Unsafe examples still achieved high similarity:

\- wrong numerical threshold

\- negation flip

\- fabricated prohibition

\- invented deadline



Conclusion:



> Semantic similarity alone cannot establish claim support.



\---



\## High-Risk Claim Guard Experiment



A deterministic high-risk guard layer was tested against 15 controlled cases.



Guard categories:

\- unsupported numbers;

\- unsupported mandatory wording;

\- unsupported actors;

\- unsupported actions;

\- negation mismatch;

\- unsupported prohibition.



Results:

\- Correct: 15/15

\- Accuracy: 100%

\- False blocks: 0

\- Missed high-risk cases: 0



This was a controlled experiment only.



\---



\## Combined Experimental Verifier



The experimental verifier combined:



1\. existing lexical verification;

2\. citation and lifecycle protection;

3\. high-risk claim guards;

4\. semantic rescue for safe paraphrases.



Final result:



\- Correct: 14/15

\- Accuracy: 93.3%

\- False acceptances: 0

\- False rejections: 1



CIT007 was successfully rescued as a grounded paraphrase.



CIT006 lifecycle-unsafe evidence remained blocked.



CIT010 remained REVIEW\_REQUIRED.



\---



\## Remaining Failure



CIT010 asks the system to correct a false premise:



The answer states that the available evidence does not establish a conflict between two policies.



This cannot be validated reliably through single-claim / single-citation lexical or semantic matching.



It requires evidence-set reasoning across multiple documents.



Therefore corrective false-premise handling should be treated as a separate future validation path rather than forced into ordinary citation verification.



\---



\## Engineering Conclusion



The safest current design is:



Lexical verification

→ lifecycle and citation safety

→ high-risk mismatch guards

→ semantic rescue only for low-risk paraphrases

→ human review for unresolved cases



Important principle:



> Semantic similarity may help recover valid paraphrases, but it must not override lifecycle controls or material claim-mismatch guards.



\---



\## Current Experimental Status



Realistic generated-answer benchmark:

\- 15 cases

\- 93.3% accuracy

\- 0 false acceptances

\- 1 false rejection



This remains a synthetic benchmark and is not production validation.



\---



\## Next Priority



Decide whether the guarded semantic-rescue design is mature enough to prototype inside the production citation verifier, with dedicated regression tests and no weakening of existing safety controls.

