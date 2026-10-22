\# Week 28 Day 3 — Manager-Facing Response Contract



\## Purpose



Week 28 Day 3 improves how the Healthcare Document Intelligence RAG

application communicates governed outcomes to operational users.



Week 28 Day 2 proved that the canonical application can naturally produce:



\- ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



Day 3 does not change those decisions.



Instead, it defines a downstream presentation layer that translates the

governed result into a clear and useful management response.



The central design rule is:



> Improve presentation, not authority.



The manager-facing response must never increase the authority already granted

by retrieval, evidence, governance, generation or assurance.



\---



\# 1. User Need



An NHS operational manager should not need to understand:



\- retrieval scores

\- evidence-packet internals

\- RRF ranking

\- precedence algorithms

\- model execution states

\- assurance implementation details

\- internal governance objects



The manager needs to understand four things:



1\. What did the system decide?

2\. What information supports that decision?

3\. Why should I trust or question the response?

4\. What should happen next?



\---



\# 2. Protected Architecture



The manager-facing layer is downstream of the existing governed application.



Canonical flow:



Question

→ Retrieval

→ Evidence

→ Provenance

→ Precedence

→ Pre-Generation Governance

→ Generation

→ Citation / Faithfulness Assurance

→ Post-Generation Governance

→ Final Governed Outcome

→ Manager-Facing Presentation



The manager-facing layer must not:



\- perform retrieval

\- change evidence

\- reinterpret provenance

\- resolve conflicts

\- override governance

\- manufacture citations

\- manufacture operational guidance

\- increase decision authority

\- convert REVIEW\_REQUIRED into ANSWER

\- convert ABSTAIN into ANSWER

\- hide material uncertainty



\---



\# 3. Authority Preservation Rule



The final governed outcome is authoritative.



The presentation layer may explain that outcome.



It may not replace it.



Allowed mapping:



ANSWER

→ manager-facing ANSWER



REVIEW\_REQUIRED

→ manager-facing REVIEW\_REQUIRED



ABSTAIN

→ manager-facing ABSTAIN



Forbidden mapping:



REVIEW\_REQUIRED

→ ANSWER



ABSTAIN

→ ANSWER



The presentation layer therefore has an authority ceiling equal to the

application's existing final outcome.



\---



\# 4. Common Manager Response Contract



Every manager-facing response should contain a stable set of fields.



\## Required Fields



\### outcome



One of:



\- ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



\### headline



A short plain-English description of the system decision.



\### summary



A concise explanation appropriate for an operational manager.



\### evidence\_basis



A safe explanation of the evidence supporting the decision.



\### confidence\_message



A qualitative explanation of how the evidence should be treated.



This must not invent a numeric probability unless one already exists as a

validated system metric.



\### next\_action



A safe explanation of what the user can do next.



\### human\_review\_required



Boolean.



\### citations



Only citations already supported by the governed response.



No citation may be created solely by the presentation layer.



\### limitations



Important restrictions or uncertainty relevant to the response.



\---



\# 5. ANSWER Contract



\## Objective



Give the manager a concise supported answer when the governed application has

already authorised an ANSWER.



\## Required Behaviour



The response should contain:



1\. the supported operational answer

2\. a short explanation of the evidence basis

3\. relevant citations

4\. any material limitations

5\. optional next-step guidance that does not introduce unsupported operational

&#x20;  authority



\## Example Structure



Outcome:

ANSWER



Headline:

Supported guidance found



Summary:

The available approved evidence supports an answer to this question.



Answer:

\[Existing governed answer]



Evidence basis:

This response is supported by the retrieved approved guidance.



Confidence message:

The available evidence was sufficient for the governed application to release

an answer.



Next action:

Use the cited source material where additional detail or confirmation is

required.



Human review required:

No



\## Safety Rules



The presentation layer must not:



\- strengthen "may" into "must"

\- strengthen "consider" into "required"

\- invent responsibility or authority

\- create new operational actions

\- remove uncertainty already present in the governed answer

\- omit important caveats

\- generate unsupported recommendations



\---



\# 6. REVIEW\_REQUIRED Contract



\## Objective



Explain clearly that relevant evidence exists but the system cannot safely

release an authoritative answer without human judgement.



This is not a system failure.



