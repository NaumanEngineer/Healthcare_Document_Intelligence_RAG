\# Week 26 Day 1 — Relationship-Aware Groundedness Design



\## Objective



Strengthen groundedness evaluation so that a claim cannot be marked supported merely because its words appear somewhere across multiple evidence items.



The evaluator must distinguish between:



\- textual overlap;

\- claim-level support;

\- source-level support;

\- relationship-level support;

\- legitimate evidence composition.



\## Core Principle



> Multiple pieces of evidence do not automatically become one piece of evidence.



\---



\## Problem



The current groundedness approach can evaluate a claim against combined evidence text.



This is useful for basic support detection, but it creates a risk.



A claim may borrow one phrase from Evidence A and another phrase from Evidence B.



If the two sources are not legitimately composable, the combined text may falsely appear to support the claim.



This creates a form of:



\*\*Frankenstein support\*\*



\---



\## Example



Evidence A:



“Escalation may be considered if operational pressure continues.”



Evidence B:



“Elective activity is currently under pressure.”



Unsafe claim:



“Elective activity must be cancelled immediately.”



Words related to:



\- escalation;

\- operational pressure;

\- elective activity



exist somewhere across the evidence set.



However:



\- no source says cancellation is required;

\- no source says action must be immediate;

\- no evidence relationship supports combining these fragments into that conclusion.



The claim must therefore remain unsupported.



\---



\## Relationship-Aware Grounding Model



Groundedness should be evaluated through five layers.



\### Layer 1 — Claim Materiality



Determine whether the claim contains material content requiring evidence.



Examples:



\- numerical statements;

\- operational recommendations;

\- policy requirements;

\- causal statements;

\- role assignments;

\- deadlines;

\- mandatory language.



Non-material formatting or conversational text does not require the same support burden.



\---



\### Layer 2 — Source-Level Support



Evaluate each evidence item independently.



For each claim and evidence item, determine:



\- support strength;

\- high-risk mismatch;

\- missing actor;

\- missing action;

\- missing number;

\- missing temporal condition;

\- missing authority;

\- lifecycle validity.



Possible source-level states:



\- DIRECT\_SUPPORT

\- PARTIAL\_SUPPORT

\- NO\_SUPPORT

\- CONTRADICTS

\- INVALID\_SOURCE



\---



\### Layer 3 — Evidence Relationship



If more than one evidence item is required, determine whether they are legitimately related.



Possible relationship classes:



\- SAME\_DOCUMENT\_CONTEXT

\- EXPLICIT\_SUPPORT\_CHAIN

\- COMPLEMENTARY\_EVIDENCE

\- EXPLICIT\_CONFLICT

\- VERSION\_SUCCESSION

\- UNRELATED

\- UNKNOWN\_RELATIONSHIP



Only approved relationship classes may contribute to multi-source claim support.



\---



\## Safe Composition



Evidence may be combined when:



\- the sources are part of the same approved context;

\- one source explicitly supplements another;

\- the claim explicitly describes a relationship between the sources;

\- Evidence Precedence permits combination;

\- no unresolved conflict changes the meaning of the claim.



\---



\## Unsafe Composition



Evidence must not be combined merely because:



\- retrieved documents share vocabulary;

\- documents appear in the same retrieval result;

\- documents discuss the same broad topic;

\- one contains the actor and another contains the action;

\- one contains a number and another contains a threshold;

\- a semantic embedding score is high.



Retrieval proximity is not evidence of logical composability.



\---



\## Layer 4 — Composite Claim Support



A claim requiring multiple sources should pass only when:



1\. every material component is supported;

2\. each component is linked to an identified evidence item;

3\. the evidence relationship permits composition;

4\. no evidence item contradicts the final claim;

5\. lifecycle and temporal conditions are valid;

6\. governance and precedence do not prohibit the combination.



\---



\## Layer 5 — Final Groundedness Decision



Suggested claim states:



\### GROUNDED\_SINGLE\_SOURCE



One valid evidence item fully supports the material claim.



\### GROUNDED\_MULTI\_SOURCE



Multiple evidence items jointly support the claim through an approved relationship.



\### PARTIALLY\_GROUNDED



Some material claim components are supported, but one or more remain unsupported.



\### UNGROUNDED



No valid evidence configuration supports the material claim.



\### CONFLICT\_BLOCKED



Evidence may individually support elements of the claim, but unresolved conflict prevents safe synthesis.



\### RELATIONSHIP\_UNVERIFIED



Multiple evidence items appear necessary but their relationship is not established.



\### NOT\_APPLICABLE



The claim does not require factual grounding.



\---



\## Required Data Structure



