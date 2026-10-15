\# Week 25 Day 4 Closeout — Groundedness and Hallucination Resistance



\## Objective



Day 4 strengthened the Healthcare Document Intelligence RAG assurance layer beyond citation presence and citation correctness.



The objective was to detect cases where an answer may contain citations but still introduces unsupported, overstated, authoritative, conflicting, or fabricated content.



The governing principle is:



> A cited answer is not necessarily a grounded answer.



\---



\## Assurance Layers Added



Day 4 introduced three new evaluation layers:



1\. Groundedness audit

2\. Overstatement audit

3\. Hallucination-resistance audit



These operate alongside the existing Week 25 citation and multi-source assurance controls.



The resulting assurance path is:



Question  

→ Evidence Packet  

→ Evidence Precedence  

→ Governance Decision  

→ Answer Context  

→ Citation Linkage  

→ Citation Completeness  

→ Citation Verification  

→ Groundedness Audit  

→ Overstatement Audit  

→ Hallucination Resistance  

→ Conflict Coverage  

→ Accept / Review / Abstain



\---



\## Groundedness Audit



Implemented in:



`src/evaluation/groundedness\_audit.py`



Groundedness states:



\- GROUNDED

\- PARTIALLY\_GROUNDED

\- UNGROUNDED

\- NOT\_APPLICABLE



The audit checks whether material answer claims are justified by approved evidence rather than merely sharing vocabulary with retrieved documents.



It also reuses the existing high-risk claim guard to detect unsupported:



\- numerical thresholds

\- mandatory language

\- actors

\- operational actions

\- prohibitions



Answer-level outcomes are:



\- PASS

\- REVIEW\_REQUIRED

\- ABSTAIN



\---



\## Overstatement Audit



Implemented in:



`src/evaluation/overstatement\_audit.py`



The audit detects whether the answer increases certainty, authority, obligation, causality, or universality beyond the supporting evidence.



Examples include transformations such as:



\- may → must

\- conditional → definite

\- advisory → mandatory

\- possible association → causal statement

\- limited applicability → universal statement



Overstatement does not require a statement to be false in the real world.



The safety question is whether the approved evidence supports the stronger wording used in the answer.



\---



\## Hallucination-Resistance Audit



Implemented in:



`src/evaluation/hallucination\_resistance.py`



The hallucination-resistance layer combines groundedness and overstatement results with governance-state protection.



It detects:



\- unsupported answer content

\- fabricated operational guidance

\- fabricated numerical thresholds

\- hidden uncertainty

\- authority escalation

\- directive content inside REVIEW\_REQUIRED

\- substantive advice inside ABSTAIN

\- governance-state violations



Important safety property:



The evaluation layer may reduce answer authority but must never increase it.



Therefore:



\- AUTO\_ANSWER may become REVIEW\_REQUIRED

\- REVIEW\_REQUIRED may not become AUTO\_ANSWER

\- ABSTAIN remains ABSTAIN



\---



\## Conflict Coverage



The Day 4 benchmark runner adds explicit conflict-coverage assurance.



For known conflicting evidence, a response must preserve the full evidence relationship rather than select one side and silently present it as the conclusion.



This protects the distinction between:



Safe:



> The approved evidence contains conflicting operational positions.



Unsafe:



> Escalation should occur now.



when the evidence base explicitly contains opposing positions.



\---



\## Integrated Faithfulness Benchmark



Implemented in:



`src/evaluation/run\_week25\_day4\_faithfulness\_benchmark.py`



The runner integrates:



\- Day 3 citation verification

\- citation completeness

\- multi-source claim verification

\- evidence precedence

\- Day 4 groundedness

\- overstatement detection

\- hallucination resistance

\- governance preservation

\- conflict coverage



The existing 18-case Week 25 benchmark remains authoritative.



The benchmark was not weakened to achieve a higher score.



Additional conservative safety signals are permitted when they do not increase answer authority.



\---



\## Key Adversarial Cases



The integrated benchmark specifically protects against:



\- unsupported operational recommendations

\- partially supported compound claims

\- discretionary language becoming mandatory

\- conflicting evidence being selectively ignored

\- uncertainty being hidden

\- REVIEW\_REQUIRED becoming authoritative

\- substantive advice inside ABSTAIN

\- fabricated numerical thresholds



\---



\## Week 24 Regression Hardening



The full repository regression identified two stale Week 24 ABSTAIN test fixtures.



Production ABSTAIN validation already required the hardened four-section contract:



\- unable\_to\_answer\_safely

\- reason

\- missing\_information

\- what\_is\_needed\_to\_continue



The stale test fixtures were aligned with that contract.



Production governance logic was not weakened.



This preserves the principle:



> The model is optional. The assurance path is not.



\---



\## Validation Evidence



Day 4 focused tests covered:



\- groundedness

\- overstatement

\- hallucination resistance

\- high-risk claim guarding

\- citation guard ordering

\- integrated Week 25 benchmark behaviour



The full repository regression completed successfully:



`933 passed`



The remaining pytest cache warning is an environment-level Windows cache-directory issue and does not represent a test failure.



`git diff --check` completed cleanly.



\---



\## Safety Properties Preserved



Day 4 preserves the following safety guarantees:



1\. Evidence remains the authority boundary.

2\. Citations alone cannot legitimise unsupported claims.

3\. Multi-source relationships must preserve required evidence.

4\. Conflicting evidence cannot be silently collapsed into one conclusion.

5\. Uncertainty cannot be converted into unsupported certainty.

6\. REVIEW\_REQUIRED cannot become authoritative.

7\. ABSTAIN cannot contain substantive operational advice.

8\. Unsupported numerical thresholds are treated as hallucination risk.

9\. Evaluation controls may reduce authority but never increase it.

10\. No external knowledge is used to justify unsupported benchmark claims.



\---



\## Portfolio Significance



This moves the project beyond a standard RAG demonstration.



The system now demonstrates an assurance-oriented healthcare AI architecture that separates:



\- retrieval

\- provenance

\- precedence

\- governance

\- citation assurance

\- groundedness

\- hallucination detection

\- abstention

\- human review



This is particularly relevant for high-risk healthcare and NHS operational decision-support systems where a fluent answer is not sufficient evidence of safety.



\---



\## Day 4 Status



Status: COMPLETE



Next:



Week 25 Day 5 — automated benchmark execution, consolidated evaluation reporting, regression evidence, and repeatable assurance measurement.

