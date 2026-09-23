\# Week 19 False-Abstention Test Plan



\## Objective



Check whether the new claim-level evidence rules are too conservative.



The system now correctly abstains on:

\- unsupported conflicts;

\- unsupported quantitative thresholds;

\- unsupported current/external facts;

\- unsupported mandatory conditions.



The next risk is the opposite failure:



> A genuinely answerable question may be rejected because the claim-level rules are too strict.



\---



\## Test Principle



Create hard but answerable questions where the required evidence really exists in the current corpus.



The system should answer when all material claims are supported.



Do not change retrieval logic during this experiment.



\---



\## Target Cases



Create approximately 12 new temporary test cases covering:



\### 1. Quantitative-looking but actually supported

Questions containing a number or threshold that is explicitly present in the source text.



Expected:

SUFFICIENT



\### 2. Relationship claims that are explicitly supported

Questions asking whether one document complements, coordinates with, or supports another when that relationship is stated in the corpus.



Expected:

SUFFICIENT



\### 3. Multi-document answerable questions

Questions requiring two documents where both pieces of evidence are present.



Expected:

SUFFICIENT



\### 4. Procedural requirements explicitly stated

Questions asking for a mandatory or required action where that wording is supported in the corpus.



Expected:

SUFFICIENT



\### 5. Hard paraphrases

Questions that use different wording from the source while preserving the same operational meaning.



Expected:

SUFFICIENT



\---



\## Metrics



Track:



\- answerable cases tested

\- correct SUFFICIENT decisions

\- false abstentions

\- false-abstention rate



Formula:



False-Abstention Rate =

answerable cases incorrectly marked INSUFFICIENT

/

total answerable cases tested



\---



\## Guardrail



Do not weaken claim-level rules just to pass individual cases.



If a failure occurs:

1\. inspect the query;

2\. inspect retrieved evidence;

3\. identify whether the failure is caused by:

&#x20;  - topic detection;

&#x20;  - claim detection;

&#x20;  - evidence matching;

&#x20;  - benchmark design;

4\. only then consider a change.



\---



\## Success Criterion



The experiment should demonstrate that claim-level safety improves abstention without causing obvious rejection of well-supported operational questions.



Do not treat this as production validation.



\---



\## Next Implementation Step



Create focused automated tests for approximately 12 hard-but-answerable questions using the existing synthetic corpus.

