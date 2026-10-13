\# Week 23 Day 5 — Review and Abstention UX



\## Purpose



Review and Abstention UX turns safe system states into useful manager-facing responses.



The system already knows how to:



\- retrieve evidence

\- assess evidence

\- preserve provenance

\- assess lifecycle

\- assess precedence

\- make governance decisions

\- build an Answer Contract

\- build governed Answer Context

\- produce a grounded response

\- link claims to citations



Day 5 focuses on how REVIEW\_REQUIRED and ABSTAIN should be communicated to a manager.



\---



\# Core Principle



> Safe refusal should still be operationally useful.



The system should not merely block an answer.



It should help the user understand:



\- why the answer was not automated

\- what evidence was found

\- what remains uncertain

\- what a human reviewer should check

\- what additional evidence would allow the process to continue



\---



\# REVIEW\_REQUIRED



REVIEW\_REQUIRED means:



\- relevant evidence exists

\- the system has not granted automated authority

\- a human should inspect the evidence before a final decision is made



The UX should make this obvious.



It must not make review look optional.



\---



\# REVIEW\_REQUIRED Manager View



Suggested fields:



\- status

\- headline

\- evidence\_summary

\- why\_review\_is\_required

\- review\_focus

\- uncertainty

\- sources

\- next\_action



Example:



Status:



Human review required



Headline:



Relevant approved evidence was found, but the system is not authorised to issue a final operational recommendation.



Evidence summary:



\- E1 — Ambulance handover guidance

\- E2 — Ambulance escalation response

\- E3 — Severe weather plan



Review focus:



Consider whether the evidence can be applied together in the current operational situation.



Next action:



A responsible operational manager should review the cited evidence before making the final decision.



\---



\# ABSTAIN



ABSTAIN means:



\- the system cannot safely produce a substantive answer

\- evidence may be missing

\- the question may be outside scope

\- evidence may be insufficient

\- the system must not fill the gap from model memory



The UX should explain this clearly without sounding like a technical error.



\---



\# ABSTAIN Manager View



Suggested fields:



\- status

\- headline

\- why\_no\_answer

\- missing\_information

\- what\_would\_allow\_progress

\- safe\_next\_action



Example:



Status:



Unable to answer safely



Headline:



The approved evidence base does not contain enough information to answer this question safely.



Missing information:



\- approved cyber-security incident procedure



What would allow progress:



Add or approve a relevant cyber-security procedure within the governed evidence base.



Safe next action:



Escalate the question to the appropriate operational or information-governance owner.



\---



\# Human Review Must Be Visible



For REVIEW\_REQUIRED:



The phrase human review required should be prominent.



The system must not:



\- bury the review requirement at the bottom

\- present a recommendation first and warning second

\- describe review as optional

\- use wording that implies automated approval



\---



\# Abstention Must Not Leak an Answer



For ABSTAIN:



The system must not:



\- provide speculative guidance

\- offer a likely answer

\- reconstruct an answer from general knowledge

\- give uncited operational instructions

\- present rejected evidence as useful guidance



The response should stay within:



\- reason for abstention

\- missing evidence

\- what is needed next

\- safe escalation path



\---



\# Evidence Visibility



For REVIEW\_REQUIRED:



Approved evidence should remain visible.



The manager should be able to see:



\- citation ID

\- document

\- page or chunk

\- evidence summary



For ABSTAIN:



Substantive evidence should normally remain absent unless needed purely to explain the abstention state.



\---



\# Review Focus



The review UX should direct the human reviewer toward the actual unresolved issue.



Possible review-focus topics include:



\- evidence conflict

\- evidence precedence

\- lifecycle risk

\- incomplete evidence

\- combined operational judgement

\- question ambiguity

\- policy applicability



The system should not invent a review reason that was not present upstream.



\---



\# Uncertainty Visibility



Uncertainty should be explicit.



Examples:



\- missing evidence topics

\- unsupported claims

\- unresolved evidence gaps

\- precedence requiring review



Uncertainty should not be converted into confident prose.



\---



\# Next-Action Principle



Every blocked response should still answer:



> What should happen next?



For REVIEW\_REQUIRED:



The next step is human assessment of the evidence.



For ABSTAIN:



The next step is usually:



\- obtain missing approved evidence

\- clarify scope

\- route to the appropriate owner

\- or reformulate the question



\---



\# Manager Language



The UX should avoid unnecessary technical terminology.



Instead of:



Governance state = REVIEW\_REQUIRED



Prefer:



Human review required



Instead of:



Insufficient retrieval evidence



Prefer:



The approved evidence base does not contain enough information to answer safely.



Technical metadata should remain available for audit but should not dominate the manager-facing message.



\---



\# Fail-Closed Behaviour



The UX formatter should fail closed when:



\- governance and response type disagree

\- REVIEW\_REQUIRED lacks human-review status

\- ABSTAIN contains substantive evidence

\- unknown citations are present

\- packet identity does not match upstream components

\- unsupported response states are supplied



\---



\# Economic Rationale



Good review and abstention UX can reduce:



\- wasted manager time

\- repeated searches

\- unclear escalation

\- unnecessary AI retries

\- time spent determining what evidence is missing



Future benchmarking can measure:



\- time to resolve a review case

\- time to identify missing evidence

\- number of unnecessary follow-up queries

\- manager review completion time

\- escalation turnaround time



\---



\# NHS Manager Value



A trustworthy system should not force a manager to choose between:



\- unsafe automation

\- or a useless refusal



The better option is:



> safe, transparent decision support that tells the manager what is known, what is uncertain, and what to do next.



\---



\# Week 23 Day 5 Principle



> When automation stops, useful decision support should continue.