It is an intended governed outcome.



\## Required Behaviour



The response should tell the manager:



1\. relevant evidence was found

2\. why automatic answering was not appropriate

3\. what type of review is required

4\. what the reviewer should examine

5\. that the system has not resolved the issue autonomously



\## Example Structure



Outcome:

REVIEW\_REQUIRED



Headline:

Human review required before using this information



Summary:

Relevant evidence was identified, but the available information should not be

combined or treated as an authoritative operational answer without human

review.



Evidence basis:

Multiple relevant evidence sources were identified.



Reason for review:

The evidence requires human judgement before a combined conclusion can be

safely released.



Next action:

Review the cited sources together and confirm the current operational position

before acting on the information.



Human review required:

Yes



\## Safety Rules



The presentation layer must not:



\- provide a disguised answer beneath the review warning

\- decide which source wins unless precedence already established this

\- invent an escalation route

\- name an approving role unless that role exists in the evidence

\- imply that human review is optional

\- convert cross-document evidence into an authoritative combined instruction



\---



\# 7. ABSTAIN Contract



\## Objective



Explain that the system cannot safely answer from the available evidence.



The abstention must be useful rather than merely saying:



"No answer."



\## Required Behaviour



The response should explain:



1\. that no safe answer can currently be provided

2\. why

3\. what information is missing

4\. what evidence would be needed to continue

5\. that no operational instruction has been inferred



\## Example Structure



Outcome:

ABSTAIN



Headline:

Insufficient evidence for a safe answer



Summary:

The available approved evidence is not sufficient to answer this question

safely.



Evidence basis:

No suitable evidence was available to support an authoritative response.



Missing information:

Current approved guidance relevant to the question.



Next action:

Provide or identify the relevant approved guidance, or route the question for

appropriate human review.



Human review required:

Yes, if an operational decision is required before suitable evidence becomes

available.



\## Safety Rules



The presentation layer must not:



\- guess

\- fill the evidence gap using general model knowledge

\- introduce an operational directive

\- invent organisational policy

\- invent responsible roles

\- express unsupported certainty

\- describe abstention as a technical failure when it is an intentional safety

&#x20; outcome



\---



\# 8. Evidence Disclosure



The manager-facing response should expose enough information to explain the

decision without exposing unnecessary internal data.



Appropriate:



\- number of supporting sources

\- source titles when already authorised for display

\- citations

\- document status where relevant

\- whether evidence was sufficient

\- whether evidence required reconciliation



Avoid exposing:



\- embeddings

\- vector values

\- raw prompt content

\- internal chain-of-thought

\- credentials

\- internal exception details

\- raw model-system messages

\- unnecessary document text

\- sensitive metadata



\---



\# 9. Confidence Language



The presentation layer should use governance-aware language rather than vague

AI confidence claims.



Preferred:



"The available evidence was sufficient for a governed answer."



"Relevant evidence was found, but human judgement is required."



"The available evidence is insufficient for a safe answer."



Avoid:



"The AI is 95% confident."



"The AI thinks this is probably correct."



"This is definitely correct."



"The model recommends..."



unless such wording is explicitly supported by a validated system contract.



\---



\# 10. Management-Friendly Language



Technical internal terms should generally be translated.



Internal:

AUTO\_ANSWER



Manager-facing:

Supported answer



Internal:

REVIEW\_REQUIRED



Manager-facing:

Human review required



Internal:

ABSTAIN



Manager-facing:

Insufficient evidence for a safe answer



Internal:

precedence conflict



Manager-facing:

The available sources cannot safely be combined without review.



Internal:

evidence sufficiency failure



Manager-facing:

The available evidence is not sufficient to support an answer.



The underlying machine-readable outcome must still remain available for

logging, testing and auditing.



\---



\# 11. Structured Response Schema



Target presentation object:



```text

{

&#x20;   "outcome": "...",

&#x20;   "headline": "...",

&#x20;   "summary": "...",

&#x20;   "answer": "... or null",

&#x20;   "evidence\_basis": "...",

&#x20;   "confidence\_message": "...",

&#x20;   "next\_action": "...",

&#x20;   "human\_review\_required": true/false,

&#x20;   "citations": \[...],

&#x20;   "limitations": \[...]

}

