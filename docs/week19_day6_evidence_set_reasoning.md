\# Week 19 Day 6 — Evidence-Set Reasoning and Corrective False-Premise Handling



\## Objective



Add a separate governance layer for questions that assume relationships between multiple policies.



The existing citation verifier is designed primarily for:



claim → cited evidence → support



Day 6 addressed a different problem:



claim → multiple documents → relationship between documents



\---



\## Problem



A user may ask:



"Which policy takes precedence in the conflict between DOC-003 and DOC-011?"



The wording assumes that a conflict exists.



A safe system should not automatically accept that premise.



It should first ask:



\- do the supplied documents explicitly conflict?

\- does one replace the other?

\- does one take precedence?

\- do they complement each other?

\- is the relationship actually established by the evidence?



\---



\## Evidence-Set Relationship Validator



Implemented:



`src/governance/evidence\_set\_relationship.py`



Supported relationship types:



\- CONFLICT

\- COMPLEMENTS

\- REPLACES

\- TAKES\_PRECEDENCE



Possible outcomes:



\- RELATIONSHIP\_SUPPORTED

\- RELATIONSHIP\_NOT\_ESTABLISHED

\- REVIEW\_REQUIRED



\---



\## Lifecycle Protection



Relationship reasoning requires lifecycle-safe evidence.



Draft, Superseded, Archived, or unconfirmed-status evidence cannot automatically establish an authoritative relationship.



These cases are routed to:



`REVIEW\_REQUIRED`



\---



\## Corrective False-Premise Validation



Implemented:



`src/governance/corrective\_false\_premise.py`



This layer supports carefully worded corrective statements when an alleged relationship is not established.



Example:



"The available evidence does not establish that DOC-003 and DOC-011 conflict."



Important limitation:



This does not prove that no conflict can exist.



It only states that the supplied evidence does not establish the alleged relationship.



\---



\## Validation



Evidence-set relationship tests:

\- 10 passed



Corrective false-premise tests:

\- 8 passed



Combined relationship/correction tests:

\- 18 passed



Full project regression:

\- 338 tests passed



\---



\## Key Engineering Principle



The system should verify the premise of a question before reasoning from it.



A user's wording must not be treated as evidence.



\---



\## NHS Relevance



In operational healthcare settings, an AI system may be asked to interpret several procedures at once.



Incorrectly inventing:

\- a conflict;

\- a precedence rule;

\- a replacement relationship;

\- or a prohibition



could lead to the wrong procedure being followed.



Evidence-set reasoning reduces this risk by separating:



user allegation



from



documented policy relationship



\---



\## Current Architecture



Question

→ Scope Gate

→ Retrieval

→ Evidence Sufficiency

→ Pre-generation Governance

→ Answer Generation

→ Citation Verification

→ High-Risk Claim Guard

→ Guarded Semantic Rescue

→ Evidence-Set Relationship Validation

→ Corrective False-Premise Validation

→ Post-generation Governance



\---



\## Current Status



Day 6 evidence-set reasoning implemented.



Full regression:

\- 338 tests passed



\---



\## Next Priority



Integrate the relationship/corrective validation into a realistic end-to-end answer flow and benchmark the complete governed assistant rather than isolated modules.

