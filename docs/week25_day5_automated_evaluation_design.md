\# Week 25 Day 5 — Automated Evaluation Design



\## Objective



Build a repeatable evaluation workflow that runs the Week 25 citation and faithfulness assurance layers together and produces a consolidated machine-readable and human-readable result.



The evaluation framework must preserve the existing governance principle:



> The model is optional. The assurance path is not.



\---



\## Evaluation Layers



The automated runner should cover:



1\. Benchmark validation

2\. Citation correctness

3\. Citation completeness

4\. Multi-source claim verification

5\. Evidence precedence

6\. Groundedness

7\. Overstatement

8\. Hallucination resistance

9\. Conflict coverage

10\. Governance preservation

11\. Abstention safety



\---



\## Authoritative Benchmark



The existing Week 25 benchmark remains authoritative:



`data/benchmark/week25\_citation\_faithfulness\_benchmark.json`



The benchmark must not be weakened to improve evaluation scores.



Expected benchmark size:



18 cases.



\---



\## Required Outputs



The automated runner should generate:



\### Machine-readable JSON



`outputs/week25\_automated\_assurance\_report.json`



The JSON report should include:



\- run metadata

\- benchmark case count

\- matched case count

\- mismatched case count

\- benchmark match rate

\- citation verification performance

\- groundedness findings

\- overstatement findings

\- hallucination-risk findings

\- review-authority increases

\- abstention violations

\- conflict handling

\- per-case results

\- failure reasons



\### Human-readable Markdown



`outputs/week25\_automated\_assurance\_report.md`



The Markdown report should summarise:



\- overall status

\- benchmark performance

\- safety-control coverage

\- failed cases

\- high-risk findings

\- governance preservation

\- regression evidence

\- interpretation



\---



\## Evaluation Decision Rule



The consolidated runner must fail closed.



Overall status:



\### PASS



Only when:



\- benchmark validation succeeds

\- all benchmark cases match

\- no required detector signal is missed

\- governance authority is never increased



\### FAIL



When:



\- benchmark structure is invalid

\- any benchmark case mismatches

\- an expected safety signal is missed

\- the evaluation runner itself cannot complete safely



\---



\## Governance Constraints



The automated evaluator must never reinterpret governance upward.



Allowed:



AUTO\_ANSWER → PASS



AUTO\_ANSWER → REVIEW\_REQUIRED



REVIEW\_REQUIRED → REVIEW\_REQUIRED



ABSTAIN → ABSTAIN



Prohibited:



REVIEW\_REQUIRED → AUTO\_ANSWER



ABSTAIN → REVIEW\_REQUIRED



ABSTAIN → AUTO\_ANSWER



\---



\## Reporting Principle



Extra conservative safety detections are permitted.



A benchmark case may legitimately activate more safety controls than its tags explicitly require.



Therefore:



\- missing expected safety signals are failures

\- additional conservative safety signals are not failures



\---



\## Repeatability



The final Day 5 runner should support a single command:



`python -m src.evaluation.run\_week25\_assurance\_suite`



The command should:



1\. validate the benchmark

2\. run the existing Day 3 citation benchmark

3\. run the Day 4 integrated faithfulness benchmark

4\. consolidate results

5\. write JSON

6\. write Markdown

7\. return a non-zero exit code if assurance fails



\---



\## Portfolio Value



This provides evidence that the project is not merely a working RAG prototype.



It demonstrates a repeatable healthcare-AI assurance workflow capable of testing:



\- provenance

\- citation quality

\- multi-source support

\- groundedness

\- uncertainty preservation

\- conflict handling

\- hallucination resistance

\- governance boundaries

\- safe abstention



This is directly relevant to safety-oriented NHS and healthcare AI engineering.



\---



\## Day 5 Acceptance Criteria



Day 5 will be complete when:



1\. a single automated assurance runner exists

2\. all 18 benchmark cases are evaluated

3\. JSON and Markdown reports are generated

4\. benchmark match rate is 100%

5\. regression tests pass

6\. the working tree is clean after commit

