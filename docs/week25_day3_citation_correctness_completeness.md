\# Week 25 Day 3 — Citation Correctness, Completeness \& Source Handling



\## Purpose



Week 25 Day 3 strengthens citation assurance beyond the question:



> Does this citation point to real evidence?



The system must also establish:



> Does every material claim have the citations it needs, and are those citations

> attached to the correct source evidence?



This work extends the existing Week 22–24 architecture. It does not replace

Evidence Objects, Evidence Precedence, Answer Context, Claim-Citation Linking,

Citation Verification, or governance decisions.



\---



\## Existing Architecture



The current answer assurance path is:



Question

→ Evidence Packet

→ Evidence Precedence

→ Governance

→ Answer Contract

→ Answer Context

→ Citation Index

→ Grounded Response

→ Claim-Citation Linker

→ Citation Verification

→ Accept / Review / Abstain



Week 25 Day 3 adds citation-completeness assurance between claim linking and the

final answer-level verification decision.



Target architecture:



Question

→ Evidence Packet

→ Evidence Precedence

→ Governance

→ Answer Contract

→ Answer Context

→ Citation Index

→ Grounded Response

→ Claim-Citation Linker

→ Citation Completeness Audit

→ Citation Verification

→ Faithfulness Evaluation

→ Accept / Review / Abstain



\---



\## Citation Correctness



A citation is correct only when all of the following are true:



1\. The citation ID exists in the approved Answer Context citation index.

2\. The citation resolves to an approved evidence item.

3\. The cited document ID matches the evidence document ID.

4\. The cited chunk ID matches the evidence chunk ID.

5\. The evidence lifecycle state is safe for the claimed use.

6\. The evidence materially supports the claim.

7\. The citation is attached to the claim it actually supports.



A structurally valid citation is not automatically a correct citation.



Example:



Claim:



> Elective activity must be cancelled immediately.



Citation:



> E1



Evidence E1:



> Teams should review workforce pressure.



The citation exists, but the citation is not correct for that claim.



\---



\## Citation Completeness



Citation completeness asks whether every material claim has all evidence

references required to support it.



A material claim must not pass merely because it has at least one citation.



The system must distinguish:



\- no citation;

\- one adequate citation;

\- one inadequate citation;

\- multiple citations where one is sufficient;

\- multiple citations where several are jointly required.



\---



\## Single-Source Claims



A normal evidence claim may be supported by one evidence item.



Example:



Claim:



> Ambulance handover delays should be monitored.



Required evidence:



E1



The claim is citation-complete when E1 is attached and E1 supports the claim.



\---



\## Multi-Source Claims



Some claims are inherently relational and cannot be established from one

evidence item alone.



Examples include:



\- two sources conflict;

\- one document replaces another;

\- one source takes precedence over another;

\- two policies provide different operational positions;

\- evidence from several sources is required to establish the conclusion.



Example:



> The approved evidence contains conflicting operational positions.



If the conclusion depends on E1 and E2 together, citing only E1 is incomplete.



The required citation set is:



E1 + E2



The claim should not receive a final SUPPORTED decision until the required

evidence set has been evaluated together.



\---



\## W25-C012



W25-C012 intentionally exposes this current architectural limitation.



Expected claim:



> The approved evidence contains conflicting operational positions.



Required citations:



E1

E2



Existing production verification evaluates one citation/evidence pair at a time.



This can produce:



PARTIALLY\_SUPPORTED

→ REVIEW\_REQUIRED



even though the evidence-set precedence layer correctly identifies:



BLOCK\_COMBINATION



The Day 3 objective is therefore not to weaken W25-C012.



The objective is to give the verifier a governed way to assess claims whose

support depends on multiple approved evidence items.



\---



\## Material vs Non-Substantive Statements



Material claims require evidence assurance.



Examples:



\- operational facts;

\- policy requirements;

\- thresholds;

\- actions;

