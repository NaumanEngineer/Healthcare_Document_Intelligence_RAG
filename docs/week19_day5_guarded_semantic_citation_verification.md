\# Week 19 Day 5 — Guarded Semantic Citation Verification



\## Objective



Move the successful Day 4 citation-verification experiment into the production citation verifier without weakening existing safety controls.



\---



\## Production Upgrade



The citation-verification pipeline now uses:



1\. citation resolution;

2\. document/chunk identity checks;

3\. lifecycle safety;

4\. lexical claim support;

5\. deterministic high-risk mismatch guards;

6\. semantic paraphrase rescue only when no hard safety condition is triggered.



\---



\## High-Risk Guard



Implemented:



`src/governance/high\_risk\_claim\_guard.py`



The guard detects:



\- unsupported numbers;

\- unsupported mandatory wording;

\- unsupported actors;

\- unsupported actions;

\- negation mismatch;

\- unsupported prohibitions.



If any high-risk mismatch is detected, semantic rescue is blocked.



\---



\## Semantic Rescue



Semantic rescue is only attempted when:



\- citation identity is valid;

\- evidence is lifecycle-safe;

\- lexical support is below threshold;

\- no high-risk mismatch is detected.



Current semantic model:



`sentence-transformers/all-MiniLM-L6-v2`



Current lexical threshold:



`0.60`



Current semantic rescue threshold:



`0.75`



\---



\## Safety Principle



Semantic similarity can never override:



\- citation mismatch;

\- non-Active evidence;

\- unsupported numerical claims;

\- unsupported deadlines;

\- unsupported actors;

\- unsupported mandatory actions;

\- negation mismatches;

\- unsupported prohibitions.



\---



\## Validation



High-risk claim guard:

\- 10 tests passed



Citation verification:

\- 16 tests passed



Realistic citation benchmark:

\- 15 cases

\- 14/15 correct

\- 93.3% accuracy

\- 0 false acceptances

\- 1 false rejection



Full project regression:

\- 320 tests passed



\---



\## Remaining Limitation



CIT010 remains REVIEW\_REQUIRED.



This case asks the system to state that the available evidence does not establish a conflict between two policies.



This is not an ordinary single-claim / single-citation verification problem.



It requires evidence-set reasoning across multiple documents.



Therefore it remains outside the current citation-verification scope.



\---



\## Engineering Finding



Lexical verification alone is too rigid for some grounded paraphrases.



Semantic similarity alone is unsafe because materially incorrect claims may remain semantically similar to valid evidence.



The safer design is:



Lexical verification

→ hard safety checks

→ high-risk mismatch guards

→ semantic rescue only for low-risk paraphrases



\---



\## Current Status



Production citation verifier upgraded successfully.



Controlled realistic benchmark:

\- 93.3% accuracy

\- 0 false acceptances

\- 1 known false rejection



Full regression:

\- 320 tests passed



\---



\## Next Priority



Design a separate evidence-set reasoning mechanism for corrective false-premise cases such as CIT010, without weakening the existing citation-verification safety architecture.

