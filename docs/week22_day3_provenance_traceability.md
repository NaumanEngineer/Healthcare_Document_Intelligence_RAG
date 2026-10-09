\# Week 22 Day 3 — Provenance \& Evidence Traceability



\## Status



Completed.



\## Objective



Strengthen evidence traceability so that every evidence item can be

linked back to its source document, version, lifecycle state, page,

chunk, ingestion run, retrieval route and evidence role.



The provenance layer must verify evidence metadata rather than merely

store it.



\## Core Principle



Evidence provenance should answer:



\- Where did this evidence come from?

\- Which document produced it?

\- Which document version was used?

\- What lifecycle status did the document have?

\- Which page and chunk produced the evidence?

\- Which ingestion run created the chunk?

\- Which retrieval route selected it?

\- What evidence role does it serve?

\- Does its metadata match the canonical document register?



\## Existing Foundation



The project already had:



\- canonical document metadata

\- document lifecycle states

\- source location

\- source file

\- document version

\- effective date

\- ingestion batch identifiers

\- page and chunk identifiers

\- Active-only normal retrieval

\- structured evidence objects



Day 3 added explicit provenance verification on top of that foundation.



\## New Module



\### src/evidence/provenance.py



The provenance module builds a compact trace record for each evidence

object.



Each record contains:



\- evidence\_id

\- document\_id

\- chunk\_id

\- source

&#x20; - title

&#x20; - document\_type

&#x20; - source\_type

&#x20; - source\_location

&#x20; - source\_file

\- document\_lifecycle

&#x20; - version

&#x20; - effective\_date

&#x20; - status

\- location

&#x20; - page

&#x20; - chunk\_number

\- lineage

&#x20; - ingestion\_batch\_id

&#x20; - retrieval\_route

&#x20; - evidence\_role

\- traceability

&#x20; - traceability\_status

&#x20; - canonical\_document\_registered

&#x20; - canonical\_metadata\_match

&#x20; - metadata\_mismatches



\## Traceability States



Three traceability states are supported:



\### VERIFIED



The evidence document is registered and all canonical metadata matches.



\### MISMATCH



The document is registered but one or more metadata fields do not match

the canonical document register.



Examples:



\- wrong version

\- wrong lifecycle status

\- wrong source file

\- wrong source location



\### UNREGISTERED



The evidence refers to a document that is not present in the canonical

document register.



\## Fail-Closed Behaviour



The provenance layer fails when important lineage information is absent

or invalid.



Required provenance includes:



\- evidence\_id

\- document\_id

\- chunk\_id

\- source metadata

\- document lifecycle

\- page

\- chunk number

\- ingestion batch

\- retrieval route

\- evidence role



Invalid page or chunk values also fail validation.



\## Evidence Packet Integration



The Evidence Packet now automatically contains:



\- full provenance records

\- provenance\_summary



This means evidence traceability becomes part of the question-level

audit object rather than remaining disconnected from retrieval.



\## Provenance Summary



The packet-level provenance summary contains:



\- record\_count

\- VERIFIED count

\- MISMATCH count

\- UNREGISTERED count

\- all\_verified

\- mismatch\_evidence\_ids

\- unregistered\_evidence\_ids



This allows a reviewer to understand provenance quality without reading

every evidence record manually.



\## Real End-to-End Check



Question:



"How should severe weather pressure and ambulance handover disruption

be considered together?"



Architecture v2 result:



\- route: BOUNDED\_AGENTIC

\- evidence count: 3

\- DOC-008 page 1

\- DOC-008 page 2

\- DOC-009 page 2



Provenance result:



\- record count: 3

\- VERIFIED: 3

\- MISMATCH: 0

\- UNREGISTERED: 0

\- all\_verified: true



All evidence matched the canonical document register.



\## Governance Preservation



Successful provenance verification does not grant permission to answer.



For the real Q027 case:



\- evidence sufficiency: SUFFICIENT

\- provenance: VERIFIED

\- governance: REVIEW\_REQUIRED

\- human review required: true

\- may\_generate\_answer: false



This preserves the separation between:



retrieval quality



and



operational decision authority.



\## Testing



New provenance tests:



10 passed



New provenance-summary tests:



5 passed



Existing Evidence Packet tests:



9 passed



Full project regression:



580 passed



\## Day 3 Decision



PASS — KEEP



Provenance Record v1 and provenance\_summary become part of the working

Evidence Packet architecture.



\## Architecture After Day 3



Question

→ Architecture v2 Retrieval

→ Evidence Sufficiency

→ Structured Evidence Objects

→ Provenance Verification

→ Evidence Packet

→ Provenance Summary

→ Governance

→ Human Review / Safe Outcome



\## Next Step



Week 22 Day 4 should focus on:



Contradiction, Supersession and Precedence Handling.



The system should determine when retrieved documents:



\- contradict one another

\- refer to different lifecycle states

\- contain superseded guidance

\- require precedence rules

\- should be blocked from unsafe combination



The assurance layer must remain authoritative.

