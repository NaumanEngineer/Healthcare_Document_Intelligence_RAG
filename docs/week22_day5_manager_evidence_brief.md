\# Week 22 Day 5 — Manager-Ready Evidence Brief



\## Objective



Create a concise, deterministic, manager-facing evidence brief from the existing Week 22 Evidence Packet.



The brief is designed to answer five operational questions:



1\. What is the question?

2\. What evidence was found?

3\. Is the evidence current and traceable?

4\. Is it safe to combine?

5\. What action is allowed now?



The brief does not create new facts.



It does not override retrieval, evidence sufficiency, provenance, lifecycle controls, precedence assessment or governance.



The Evidence Packet remains the source of truth.



\---



\## New Module



Created:



`src/evidence/manager\_evidence\_brief.py`



The module converts one Evidence Packet into a compact manager-facing structure.



It introduces three brief states:



\### `BRIEF\_READY`



Evidence is sufficient and the current assurance/governance controls do not require human review.



\### `BRIEF\_REVIEW\_REQUIRED`



Evidence exists and may be useful, but human review is still required.



This can occur when:



\- governance requires review;

\- evidence combination requires review;

\- an explicit conflict blocks automatic combination.



\### `BRIEF\_UNAVAILABLE`



The system does not have sufficient evidence to produce a usable manager brief.



This protects against producing confident-looking summaries from missing or insufficient evidence.



\---



\## Brief Structure



The Manager Evidence Brief contains:



\- brief version;

\- Evidence Packet ID;

\- operational question;

\- brief status;

\- document summary;

\- evidence summary;

\- assurance summary;

\- governance summary;

\- deterministic manager action.



\---



\## Document Summary



The brief preserves:



\- document count;

\- document IDs.



This allows a manager or reviewer to see which documents contributed to the evidence set without opening the full technical packet immediately.



\---



\## Evidence Summary



The brief includes:



\- evidence object count;

\- evidence sufficiency;

\- sufficiency reason;

\- unresolved final missing topics;

\- unsupported claims.



The brief therefore distinguishes between evidence that was initially missing and evidence that remains unresolved after retrieval enhancement.



\---



\## Assurance Summary



The brief exposes:



\- whether provenance is fully verified;

\- whether all evidence is Active;

\- the precedence decision;

\- the precedence reason.



This gives the manager a compact view of whether the evidence is current, traceable and safe to combine.



\---



\## Governance Summary



The existing governance decision remains authoritative.



The brief preserves:



\- governance decision;

\- whether human review is required;

\- whether answer generation is allowed;

\- governance reason.



The Manager Evidence Brief does not upgrade a `REVIEW\_REQUIRED` or `ABSTAIN` decision.



\---



\## Manager Action



The manager action is deterministic.



Examples:



\### Insufficient evidence



The manager is told not to rely on the evidence set and that additional or more suitable evidence is required.



\### Explicit conflict



The manager is told not to combine the evidence automatically and that a human reviewer must resolve the conflict.



\### Human review required



The brief is labelled for review use only.



\### Controlled next step allowed



The brief states that the evidence is suitable for the next controlled workflow step, subject to organisational governance.



\---



\## Testing



Created:



`tests/test\_manager\_evidence\_brief.py`



Coverage includes:



1\. ready brief;

2\. governance review requirement;

3\. precedence review requirement;

4\. blocked evidence combination;

5\. insufficient evidence;

6\. zero evidence objects;

7\. document ID preservation;

8\. missing-topic preservation;

9\. unsupported-claim preservation;

10\. blank packet ID;

11\. blank question;

12\. invalid packet type.



Result:



`12 passed`



\---



\## Real Q027 Validation



Created:



`src/evaluation/check\_week22\_day5\_manager\_brief.py`



Question:



> How should severe weather pressure and ambulance handover disruption be considered together?



The real Architecture v2 pipeline produced:



\- route: `BOUNDED\_AGENTIC`;

\- evidence count: `3`;

\- documents:

&#x20; - DOC-008

&#x20; - DOC-009;

\- evidence sufficient: `True`;

\- final missing topics: none;

\- unsupported claims: none;

\- provenance verified: `True`;

\- all evidence Active: `True`;

\- precedence decision: `SAFE\_TO\_COMBINE`;

\- governance decision: `REVIEW\_REQUIRED`;

\- human review required: `True`;

\- answer generation allowed: `False`.



The resulting brief state was:



`BRIEF\_REVIEW\_REQUIRED`



The manager action was:



Use the brief as review material only and require human assessment before operational use.



\---



\## Interpretation



The Q027 result demonstrates an important architectural separation.



The system can determine that:



\- the evidence is sufficient;

\- the evidence is traceable;

\- the evidence is current;

\- the evidence can be combined safely at the evidence-set level;



while still concluding that:



\- autonomous answer generation is not allowed;

\- human review is required.



This prevents evidence quality from being confused with decision authority.



\---



\## NHS Manager Interpretation



For a non-technical NHS manager, the Evidence Packet is the detailed technical record.



The Manager Evidence Brief is the executive front page.



Instead of exposing retrieval scores, chunk metadata and audit details first, the manager sees:



\- what evidence was found;

\- whether it is current;

\- whether it is traceable;

\- whether documents conflict;

\- whether human review is required;

\- what the safe next action is.



The technical Evidence Packet remains available underneath for audit and assurance.



\---



\## Full Regression



Full project regression after Day 5:



`604 passed`



Previous Day 4 baseline:



`592 passed`



No regression was introduced.



\---



\## Architecture After Day 5



Question  

→ Scope Gate  

→ Architecture v2 Retrieval  

→ Evidence Sufficiency  

→ Structured Evidence  

→ Provenance Verification  

→ Lifecycle Assurance  

→ Conflict / Supersession / Precedence Assessment  

→ Governance  

→ Evidence Packet  

→ Manager Evidence Brief  

→ Human Review / Controlled Next Step / Abstention



\---



\## Safety Boundary



Manager Evidence Brief v1 is not a generative executive summary.



It does not paraphrase or synthesize document content into new management recommendations.



It organizes already validated Evidence Packet information into a manager-readable assurance format.



This keeps the first version deterministic and auditable.



A later layer may introduce grounded narrative generation, but only behind the existing evidence and governance controls.



\---



\## Decision



\*\*PASS — KEEP\*\*



Manager Evidence Brief v1 becomes part of the Week 22 evidence workflow.



Day 6 can now evaluate and package the full Week 22 architecture for portfolio use.

