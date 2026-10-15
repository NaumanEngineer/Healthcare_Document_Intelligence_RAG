\# Week 25 Day 5 Closeout — Automated Assurance Suite



\## Objective



Build a single repeatable assurance workflow that consolidates the Week 25 citation, groundedness, hallucination-resistance, governance, and abstention checks.



\## Principle



> The model is optional. The assurance path is not.



\## What Was Built



A unified assurance runner was added:



`src/evaluation/run\_week25\_assurance\_suite.py`



The runner:



1\. validates the authoritative Week 25 benchmark;

2\. runs the Day 3 citation-faithfulness benchmark;

3\. runs the Day 4 groundedness and hallucination-resistance benchmark;

4\. verifies cross-layer case alignment;

5\. consolidates assurance results;

6\. writes machine-readable JSON;

7\. writes human-readable Markdown;

8\. fails closed with a non-zero exit code when assurance fails.



\## Single Command



The full Week 25 assurance workflow can now be run with:



`python -m src.evaluation.run\_week25\_assurance\_suite`



\## Generated Reports



Machine-readable:



`outputs/week25\_automated\_assurance\_report.json`



Human-readable:



`outputs/week25\_automated\_assurance\_report.md`



\## Benchmark Integrity



The authoritative benchmark contains 18 cases.



Upstream governance distribution:



\- AUTO\_ANSWER: 10

\- REVIEW\_REQUIRED: 6

\- ABSTAIN: 2



Expected verification distribution:



\- PASS: 4

\- REVIEW\_REQUIRED: 13

\- ABSTAIN: 1



Expected overall outcomes:



\- PASS: 6

\- PASS\_WITH\_WARNINGS: 0

\- FAIL: 12



Cases requiring human review:



\- 14



Benchmark validation status:



\*\*PASS\*\*



The expected FAIL cases are deliberate adversarial cases and are not production failures.



\## Citation and Multi-Source Assurance



Day 3 hardened citation benchmark:



\- Cases: 18

\- Matched: 18

\- Mismatched: 0

\- Match rate: 100%

\- Multi-source cases evaluated: 1



\## Groundedness and Hallucination Resistance



Day 4 integrated faithfulness benchmark:



\- Cases: 18

\- Matched: 18

\- Mismatched: 0

\- Match rate: 100%



Detected adversarial safety signals:



\- Hallucination-risk cases: 11

\- Overstatement cases: 11

\- Review-authority increases: 2

\- Abstention violations: 1

\- Ignored conflicts: 1



These detections mean the assurance controls caught deliberately adversarial benchmark behaviours. They do not mean unsafe outputs escaped the system.



\## Adversarial Case Register



The generated Markdown report records the exact benchmark cases that activated each detector, including:



\- hallucination risk;

\- overstatement;

\- review-authority increase;

\- abstention violation;

\- ignored conflict.



This makes the assurance evidence auditable.



\## Fail-Closed Hardening



A dedicated test suite was added:



`tests/test\_week25\_assurance\_suite.py`



It verifies:



\- perfect 18-case PASS behaviour;

\- incorrect benchmark case count fails;

\- Day 3 mismatch fails;

\- Day 4 mismatch fails;

\- cross-layer case-order mismatch fails;

\- duplicate case IDs fail;

\- benchmark-validation failure propagates;

\- adversarial case register uses the correct result fields;

\- safety properties are preserved;

\- JSON report generation;

\- Markdown report generation;

\- CLI exits non-zero on assurance failure;

\- CLI exits non-zero on internal runner failure.



Focused Day 5 assurance tests:



\*\*13 passed\*\*



\## Full Regression Evidence



Full repository test suite:



\*\*946 passed\*\*



No failed tests.



No test errors.



One environment-level pytest cache warning remained:



`.pytest\_cache` WinError 183



This warning did not affect the test outcomes.



\## Safety Properties Preserved



1\. The benchmark is not weakened to improve scores.

2\. Additional conservative safety detections are permitted.

3\. Missing required safety signals cause failure.

4\. Governance authority may be reduced but never increased.

5\. REVIEW\_REQUIRED cannot become authoritative.

6\. ABSTAIN cannot become substantive advice.

7\. Unsupported claims cannot be justified using external knowledge.

8\. Cross-layer case alignment is verified.

9\. Benchmark mismatches cause suite failure.

10\. Internal runner errors fail closed.



\## Portfolio Significance



The project now demonstrates more than a functioning RAG workflow.



It includes a repeatable healthcare-AI assurance system covering:



\- provenance;

\- citation verification;

\- citation completeness;

\- multi-source evidence;

\- evidence precedence;

\- groundedness;

\- overstatement detection;

\- hallucination resistance;

\- conflict handling;

\- governance preservation;

\- abstention safety;

\- automated regression evidence.



This provides stronger evidence for safety-oriented NHS and HealthTech AI engineering roles.



\## Status



\*\*Week 25 Day 5 COMPLETE\*\*



\## Next



Week 25 Day 6:



\- benchmark hardening;

\- final Week 25 evaluation summary;

\- portfolio packaging;

\- interview evidence;

\- Week 25 closeout.

