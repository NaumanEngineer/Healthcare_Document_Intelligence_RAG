\# Week 22 Day 1 — Structured Evidence Extraction



\## Status



Completed.



\## Objective



Move beyond retrieval-result chunks and create deterministic,

traceable evidence objects suitable for later evidence packets,

governance, audit and manager-facing evidence workflows.



\## Core Design Principle



The evidence layer preserves retrieved source evidence and provenance.



It does not invent:



\- claims

\- summaries

\- confidence values

\- retrieval scores

\- document metadata



\## Evidence Object v1



Each structured evidence object contains:



\- evidence\_id

\- document\_id

\- chunk\_id

\- title

\- document\_type

\- source\_type

\- source\_location

\- source\_file

\- version

\- effective\_date

\- status

\- page

\- chunk\_number

\- evidence\_text

\- extraction\_status

\- ingestion\_batch\_id

\- retrieval\_route

\- evidence\_role

\- retrieval\_scores



Retrieval scores are retained only when actually present.



\## New Modules



\### src/evidence/evidence\_object.py



Creates deterministic evidence objects from retrieval-result chunks.



Important behaviours:



\- required provenance is validated

\- missing provenance fails closed

\- empty evidence text fails closed

\- unsupported evidence roles fail

\- retrieval scores are never invented

\- multiple chunks can be converted consistently



\### src/evidence/evidence\_from\_retrieval.py



Connects Architecture v2 retrieval output to the evidence layer.



Important behaviours:



\- requires valid retrieval results

\- requires valid selected route

\- requires final evidence assessment

\- returns no evidence objects when evidence is insufficient

\- preserves the Architecture v2 retrieval route



\## Real End-to-End Check



Question:



"How should severe weather pressure and ambulance handover disruption be considered together?"



Architecture v2 selected:



BOUNDED\_AGENTIC



Stop reason:



EVIDENCE\_SUFFICIENT\_AFTER\_REFINEMENT



Final evidence became sufficient for:



\- ambulance handover

\- severe weather



Structured evidence objects were created for final retrieved evidence including:



\- DOC-008 Ambulance Handover Escalation Guidance

\- DOC-009 Severe Weather Operational Plan



The evidence objects preserved:



\- document identity

\- lifecycle status

\- source file

\- page

\- chunk ID

\- ingestion batch

\- retrieval route

\- real retrieval scores

\- original evidence text



\## Testing



Evidence object unit tests:



10 passed



Evidence-from-retrieval tests:



5 passed



Full project regression:



556 passed



\## Day 1 Decision



PASS — KEEP



Structured Evidence Object v1 becomes the foundation for Week 22 Day 2 Evidence Packet construction.



\## Next Step



Week 22 Day 2 should combine multiple evidence objects into one

structured Evidence Packet representing the evidence available for

a question.



The packet should distinguish:



\- supporting evidence

\- relationship evidence

\- missing evidence

\- provenance

\- lifecycle state

\- retrieval route

\- governance state



The evidence packet must remain auditable and must not convert

retrieval success into permission to answer.

