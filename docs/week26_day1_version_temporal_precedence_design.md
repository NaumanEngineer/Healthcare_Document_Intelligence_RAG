\# Week 26 Day 1 — Version-Chain and Temporal Precedence Design



\## Objective



Define how the assurance framework should handle:



\- active documents;

\- superseded documents;

\- draft replacements;

\- archived guidance;

\- effective dates;

\- explicit replacement chains;

\- temporal validity;

\- conflicting document versions.



The goal is to prevent a RAG system from treating the newest, most similar, or most recently retrieved document as automatically authoritative.



\## Core Principle



> Recency is not the same as authority.



\---



\## Problem



Healthcare document repositories frequently contain several versions of the same or related guidance.



A retrieval system may return:



\- current approved policy;

\- superseded policy;

\- draft replacement;

\- archived guidance;

\- historical procedure.



All may contain relevant vocabulary.



Without lifecycle and temporal reasoning, a model may produce an answer that is textually supported but operationally invalid.



\---



\## Key Concepts



\### Lifecycle Status



Relevant lifecycle states include:



\- ACTIVE

\- SUPERSEDED

\- DRAFT

\- ARCHIVED



Lifecycle status describes document authority.



\### Effective Date



The date from which a document or policy applies.



\### Superseded Date



The point at which a document ceased to be current.



\### Replacement Relationship



An explicit relationship showing that one document replaces another.



Example:



`POLICY-V2 replaces POLICY-V1`



\### Query Time



The time period relevant to the user's question.



A source may be valid historically but invalid for the requested date.



\---



\## Precedence Inputs



A Week 26 precedence decision should consider:



1\. document identity;

2\. document version;

3\. lifecycle status;

4\. effective date;

5\. superseded date;

6\. explicit replacement metadata;

7\. approval status;

8\. query-relevant date;

9\. contradiction between versions;

10\. evidence purpose.



\---



\## Scenario 1 — Active vs Superseded



Evidence A:



\- version: 1

\- status: SUPERSEDED

\- rule: “Escalation must begin at threshold X.”



Evidence B:



\- version: 2

\- status: ACTIVE

\- rule: “Escalation may be considered at threshold X.”



Question:



“What is the current escalation requirement?”



Expected behaviour:



\- ACTIVE version preferred;

\- superseded mandatory wording must not be presented as current;

\- claim using Version 1 mandatory language should require review;

\- provenance should record both sources if both were retrieved.



\---



\## Scenario 2 — Active vs Draft Replacement



Evidence A:



\- status: ACTIVE

\- approved;

\- current operational guidance.



Evidence B:



\- status: DRAFT

\- newer date;

\- intended replacement.



Expected behaviour:



The draft must not automatically override the active document merely because it is newer.



Possible decision:



`REVIEW\_BEFORE\_COMBINATION`



The system should make the lifecycle difference visible.



\---



\## Scenario 3 — Explicit Replacement



Evidence A:



\- active until March;

\- replaced by Evidence B.



Evidence B:



\- effective from 1 April;

\- explicitly replaces Evidence A.



Question date:



15 April.



Expected behaviour:



Evidence B is the current source.



Evidence A may be useful for historical context but must not define current operational guidance.



\---



\## Scenario 4 — Historical Question



Evidence A:



\- active January to March.



Evidence B:



\- active from April.



Question:



“What guidance applied on 10 February?”



Expected behaviour:



Evidence A may legitimately support the answer.



A superseded document is not invalid for historical questions when the requested time falls within its valid period.



This demonstrates:



\*\*superseded does not mean factually unusable in all contexts.\*\*



\---



\## Scenario 5 — Unknown Replacement Relationship



Evidence A:



\- status: SUPERSEDED.



Evidence B:



\- status: ACTIVE.



No explicit metadata confirms whether B replaced A.



Expected behaviour:



The system should not invent the relationship.



Possible outcome:



\- REVIEW\_BEFORE\_COMBINATION;

\- relationship uncertainty recorded;

\- no authoritative synthesis if meaning differs materially.



\---



\## Scenario 6 — Two Active Documents Conflict



Evidence A:



\- ACTIVE

\- approved

\- says escalation may be required.



Evidence B:



\- ACTIVE

\- approved

\- says escalation should not occur.



Expected behaviour:



The system must not assume one outranks the other unless authority metadata supports that conclusion.



Possible precedence:



`BLOCK\_COMBINATION`



or:



