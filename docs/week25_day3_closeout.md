\# Week 25 Day 3 Closeout — Citation Correctness, Completeness \& Multi-Source Assurance



\## Status



COMPLETE



Week 25 Day 3 strengthened citation assurance from simple citation presence into

deterministic citation completeness and governed multi-source verification.



The key engineering outcome was resolution of the Week 25 benchmark case

W25-C012 without weakening the benchmark expectation.



Final Week 25 hardened benchmark:



\- Cases: 18

\- Matched: 18

\- Mismatched: 0

\- Match rate: 100.0%

\- Multi-source cases evaluated: 1



\---



\## Problem Addressed



The existing citation verifier was designed primarily around one claim being

checked against one citation and one evidence item.



That was sufficient for ordinary factual claims, but it created a limitation

for relational claims such as:



> The approved evidence contains conflicting operational positions.



That conclusion cannot safely be established from one source alone.



It requires evidence from multiple approved sources together.



W25-C012 exposed this limitation:



\- required citations: E1 + E2

\- expected claim status: SUPPORTED

\- expected verification: PASS

\- expected precedence: BLOCK\_COMBINATION



Before Day 3, the claim was evaluated through a single-citation path and was

therefore classified as PARTIALLY\_SUPPORTED.



\---



\## Day 3 Architecture



Day 3 added the following assurance path:



Grounded Response

→ Claim-Citation Linker

→ Citation Completeness Audit

→ Citation Assurance

→ Single-Source Verification

→ Multi-Source Relationship Verification

→ Evidence Precedence

→ Final Verification Decision



This extends the existing architecture without replacing the original citation

verifier.



\---



\## New Citation Completeness Layer



The new citation completeness module distinguishes:



\- COMPLETE

\- INCOMPLETE

\- UNCITED

\- INVALID\_CITATION

\- NOT\_REQUIRED



A material claim can no longer be considered citation-complete simply because

one citation exists.



The claim must contain every citation required by its support contract.



Example:



Required citations:



E1 + E2



Attached:



E1



Result:



INCOMPLETE



Attached:



E1 + E2



Result:



COMPLETE



\---



\## New Citation Assurance Layer



The citation assurance layer connects:



Answer Context

→ Approved Citation Index

→ Claim-Citation Linkage

→ Citation Completeness



It preserves:



\- packet identity

\- governance decision

\- response type

\- approved citation identifiers

\- evidence provenance

\- source metadata



Unknown citations fail closed.



Citation completeness cannot upgrade governance.



\---



\## Multi-Citation Claim Linking



The claim-citation linker was upgraded to support both:



Legacy:



citation\_id = E1



and:



citation\_ids = \[E1, E2]



This preserves backward compatibility while allowing relational claims to retain

multiple approved citations.



The linker now supports:



\- one citation per claim;

\- multiple citations per claim;

\- citation de-duplication;

\- validation of unknown citation IDs;

\- rejection of contradictory singular/plural citation metadata;

\- preservation of non-substantive claims.



\---



\## Multi-Source Relationship Verification



A new deterministic verifier handles claims whose support depends on explicit

relationships between multiple approved documents.



Current supported relationship types include:



\- CONFLICT

\- REPLACES

\- TAKES\_PRECEDENCE



The verifier requires:



1\. at least two required approved citations;

2\. complete citation coverage;

3\. citation-to-evidence identity preservation;

4\. Active lifecycle state;

5\. an explicit relationship established by Evidence Precedence;

6\. claim wording consistent with the relationship.



It does not infer relationships from semantic similarity.



\---



\## W25-C012 Resolution



W25-C012 now passes through joint multi-source verification.



Claim:



> The approved evidence contains conflicting operational positions.



Required citations:



\- E1

\- E2



Actual result:



\- Claim status: SUPPORTED

\- Verification decision: PASS

\- Precedence decision: BLOCK\_COMBINATION

\- Multi-source verification used: true

\- Evidence count: 2



This is the desired governed behaviour.



PASS means the relational claim itself is faithfully supported.



It does not mean the conflicting evidence may be automatically combined.



The separate precedence decision remains:



BLOCK\_COMBINATION



Therefore the architecture preserves the distinction between:



claim truth

and

operational permission.



\---



\## Safety Properties Preserved



Day 3 preserves the following safety properties:



1\. Unknown citation IDs fail closed.

2\. Missing material citations fail closed.

3\. Citation completeness cannot override lifecycle safety.

4\. Citation completeness cannot override Evidence Precedence.

5\. Citation completeness cannot override governance.

6\. Multi-source verification requires explicit approved evidence.

7\. Semantic similarity cannot manufacture a document relationship.

8\. Non-Active evidence cannot establish a safe multi-source claim.

9\. Required multi-source citations must all be present.

10\. Human-review requirements are preserved.

11\. BLOCK\_COMBINATION remains authoritative even when a relationship claim is

&#x20;   correctly verified.

12\. ABSTAIN cannot be upgraded into an operational answer.



\---



\## Test Evidence



Day 3 test layers included:



\### Citation completeness



13 tests passed.



\### Citation assurance



12 tests passed.



\### Multi-citation linker



10 tests passed.



\### Multi-source relationship verification



10 tests passed.



\### Combined Day 3 assurance



45 tests passed.



\### Existing + Day 3 regression suite



93 tests passed before benchmark integration.



\### Final benchmark and regression suite



Week 25 benchmark:



18 / 18 matched



100.0%



Combined regression suite:



115 tests passed.



The remaining Pytest warning relates only to Windows `.pytest\_cache` creation

and does not indicate test failure or product logic failure.



\---



\## Engineering Lesson



The important architectural lesson from W25-C012 is:



> Some claims are properties of an evidence set, not properties of one evidence

> item.



A single-document verifier cannot safely prove a cross-document relationship.



Relational claims therefore require:



\- multiple approved citations;

\- evidence-set reasoning;

\- explicit precedence or relationship evidence;

\- preservation of governance boundaries.



\---



\## Portfolio Significance



This work demonstrates more than basic RAG citation generation.



It demonstrates governed evidence assurance including:



\- citation completeness;

\- provenance validation;

\- multi-source claims;

\- source lifecycle safety;

\- conflict detection;

\- precedence controls;

\- deterministic fail-closed behaviour;

\- regression benchmarking.



This is directly relevant to high-assurance healthcare AI systems where a

correctly cited answer may still be unsafe if source relationships are ignored.



\---



\## Day 3 Final Principle



> A citation proves where information came from.

>

> Citation assurance proves whether the claim used the right evidence,

> all required evidence, and preserved the governance meaning of that evidence.

