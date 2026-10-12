\# Week 23 Day 3 — Grounded Answer Generation



\## Purpose



Grounded Answer Generation converts the governed Answer Context into a manager-readable response.



It sits after:



Retrieval

→ Evidence Packet

→ Answer Contract

→ Answer Context

→ Grounded Answer Generator



The generator must not independently decide:



\- whether the question is answerable

\- whether evidence is sufficient

\- whether evidence may be combined

\- whether human review is required

\- whether governance may be overridden

\- whether lifecycle-risk evidence should be treated as current authority



Those decisions are already made upstream.



\---



\# Core Principle



> Generation may express approved evidence, but it may not create new authority.



The generator is a communication layer.



It is not a governance engine.



It is not a retrieval engine.



It is not an evidence adjudicator.



\---



\# Inputs



The grounded generator receives:



1\. Answer Contract

2\. Answer Context



The Answer Contract defines:



\- governance decision

\- response type

\- permitted sections

\- generation permission

\- human-review requirement



The Answer Context defines:



\- question

\- approved evidence

\- stable citations

\- uncertainty

\- precedence state

\- safety constraints



\---



\# Output



The generator should return a structured response object.



Suggested fields:



\- response\_version

\- packet\_id

\- governance\_decision

\- response\_type

\- generation\_status

\- requires\_human\_review

\- sections

\- citations\_used

\- safety\_summary



\---



\# Generation Status



Suggested generation statuses:



\- GENERATED

\- REVIEW\_SUMMARY

\- ABSTAINED



These statuses must correspond to governance.



AUTO\_ANSWER:



\- response\_type = ANSWER

\- generation\_status = GENERATED



REVIEW\_REQUIRED:



\- response\_type = REVIEW

\- generation\_status = REVIEW\_SUMMARY



ABSTAIN:



\- response\_type = ABSTENTION

\- generation\_status = ABSTAINED



\---



\# AUTO\_ANSWER Behaviour



When governance is AUTO\_ANSWER:



The generator may produce:



\- management summary

\- evidence-based explanation

\- operational implication

\- caveats

\- sources



It may summarise and combine evidence only where upstream precedence permits.



It must:



\- stay within approved evidence

\- preserve citation references

\- communicate uncertainty where present

\- avoid unsupported material claims



It must not:



\- invent facts

\- invent citations

\- introduce external knowledge

\- silently upgrade draft or superseded material

\- issue recommendations unsupported by evidence



\---



\# REVIEW\_REQUIRED Behaviour



When governance is REVIEW\_REQUIRED:



The generator may produce:



\- evidence summary

\- explanation of why human review is required

\- review focus

\- evidence gaps or uncertainty

\- sources



It must not present the response as a final operational decision.



It must not:



\- generate an authoritative recommendation

\- hide the review requirement

\- convert uncertainty into certainty

\- treat human review as optional



A REVIEW response should help a manager understand the evidence without pretending that automation has resolved the decision.



\---



\# ABSTAIN Behaviour



When governance is ABSTAIN:



The generator may produce:



\- unable-to-answer-safely statement

\- reason

\- missing evidence

\- information needed to continue



It must not:



\- produce a substantive hidden answer

\- speculate

\- reconstruct an answer from model memory

\- use rejected evidence

\- offer an operational recommendation



The response should remain useful by explaining what is missing and what would be needed next.



\---



\# Citation Rule



The generator must use only citation IDs supplied by the Answer Context.



Examples:



\- E1

\- E2

\- E3



The generator must not create:



\- E4 when no E4 exists

\- new document IDs

\- new page numbers

\- new source filenames



Every substantive evidence-based statement should be traceable to one or more approved evidence references.



\---



\# Claim Grounding Rule



A generated claim is permitted only when it can be supported by approved evidence in the Answer Context.



Unsupported material claims must not be presented as established fact.



If a claim cannot be grounded:



\- omit it

\- qualify it

\- or route it to human review



\---



\# Authority Rule



The generator cannot increase authority.



Examples:



ABSTAIN

must remain

ABSTAIN



REVIEW\_REQUIRED

must remain

REVIEW\_REQUIRED



AUTO\_ANSWER

may generate only within the permissions granted by the Answer Contract.



The generator cannot reinterpret REVIEW\_REQUIRED as AUTO\_ANSWER.



\---



\# Context Boundary Rule



The generator should use only the supplied Answer Context.



It should not rely on:



\- model memory

\- external knowledge

\- unrelated retrieval results

\- rejected chunks

\- hidden prompts

\- unsupported assumptions



This makes the generated response auditable.



\---



\# Deterministic First Strategy



Day 3 will initially implement a deterministic grounded-response builder.



This allows us to test:



\- governance enforcement

\- response structure

\- citation handling

\- abstention behaviour

\- human-review behaviour

\- fail-closed behaviour



before connecting a language model.



A future LLM should operate inside this validated boundary rather than replacing it.



\---



\# Fail-Closed Behaviour



The grounded generator should fail closed when:



\- packet IDs do not match

\- governance decisions do not match

\- response types do not match

\- generation permission contradicts governance

\- required evidence is missing

\- required citations are unavailable

\- REVIEW\_REQUIRED lacks its review flag

\- ABSTAIN contains substantive answer evidence

\- an unsupported response state is supplied



\---



\# Economic Rationale



Grounded generation can reduce:



\- manual document summarisation

\- repetitive briefing preparation

\- time spent locating supporting evidence

\- manager effort checking where statements came from



However, Week 23 should not claim measured savings until those savings are actually benchmarked.



Future evaluation can measure:



\- briefing preparation time

\- evidence-checking time

\- average citations per answer

\- review rate

\- abstention rate

\- token usage

\- cost per response



\---



\# NHS Manager Value



The goal is not simply to produce fluent text.



The goal is to produce responses that a manager can:



\- understand quickly

\- trace back to evidence

\- distinguish from human judgement

\- recognise when review is required

\- trust not to overstate certainty



\---



\# Week 23 Day 3 Principle



> A trustworthy AI answer is not merely fluent; it is permissioned, grounded, traceable and appropriately uncertain.
