\# Week 23 Day 4 — Claim-to-Citation Linking



\## Purpose



Claim-to-Citation Linking makes generated responses auditable at the statement level.



Instead of only recording which documents were used somewhere in the response, the system records which approved evidence supports each substantive claim.



The flow is:



Retrieval

→ Evidence Packet

→ Answer Contract

→ Answer Context

→ Grounded Response

→ Claim-to-Citation Linking



\---



\# Core Principle



> Every substantive claim should be traceable to approved evidence.



The linking layer does not decide whether evidence is trustworthy.



That has already been handled upstream through:



\- evidence sufficiency

\- provenance

\- lifecycle controls

\- evidence precedence

\- governance

\- Answer Contract

\- Answer Context



Its role is traceability.



\---



\# Why This Matters



A response may cite three documents overall but still leave an important question unanswered:



Which document supports which statement?



Claim-level linking solves this.



Example:



Claim:



Bed capacity pressure should be considered alongside escalation and site-flow arrangements.



Support:



E1

DOC-004

Page 2



This is more useful than simply listing DOC-004 at the bottom of the response.



\---



\# Inputs



The linking layer receives:



1\. Grounded Response

2\. Answer Context



The Grounded Response supplies:



\- response type

\- sections

\- evidence-based statements

\- citations used



The Answer Context supplies:



\- approved evidence

\- citation index

\- evidence text

\- source metadata



\---



\# Output



Suggested output fields:



\- linkage\_version

\- packet\_id

\- governance\_decision

\- response\_type

\- claims

\- linkage\_summary

\- unsupported\_claims

\- safety\_summary



Each claim record should contain:



\- claim\_id

\- claim\_text

\- section

\- citation\_ids

\- support\_status



Suggested support statuses:



\- SUPPORTED

\- NON\_SUBSTANTIVE

\- UNSUPPORTED



\---



\# Claim Definition



A substantive claim is a statement that communicates factual or operational information derived from evidence.



Examples:



\- a policy requirement

\- an operational procedure

\- an escalation condition

\- a document-defined relationship

\- an evidence-based management implication



Non-substantive content may include:



\- headings

\- labels

\- safe system-status statements

\- statements that merely explain that human review is required

\- abstention wording



\---



\# AUTO\_ANSWER Behaviour



For AUTO\_ANSWER:



Evidence-based claims should link to one or more approved citation IDs.



Example:



Claim C1



Bed capacity pressure should be reviewed alongside site-flow and escalation arrangements.



Citation:



E1



Support status:



SUPPORTED



\---



\# REVIEW\_REQUIRED Behaviour



For REVIEW\_REQUIRED:



Evidence-summary claims may still be linked to approved evidence.



However, statements explaining that human review is required are governance statements rather than evidence-derived claims.



Those may be labelled:



NON\_SUBSTANTIVE



or otherwise identified as system/governance statements.



The linking layer must not make REVIEW\_REQUIRED appear equivalent to an authoritative answer.



\---



\# ABSTAIN Behaviour



For ABSTAIN:



The response should normally contain no evidence-derived substantive claims.



Statements such as:



The system cannot answer safely from the approved evidence.



are system-status statements.



They should not be falsely linked to evidence.



The linkage layer should preserve abstention rather than trying to manufacture citations.



\---



\# Citation Boundary



Only citation IDs present in the Answer Context may be used.



The linker must not invent:



\- new citation IDs

\- new document IDs

\- new pages

\- new source files



If a claim cannot be supported by approved citations, it should be marked UNSUPPORTED.



\---



\# Evidence Boundary



The linker should only use evidence supplied in the Answer Context.



It must not search external sources.



It must not use model memory.



It must not reconstruct support from rejected retrieval chunks.



\---



\# Fail-Closed Behaviour



The claim-linking layer should fail closed when:



\- packet IDs do not match

\- governance decisions do not match

\- response types do not match

\- the response cites IDs not present in the Answer Context

\- required evidence metadata is missing

\- unsupported claims are incorrectly treated as supported



\---



\# Unsupported Claim Rule



An unsupported material claim is a safety defect.



If the system cannot map a substantive claim to approved evidence:



\- mark it UNSUPPORTED

\- do not silently treat it as grounded

\- expose it for review or removal



This principle will become important when a language model is connected later.



\---



\# Audit Value



Claim-to-citation linking makes it easier to answer:



\- Why did the AI say this?

\- Which source supports this statement?

\- Which page or chunk was used?

\- Was the source current?

\- Was the claim grounded or unsupported?



\---



\# Economic Rationale



Claim-level traceability can reduce:



\- time spent manually checking AI outputs

\- document verification effort

\- audit preparation effort

\- time spent tracing recommendations back to source policy



These savings should be measured in future benchmark work rather than claimed prematurely.



\---



\# NHS Manager Value



A manager should be able to move from:



AI statement



to:



supporting evidence



without having to repeat the entire search process manually.



This increases:



\- transparency

\- confidence

\- auditability

\- review speed

\- accountability



\---



\# Week 23 Day 4 Principle



> A trustworthy answer should not only cite sources; it should show which source supports which claim.