\- responsibilities;

\- source comparisons;

\- source conflicts;

\- lifecycle or precedence claims.



Non-substantive statements may legitimately have no citation.



Examples:



\- formatting text;

\- headings;

\- process statements;

\- safe abstention wording;

\- statements explaining that human review is required, where the statement is

&#x20; generated directly from governance state rather than from document content.



Non-substantive classification must not be used to hide operational claims.



\---



\## Completeness Decisions



The citation completeness layer should use deterministic statuses:



\### COMPLETE



The material claim has all citations required for its support contract.



\### INCOMPLETE



The claim has some valid citations but is missing one or more required sources.



\### UNCITED



The material claim has no citation.



\### INVALID\_CITATION



At least one attached citation is not present in the approved citation index or

does not resolve to the expected evidence.



\### NOT\_REQUIRED



The statement is genuinely non-substantive and does not require evidence

citation.



\---



\## Answer-Level Citation Completeness Decision



The answer-level decision should be:



\### PASS



Every material claim is COMPLETE and all citation identifiers are valid.



\### REVIEW\_REQUIRED



Any material claim is:



\- INCOMPLETE;

\- UNCITED;

\- INVALID\_CITATION.



\### ABSTAIN



No material answer claims are available for citation assurance and upstream

governance already requires abstention.



Citation completeness must never upgrade upstream governance.



\---



\## Required Safety Properties



The Day 3 implementation must preserve the following properties:



1\. Unknown citation IDs fail closed.

2\. Missing citations fail closed for material claims.

3\. Superseded or unsafe evidence cannot be rehabilitated by completeness.

4\. Citation completeness cannot override evidence precedence.

5\. Citation completeness cannot override governance.

6\. Semantic similarity cannot manufacture missing citations.

7\. Multiple citations cannot be treated as interchangeable when the claim

&#x20;  requires joint evidence.

8\. A multi-source claim must preserve every source required to support the

&#x20;  relationship being asserted.

9\. Human review requirements must never be downgraded.

10\. ABSTAIN must never become an operational answer because citations exist.



\---



\## Source Handling



Approved source handling must preserve:



\- citation\_id;

\- evidence\_id;

\- document\_id;

\- chunk\_id;

\- source\_file;

\- page;

\- version;

\- lifecycle status.



The system must not create new source identifiers during answer generation.



Citation IDs must originate from the Answer Context citation index.



\---



\## Day 3 Implementation Boundary



Day 3 will add:



1\. deterministic citation-completeness auditing;

2\. validation of attached citation sets;

3\. governed support for multi-citation material claims;

4\. regression tests for missing, unknown, duplicate, partial and multi-source

&#x20;  citations;

5\. benchmark integration.



Day 3 will not:



\- introduce free-form model reasoning as an assurance control;

\- infer document authority from unsupported metadata;

\- bypass Evidence Precedence;

\- weaken lifecycle controls;

\- convert REVIEW\_REQUIRED into AUTO\_ANSWER;

\- force W25-C012 to PASS merely to improve benchmark statistics.



\---



\## Acceptance Criteria



Day 3 is complete only when:



\- existing citation verification tests continue to pass;

\- existing high-risk mismatch tests continue to pass;

\- Week 25 benchmark validation remains green;

\- single-source supported claims remain supported;

\- uncited material claims require review;

\- unknown citation IDs require review;

\- multi-source claims can preserve and evaluate multiple approved citations;

\- W25-C012 is resolved through architectural support rather than benchmark

&#x20; manipulation;

\- all changes are documented and committed with a clean working tree.



\---



\## Engineering Principle



> Citation presence is not citation assurance.



A trustworthy healthcare RAG system must know:



\- what claim was made;

\- which evidence supports it;

\- whether every required source is present;

\- whether the source is safe to use;

\- whether multiple sources must be evaluated together;

\- and whether the final claim remains faithful to those sources.

