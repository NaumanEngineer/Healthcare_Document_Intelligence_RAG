\# Week 23 Day 1 — Answer Contract



\## Purpose



The Answer Contract defines what the system is permitted to communicate after retrieval, evidence assessment and governance have already completed.



The contract does not decide whether evidence is sufficient.



The contract does not decide whether a question is in scope.



The contract does not override governance.



Its role is to translate an existing governance decision into a controlled response format.



\---



\## Governing Principle



> Governance decides permission. The generator only formats permitted content.



The answer-generation layer must never upgrade a governance decision.



Examples:



\- ABSTAIN must never become AUTO\_ANSWER

\- REVIEW\_REQUIRED must never become an authoritative recommendation

\- insufficient evidence must never be presented as sufficient evidence

\- unsafe or unverified evidence must not be presented as approved evidence



\---



\## Input



The Answer Contract receives a question-level Evidence Packet.



Relevant packet fields include:



\- packet\_id

\- question

\- evidence\_sufficiency

\- evidence

\- evidence\_count

\- document\_ids

\- provenance

\- provenance\_summary

\- precedence\_assessment

\- missing\_evidence

\- lifecycle\_summary

\- governance

\- audit\_summary



The Answer Contract must use the existing governance decision as authoritative.



\---



\## Governance States



The supported governance states are:



\- AUTO\_ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



No other governance state is valid.



Unsupported governance states must fail closed.



\---



\# AUTO\_ANSWER Contract



\## Purpose



AUTO\_ANSWER permits the system to produce a grounded management-facing answer using only the approved evidence.



\## Allowed Sections



The response may contain:



1\. Management Summary

2\. Evidence-Based Explanation

3\. Operational Implication

4\. Caveats

5\. Sources



\## Allowed Behaviour



The generator may:



\- summarise approved evidence

\- combine evidence where precedence assessment permits

\- explain operational meaning

\- cite exact evidence

\- present relevant caveats

\- use concise manager-friendly language



\## Prohibited Behaviour



The generator must not:



\- invent new facts

\- introduce uncited material claims

\- use external knowledge unless explicitly permitted by a separate future mechanism

\- present Draft, Superseded or Archived evidence as current authority

\- override precedence controls

\- override governance

\- hide uncertainty

\- create unsupported recommendations



\---



\# REVIEW\_REQUIRED Contract



\## Purpose



REVIEW\_REQUIRED means evidence exists, but human judgement is required before an authoritative answer can be given.



\## Allowed Sections



The response may contain:



1\. Evidence Summary

2\. Why Human Review Is Required

3\. Review Focus

4\. Evidence Gaps or Uncertainty

5\. Sources



\## Allowed Behaviour



The generator may:



\- summarise the available evidence

\- identify the reason review is required

\- identify issues a reviewer should consider

\- show relevant source evidence

\- describe unresolved uncertainty



\## Prohibited Behaviour



The generator must not:



\- make the final operational decision

\- issue an authoritative recommendation

\- imply that review is optional

\- present unresolved evidence as settled fact

\- upgrade the case to AUTO\_ANSWER



\---



\# ABSTAIN Contract



\## Purpose



ABSTAIN means the system is not permitted to provide a substantive answer.



\## Allowed Sections



The response may contain:



1\. Unable to Answer Safely

2\. Reason

3\. Missing Evidence

4\. What Is Needed to Continue



\## Allowed Behaviour



The system may explain:



\- why the question cannot be answered safely

\- whether the issue is out of scope

\- whether evidence is insufficient

\- what evidence would be needed

\- whether a human or external process is required



\## Prohibited Behaviour



The system must not:



\- provide a hidden answer inside the explanation

\- speculate

\- invent missing evidence

\- produce an operational recommendation

\- present weak evidence as sufficient

\- silently answer from model memory



\---



\# Monotonic Safety Rule



The answer layer must preserve or reduce automation authority.



It must never increase authority.



Allowed transitions:



\- AUTO\_ANSWER → AUTO\_ANSWER

\- AUTO\_ANSWER → REVIEW\_REQUIRED

\- AUTO\_ANSWER → ABSTAIN

\- REVIEW\_REQUIRED → REVIEW\_REQUIRED

\- REVIEW\_REQUIRED → ABSTAIN

\- ABSTAIN → ABSTAIN



Forbidden transitions:



\- REVIEW\_REQUIRED → AUTO\_ANSWER

\- ABSTAIN → REVIEW\_REQUIRED

\- ABSTAIN → AUTO\_ANSWER



\---



\# Citation Rule



Any material factual claim in an AUTO\_ANSWER or REVIEW\_REQUIRED response must be traceable to approved evidence.



At minimum, the answer layer should preserve:



\- evidence\_id

\- document\_id

\- chunk\_id

\- page

\- source\_file

\- version

\- status



A claim without supporting approved evidence must not be presented as established fact.



\---



\# Provenance Rule



Evidence used in a normal answer should be provenance-verified.



If provenance is mismatched or unregistered, the answer layer must not silently proceed as if the evidence were verified.



Such cases should remain reviewable or unavailable according to governance.



\---



\# Lifecycle Rule



Current authoritative answers must not rely on Draft, Superseded or Archived evidence as if those documents were Active.



Lifecycle state must remain visible to the answer layer.



\---



\# Precedence Rule



Evidence may only be combined automatically when the evidence precedence layer permits it.



SAFE\_TO\_COMBINE does not itself grant answer permission.



Governance remains authoritative.



\---



\# Structured Output Goal



Future generation code should return a structured object rather than free-form text only.



Example fields:



\- answer\_contract\_version

\- packet\_id

\- governance\_decision

\- response\_type

\- response\_sections

\- citations

\- requires\_human\_review

\- may\_generate\_answer

\- safety\_notes



\---



\# Failure Behaviour



The Answer Contract must fail closed when:



\- the governance object is missing

\- the governance decision is unsupported

\- required packet fields are malformed

\- answer permission is inconsistent

\- evidence required for a response is unavailable



Fail-closed behaviour should result in either:



\- REVIEW\_REQUIRED

\- ABSTAIN



depending on the existing governance state.



\---



\# NHS Manager Interpretation



The goal is not to make the AI sound confident.



The goal is to make the AI useful without hiding the evidence or governance state.



A manager should be able to understand:



\- what the system knows

\- what evidence supports it

\- what the system does not know

\- whether human review is required

\- what action or evidence is needed next



\---



\# Week 23 Day 1 Principle



> A trustworthy AI answer is not just well-written text. It is a permitted, evidence-grounded communication produced inside a defined governance contract.