`REVIEW\_BEFORE\_COMBINATION`



depending on the existing evidence relationship.



\---



\## Temporal Validity Model



For each source, evaluate whether it is valid relative to the query date.



Suggested states:



\- TEMPORALLY\_VALID

\- TEMPORALLY\_HISTORICAL

\- TEMPORALLY\_EXPIRED

\- FUTURE\_EFFECTIVE

\- TEMPORALLY\_UNKNOWN



\---



\## Example



Query date:



2026-04-15



Document:



\- effective\_date: 2026-01-01

\- superseded\_date: 2026-03-31



Expected temporal status:



`TEMPORALLY\_EXPIRED`



For a February question, the same document could instead be:



`TEMPORALLY\_VALID`



\---



\## Proposed Version Relationship States



Suggested relationship states:



\- CURRENT\_VERSION

\- PREVIOUS\_VERSION

\- EXPLICIT\_REPLACEMENT

\- POSSIBLE\_REPLACEMENT

\- PARALLEL\_ACTIVE

\- HISTORICAL\_ONLY

\- VERSION\_RELATIONSHIP\_UNKNOWN



\---



\## Proposed Precedence Decision Inputs



A future evaluator may receive:



\- evidence\_id;

\- document\_id;

\- version;

\- lifecycle\_status;

\- approval\_status;

\- effective\_date;

\- superseded\_date;

\- replaces\_document\_id;

\- replaced\_by\_document\_id;

\- query\_date;

\- document\_type;

\- source\_authority;

\- conflict\_detected.



\---



\## Safe Combination Rules



Combination may be safe when:



\- sources are temporally valid;

\- lifecycle states are compatible;

\- replacement chains are explicit;

\- no unresolved contradiction exists;

\- the intended claim does not exceed source authority.



\---



\## Review Required Rules



Human review should be required when:



\- an active and draft source differ materially;

\- replacement metadata is ambiguous;

\- multiple active approved documents conflict;

\- query date is missing for a time-sensitive question;

\- effective dates overlap unexpectedly;

\- authority ranking is unknown.



\---



\## Block Combination Rules



Combination should be blocked when:



\- explicit conflicting current guidance exists;

\- superseded wording is used to override active policy;

\- the system would need to invent a replacement relationship;

\- sources are temporally incompatible with the question;

\- unresolved version conflict materially changes operational advice.



\---



\## Interaction With Groundedness



A claim may be textually supported but temporally invalid.



Example:



The claim exactly matches an old policy.



That does not make the claim current.



Therefore:



Groundedness should consider both:



\- textual support;

\- temporal/lifecycle validity.



Possible result:



`TEXTUALLY\_SUPPORTED\_BUT\_TEMPORALLY\_INVALID`



This should not be treated as safe grounded support.



\---



\## Interaction With Governance



Temporal and version reasoning may reduce authority.



Examples:



\- AUTO\_ANSWER + temporal ambiguity → REVIEW\_REQUIRED

\- AUTO\_ANSWER + explicit current conflict → REVIEW\_REQUIRED

\- REVIEW\_REQUIRED + clear temporal support → still REVIEW\_REQUIRED

\- ABSTAIN + valid historical source → still ABSTAIN



Precedence never upgrades governance.



\---



\## Week 26 Benchmark Cases Supported By This Design



This design supports:



\### W26-C004



Superseded + active version chain.



\### W26-C005



Historical evidence incorrectly used as current guidance.



It also provides the basis for later cases involving:



\- overlapping effective periods;

\- draft replacement;

\- multiple active conflicting policies;

\- missing replacement metadata.



\---



\## Implementation Strategy



Do not immediately change the existing Week 25 precedence engine.



Phase the work:



1\. define temporal/version data contract;

2\. create benchmark cases;

3\. implement a Week 26 temporal-precedence evaluator;

4\. compare results with existing precedence decisions;

5\. integrate only after regression testing.



\---



\## Acceptance Criteria



The future implementation should demonstrate that:



1\. newer does not automatically mean authoritative;

2\. active outranks superseded for current questions;

3\. historical questions can legitimately use historical sources;

4\. drafts do not silently replace approved guidance;

5\. ambiguous replacement chains fail closed;

6\. current conflicting guidance remains visible;

7\. temporal invalidity can prevent otherwise textually supported claims from passing;

8\. governance authority is never increased.



\## Status



\*\*Week 26 Day 1 Session 4 COMPLETE\*\*

