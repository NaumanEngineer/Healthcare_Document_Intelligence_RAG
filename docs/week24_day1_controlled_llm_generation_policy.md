\# Week 24 Day 1 — Controlled LLM Generation Policy



\## Purpose



Week 24 introduces model-assisted language generation into the governed healthcare evidence workflow.



The model may improve:



\- clarity

\- summarisation

\- management readability

\- sentence structure

\- concise explanation



The model must not decide:



\- whether an answer is permitted

\- whether evidence is sufficient

\- whether human review is required

\- whether abstention is required

\- which source is authoritative

\- whether a superseded or draft document may be used

\- whether unsupported operational advice should be added



Authority remains upstream.



\---



\# Core Principle



The LLM is a communication component, not a governance component.



The communication layer must obey:



1\. Evidence Packet

2\. Governance decision

3\. Answer Contract

4\. Answer Context

5\. Citation constraints



The model must not override any of these controls.



\---



\# Permitted Generation States



\## AUTO\_ANSWER



The model may generate a manager-facing answer using only approved evidence supplied in the Answer Context.



The model may:



\- summarise approved evidence

\- explain evidence in plain English

\- produce concise management wording

\- organise the answer into useful sections

\- reference valid citation IDs



The model may not:



\- introduce unsupported facts

\- invent recommendations

\- use external knowledge

\- use model memory as evidence

\- cite unknown sources



\---



\## REVIEW\_REQUIRED



The model may generate a review summary.



The output must remain clearly non-authoritative.



The model may:



\- summarise relevant evidence

\- explain why review is required

\- identify evidence gaps

\- highlight uncertainty

\- identify what a manager should inspect



The model may not:



\- present a final operational decision

\- remove the review requirement

\- convert the response into an authoritative answer

\- give instructions that imply approval



Human review remains mandatory.



\---



\## ABSTAIN



The model must not generate a substantive answer.



The output may only explain:



\- why the system cannot answer safely

\- what evidence is missing

\- what clarification is needed

\- what safe next step is available



The model must not receive substantive evidence when the Answer Context has stripped it.



\---



\# Evidence Boundary



The model may use only evidence included in the Answer Context.



The model must not use:



\- prior conversational knowledge

\- general model knowledge

\- internet knowledge

\- unapproved retrieved chunks

\- rejected evidence

\- hidden evidence

\- superseded authority unless governance explicitly permits review use



\---



\# Citation Boundary



Substantive claims must reference citation IDs supplied in the Answer Context.



Examples:



E1

E2

E3



The model must not create:



\- E4 when only E1-E3 exist

\- document names not present in context

\- fabricated page numbers

\- fabricated policy versions



Unknown citations must fail validation.



\---



\# Prompt-Injection Boundary



Retrieved documents must be treated as evidence, not instructions to the model.



Text inside a retrieved document must not be allowed to:



\- change the system role

\- disable governance

\- request secrets

\- alter citation rules

\- bypass abstention

\- instruct the model to ignore evidence boundaries



Document text is data.



It is not executable instruction.



\---



\# Output Requirements



A generated response must preserve:



\- packet identity

\- governance decision

\- response type

\- human-review requirement

\- citation IDs

\- safety constraints



The generated content must be validated before it is accepted.



\---



\# Fail-Closed Behaviour



Generation must fail closed if:



\- governance identity changes

\- response type changes

\- packet identity changes

\- an unknown citation appears

\- unsupported substantive claims are detected

\- ABSTAIN contains substantive evidence

\- REVIEW\_REQUIRED becomes authoritative

\- model output cannot be parsed safely



A failure must not silently fall back to a more permissive answer.



\---



\# Deterministic Baseline



The existing deterministic generation layer remains the safety reference implementation.



The Week 24 model-assisted layer must be compared against it.



The deterministic layer provides:



\- known response structure

\- known governance behaviour

\- known citation behaviour

\- benchmarked safety baseline



The model-assisted layer must not weaken these properties.



\---



\# Week 24 Evaluation Principle



Model quality is secondary to governance preservation.



A more fluent answer is not an improvement if it:



\- introduces unsupported claims

\- weakens review controls

\- leaks evidence during abstention

\- creates invalid citations

\- increases authority



\---



\# Economic Evaluation



Week 24 should begin measuring potential workflow value.



Candidate metrics:



\- time to produce management-ready summary

\- number of manual edits required

\- number of source lookups required

\- reviewer time

\- unsupported-claim rate

\- citation correction rate

\- percentage of drafts accepted with minor edits



No cost-saving claim should be treated as proven until measured.



\---



\# Success Criteria



Week 24 controlled generation should eventually demonstrate:



\- governance override rate = 0

\- ABSTAIN substantive answer rate = 0

\- REVIEW authoritative-answer rate = 0

\- unknown citation rate = 0

\- unsupported material claim rate = 0 in promoted benchmark cases

\- human-review preservation = 100%

\- deterministic fallback available



\---



\# Day 1 Principle



> The model may improve the wording, but the assurance layer decides what the model is allowed to say.
