\# Week 19 Day 3 — Citation Verification and Grounded Answer Governance



\## Objective



Add a post-generation safety layer that verifies whether generated answer claims are actually supported by the cited evidence.



The system previously checked whether sufficient evidence existed before answer generation.



Day 3 added a second question:



> Did the generated answer remain grounded in that evidence?



\---



\## Problem



Good retrieval does not guarantee a grounded answer.



A system may retrieve the correct NHS operational document but still:

\- invent a threshold;

\- add an unsupported mandatory action;

\- cite the wrong document;

\- cite the wrong chunk;

\- use Draft or Superseded evidence;

\- partially support a sentence while presenting the whole sentence as authoritative.



\---



\## New Citation Verification Layer



Implemented:



`src/governance/citation\_verification.py`



The verifier checks:



\- whether a claim has a citation;

\- whether the cited document exists;

\- whether the cited chunk matches;

\- whether the evidence is lifecycle-safe;

\- whether material claim terms are supported by the cited evidence.



Claim outcomes:



\- SUPPORTED

\- PARTIALLY\_SUPPORTED

\- UNSUPPORTED

\- CITATION\_MISMATCH



\---



\## Answer-Level Citation Decision



Multiple claim results are aggregated into:



\- PASS

\- REVIEW\_REQUIRED

\- ABSTAIN



All material claims must be supported for an answer to pass citation validation.



\---



\## Governance Integration



Updated:



`src/governance/review\_decision.py`



Added post-generation governance through:



`decide\_post\_generation\_outcome()`



The design preserves the original pre-generation governance layer.



The safety hierarchy is:



1\. Scope gate

2\. Retrieval

3\. Evidence sufficiency

4\. Pre-generation governance

5\. Answer generation

6\. Citation verification

7\. Post-generation governance



\---



\## Core Safety Rule



Post-generation checks cannot upgrade an unsafe earlier decision.



Examples:



\- ABSTAIN + citation PASS → ABSTAIN

\- REVIEW\_REQUIRED + citation PASS → REVIEW\_REQUIRED

\- AUTO\_ANSWER + citation REVIEW\_REQUIRED → REVIEW\_REQUIRED

\- AUTO\_ANSWER + citation PASS → AUTO\_ANSWER



This creates a monotonic safety model:



> Later stages may preserve or downgrade safety decisions, but never upgrade an unsafe case.



\---



\## Validation



Focused citation verification:

\- 8 baseline tests passed



Hard citation cases:

\- 8 tests passed



Combined citation tests:

\- 16 tests passed



Citation + governance integration:

\- 28 tests passed



Full project regression:

\- 310 tests passed



\---



\## Hard Cases Tested



The verifier was tested against:



\- wrong document citation;

\- wrong chunk citation;

\- missing citation;

\- unsupported claims;

\- partial support;

\- fabricated thresholds;

\- Draft evidence;

\- Superseded evidence;

\- missing evidence;

\- multi-document answers;

\- mixed supported and unsupported claims.



\---



\## Key Engineering Learning



Relevant retrieval is not enough.



A trustworthy healthcare RAG system also needs to verify:



> Every material statement in the final answer is traceable to the correct supporting evidence.



\---



\## NHS Relevance



For an NHS operational assistant, citations may be interpreted by managers as evidence of authority.



Therefore an incorrect citation can be more dangerous than no citation because it can make unsupported information appear verified.



The citation-verification layer reduces this risk by checking the relationship between:



answer claim → cited chunk → document lifecycle → final governance decision.



\---



\## Current Limitation



The current prototype uses deterministic lexical support.



This does not prove full semantic entailment.



The configured lexical threshold is an experimental engineering control rather than a production-grade factuality score.



Future work may compare:

\- deterministic rules;

\- embedding-based claim support;

\- NLI models;

\- constrained LLM judging;

\- human-reviewed validation sets.



\---



\## Day 3 Outcome



The project now validates both sides of grounded RAG:



Before generation:

> Do we have enough evidence?



After generation:

> Did the answer stay within the evidence?



Full regression status:

\- 310 tests passed



Next priority:

Evaluate citation verification on realistic generated answers and measure false-positive and false-negative grounding decisions before increasing verifier complexity.

