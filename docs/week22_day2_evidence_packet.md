\# Week 22 Day 2 — Evidence Packet Builder



\## Status



Completed.



\## Objective



Combine Architecture v2 retrieval outputs, structured evidence,

evidence sufficiency, lifecycle state, provenance and governance

into one deterministic question-level Evidence Packet.



\## Core Principle



The Evidence Packet is an audit structure.



It does not:



\- create new facts

\- generate claims

\- make new retrieval decisions

\- replace evidence sufficiency

\- replace governance

\- grant permission to answer



Existing Architecture v2 retrieval and governance controls remain authoritative.



\## Evidence Packet v1



The packet contains:



\- packet\_id

\- question

\- retrieval

&#x20; - route

&#x20; - stop\_reason

&#x20; - scope

\- evidence\_sufficiency

\- evidence

&#x20; - supporting

&#x20; - relationship\_evidence

&#x20; - context

\- evidence\_count

\- document\_ids

\- missing\_evidence

&#x20; - initial\_missing\_topics

&#x20; - final\_missing\_topics

&#x20; - unsupported\_claims

\- lifecycle\_summary

\- governance

\- audit\_summary



\## New Module



\### src/evidence/evidence\_packet.py



Builds one deterministic Evidence Packet from:



\- question

\- Architecture v2 retrieval output

\- Day 1 evidence objects

\- existing retrieval-governance bridge



\## Important Safety Design



The packet calls the existing governance integration:



`decide\_retrieval\_governance\_outcome()`



Therefore:



Evidence Packet != governance engine



The packet records the authoritative governance outcome.



\## Initial Gap vs Final Missing Evidence



A bug was identified during the real Q027 check.



The first implementation copied:



`routing\_decision.missing\_topics`



directly into the final missing-evidence field.



This was incorrect because routing diagnosis describes the initial

retrieval gap before bounded recovery.



The corrected design separates:



\### Initial diagnosed gap



Example:



\- severe\_weather



\### Final unresolved gap



Example after successful recovery:



\- none



This preserves the retrieval reasoning history without incorrectly

reporting recovered evidence as still missing.



\## Real End-to-End Check



Question:



"How should severe weather pressure and ambulance handover disruption be considered together?"



Architecture v2:



\- route: BOUNDED\_AGENTIC

\- stop reason: EVIDENCE\_SUFFICIENT\_AFTER\_REFINEMENT

\- evidence count: 3

\- document IDs:

&#x20; - DOC-008

&#x20; - DOC-009



Lifecycle:



\- Active evidence: 3

\- all\_active: true



Initial missing topic:



\- severe\_weather



Final missing topics:



\- none



Governance:



\- REVIEW\_REQUIRED

\- requires\_human\_review: true

\- may\_generate\_answer: false



The packet therefore records that Architecture v2 recovered the missing

severe-weather evidence but still requires human review because the

question involves cross-document / multi-domain reasoning.



\## Testing



Evidence Packet tests:



9 passed



Full project regression:



565 passed



\## Day 2 Decision



PASS — KEEP



Evidence Packet v1 becomes the structured evidence container for later

Week 22 provenance, relationship and manager-facing evidence workflows.



\## Next Step



Week 22 Day 3 should strengthen provenance and evidence traceability.



Priority areas:



\- document identity

\- source location

\- version

\- lifecycle status

\- page

\- chunk

\- ingestion batch

\- retrieval route

\- evidence role

\- relationship provenance

\- audit lineage



No important evidence item should exist without traceable provenance.