A future relationship-aware groundedness result should include:



\- claim\_id;

\- groundedness\_status;

\- materiality;

\- evidence\_ids\_considered;

\- source\_level\_results;

\- relationship\_result;

\- supported\_components;

\- unsupported\_components;

\- contradictory\_components;

\- lifecycle\_valid;

\- temporal\_valid;

\- composition\_allowed;

\- final\_reason.



\---



\## Example Result — Frankenstein Support



Claim:



“Elective activity must be cancelled immediately.”



Evidence:



\- E1: escalation may be considered;

\- E2: elective activity under pressure.



Expected result:



\- source-level E1: PARTIAL\_SUPPORT

\- source-level E2: PARTIAL\_SUPPORT

\- relationship: UNRELATED or UNKNOWN\_RELATIONSHIP

\- mandatory wording support: missing

\- immediate action support: missing

\- cancellation support: missing

\- composition allowed: false

\- groundedness: UNGROUNDED or RELATIONSHIP\_UNVERIFIED

\- final decision: REVIEW\_REQUIRED



\---



\## Example Result — Legitimate Multi-Source Support



Evidence A:



“Policy A applies to acute sites.”



Evidence B:



“Site X is classified as an acute site.”



Claim:



“Policy A applies to Site X.”



This may be valid multi-source reasoning if:



\- both sources are active;

\- the classification relationship is explicit;

\- no contradictory evidence exists;

\- Evidence Precedence permits the combination.



Expected:



\- relationship: COMPLEMENTARY\_EVIDENCE

\- composition allowed: true

\- groundedness: GROUNDED\_MULTI\_SOURCE



\---



\## Example Result — Conflict-Aware Support



Evidence A:



“Escalation may be required.”



Evidence B:



“Escalation is not recommended.”



Claim:



“The evidence contains conflicting positions on escalation.”



Expected:



\- source support: valid

\- relationship: EXPLICIT\_CONFLICT

\- composition allowed for conflict-description claim: true

\- operational synthesis allowed: false

\- groundedness: GROUNDED\_MULTI\_SOURCE

\- precedence: BLOCK\_COMBINATION



This demonstrates an important distinction:



A claim describing a conflict may be grounded even when operational combination is prohibited.



\---



\## Integration With Existing Architecture



Relationship-aware groundedness should sit after:



\- citation linkage;

\- citation completeness;

\- citation verification;

\- multi-source verification;

\- Evidence Precedence.



Suggested flow:



Question  

→ Evidence Packet  

→ Evidence Precedence  

→ Governance  

→ Answer Contract  

→ Answer Context  

→ Claim-Citation Linkage  

→ Citation Completeness  

→ Citation Verification  

→ Multi-Source Verification  

→ Relationship-Aware Groundedness  

→ Overstatement Audit  

→ Hallucination Resistance  

→ Conflict Coverage  

→ Final Assurance Decision



\---



\## Governance Interaction



Relationship-aware groundedness must never increase authority.



Examples:



\- AUTO\_ANSWER + relationship failure → REVIEW\_REQUIRED

\- REVIEW\_REQUIRED + grounded claim → still REVIEW\_REQUIRED

\- ABSTAIN + grounded fragment → still ABSTAIN



Groundedness determines support.



Governance determines authority.



These are related but separate concepts.



\---



\## Fail-Closed Rules



The evaluator should fail closed when:



\- multi-source support is required but relationship metadata is missing;

\- evidence lifecycle is ambiguous;

\- temporal validity is unresolved;

\- source conflict exists without safe claim framing;

\- support depends on unrelated documents;

\- actor or responsibility support is incomplete;

\- evidence composition is uncertain.



\---



\## Week 26 Implementation Strategy



Do not immediately replace the existing groundedness implementation.



Use a layered evolution:



\### Phase 1



Add relationship-aware evaluation as a separate Week 26 module.



\### Phase 2



Test it against new adversarial benchmark cases.



\### Phase 3



Compare decisions with the existing groundedness audit.



\### Phase 4



Integrate only after regression evidence demonstrates no Week 25 safety regression.



This preserves the existing stable benchmark while enabling controlled hardening.



\---



\## Acceptance Criteria



Relationship-aware groundedness should eventually prove that:



1\. unrelated sources cannot create artificial support;

2\. legitimate complementary sources can support one claim;

3\. explicit conflict remains visible;

4\. version and lifecycle status affect support;

5\. missing relationship metadata fails closed;

6\. multi-source support does not bypass Evidence Precedence;

7\. governance authority is never increased.



\## Status



\*\*Week 26 Day 1 Session 3 COMPLETE\*\*

