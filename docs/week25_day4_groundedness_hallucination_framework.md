\# Week 25 Day 4 — Groundedness, Unsupported Claims \& Hallucination Resistance



\## Purpose



Week 25 Day 4 strengthens the system beyond citation validity and citation

completeness.



The central question is:



> Is the actual answer wording fully justified by the approved evidence?



A claim may contain a valid citation and still be unsafe.



Examples include:



\- adding a number that does not appear in the evidence;

\- changing "should consider" into "must";

\- adding an actor who is not named;

\- adding an operational action that is not supported;

\- hiding uncertainty;

\- presenting conflicting evidence as settled fact;

\- turning REVIEW\_REQUIRED wording into an authoritative instruction;

\- attaching a citation to a claim that overstates the cited source.



Day 4 therefore focuses on groundedness and hallucination resistance.



\---



\## Existing Assurance Architecture



The current Week 25 architecture includes:



Question

→ Evidence Packet

→ Evidence Precedence

→ Governance

→ Answer Contract

→ Answer Context

→ Grounded Response

→ Claim-Citation Linker

→ Citation Completeness

→ Citation Assurance

→ Citation Verification

→ Multi-Source Verification

→ Final Verification Decision



Day 4 adds a separate groundedness layer.



Target architecture:



Question

→ Evidence Packet

→ Evidence Precedence

→ Governance

→ Answer Contract

→ Answer Context

→ Grounded Response

→ Claim-Citation Linker

→ Citation Completeness

→ Citation Assurance

→ Citation Verification

→ Multi-Source Verification

→ Groundedness Audit

→ Hallucination Resistance Audit

→ Final Accept / Review / Abstain Decision



\---



\## Groundedness



A claim is grounded only when its material meaning is supported by approved

evidence.



Groundedness is stricter than citation presence.



A citation can be valid while the claim remains ungrounded.



Example:



Evidence:



> Teams should review staffing pressure daily.



Claim:



> Managers must immediately suspend elective activity when staffing pressure is

> identified.



The citation may point to the correct document.



However, the claim introduces:



\- a mandatory requirement;

\- an immediate timing requirement;

\- a specific actor;

\- a suspension action;

\- an operational consequence.



These additions are not supported by the evidence.



Therefore the claim is not grounded.



\---



\## Groundedness Categories



The Day 4 groundedness layer should distinguish:



\### GROUNDED



The material meaning of the claim is supported by approved evidence.



\### PARTIALLY\_GROUNDED



Some material elements are supported, but one or more important details are

unsupported or overstated.



\### UNGROUNDED



The claim contains substantive content not supported by the approved evidence.



\### NOT\_APPLICABLE



The statement is genuinely non-substantive and does not require evidence

grounding.



\---



\## Hallucination



For this project, hallucination means:



> Material answer content that cannot be justified by the approved evidence,

> provenance, relationship state, or governance state.



Hallucination does not require the statement to be factually false in the real

world.



A statement can be true generally and still be a hallucination within this RAG

system if the approved evidence does not support it.



This distinction is critical.



The system is evidence-bounded.



It must answer from approved evidence rather than external assumptions.



\---



\## Unsupported Numerical Claims



Numbers are high-risk.



Examples include:



\- thresholds;

\- percentages;

\- time limits;

\- staffing ratios;

\- waiting-time targets;

\- escalation levels;

\- financial amounts;

\- dates;

\- capacity limits.



Example:



Evidence:



> Escalation should occur when pressure becomes significant.



Unsafe claim:



> Escalation must occur when bed occupancy exceeds 92%.



The number 92% is fabricated relative to the approved evidence.



Expected behaviour:



\- groundedness failure;

\- hallucination flag;

\- REVIEW\_REQUIRED or stronger safe handling.



\---



\## Unsupported Mandatory Language



Mandatory wording changes authority.



Examples:



\- must;

\- required;

\- mandatory;

\- immediately;

\- shall;

\- cannot;

\- prohibited;

\- must not.



Evidence:



> Teams should consider escalation.



Unsafe claim:



> Teams must escalate immediately.



The change from recommendation to obligation is material.



It must not be treated as a harmless paraphrase.



\---



\## Unsupported Actors



Adding responsibility to an actor is material.



Examples:



\- chief executive;

\- executive;

\- manager;

\- clinical lead;

\- nurse;

\- commissioner;

\- ICB;

\- Trust;

\- operational team.



Evidence:



> Escalation should be considered.



Unsafe claim:



> The chief executive must approve escalation.



The actor and approval requirement are unsupported.



\---



\## Unsupported Actions



Operational actions are high-risk.



Examples:



\- suspend;

\- cancel;

\- redeploy;

\- restore;

\- open;

\- close;

\- evacuate;

\- discharge;

\- transfer;

\- stop;

\- restrict.



Evidence:



> Capacity pressure should be reviewed.



Unsafe claim:



> Elective activity must be cancelled.



This introduces a new operational action.



\---



\## Unsupported Prohibitions



Negative obligations are high-risk.



Examples:



\- must not;

\- cannot;

\- prohibited;

\- forbidden;

\- never.



Evidence:



> Teams should consider alternative staffing options.



Unsafe claim:



> Agency staffing must not be used.



This creates a prohibition not present in evidence.



\---



\## Hidden Uncertainty



A claim can be misleading even when most of its content is technically related

to the evidence.



Example evidence:



> The available evidence suggests staffing pressure may contribute to delays.



Unsafe answer:



> Staffing pressure causes delays.



The answer removes:



\- uncertainty;

\- causal caution;

\- evidential limitation.



The result is an authority increase.



Day 4 must detect this type of overstatement.



\---



\## Overstatement



Overstatement occurs when the answer expresses a stronger proposition than the

evidence supports.



Examples:



Evidence:

> may increase risk



Answer:

> increases risk



Evidence:

> should consider



Answer:

> must



Evidence:

> some services reported



Answer:

> all services experience



Evidence:

> evidence suggests



Answer:

> evidence proves



Overstatement is a groundedness failure even when the topic itself is correct.



\---



\## Conflict Hallucination



When evidence conflicts, the system must not collapse disagreement into a

single settled conclusion.



Evidence A:



> Use approach X.



Evidence B:



> Do not use approach X.



Unsafe answer:



> The approved policy requires approach X.



The correct system behaviour is to preserve conflict and human review.



The answer may truthfully say:



> The approved evidence contains conflicting operational positions.



It may not choose one side without governed precedence evidence.



\---



\## Governance Hallucination



Answer authority must not exceed upstream governance.



If upstream governance is:



REVIEW\_REQUIRED



the generated answer must not behave as:



AUTO\_ANSWER



If upstream governance is:



ABSTAIN



the generated answer must not contain substantive operational advice.



Examples of governance hallucination include:



\- converting review guidance into instruction;

\- presenting uncertain evidence as approved policy;

\- adding actions to an abstention response;

\- hiding the requirement for human review.



\---



\## Evidence-Bounded Generation



The system operates under an evidence-bounded principle.



The model may:



\- summarise;

\- paraphrase safely;

\- organise evidence;

\- explain supported relationships;

\- surface uncertainty;

\- identify evidence gaps.



The model may not:



\- invent missing facts;

\- fill operational gaps from general knowledge;

\- add unsupported thresholds;

\- add unsupported actors;

\- add unsupported actions;

\- resolve conflicts without evidence;

\- increase authority;

\- create policy.



\---



\## Groundedness Evidence Set



A claim may be grounded by:



1\. one approved evidence item;

2\. several approved evidence items jointly;

3\. explicit evidence relationship metadata;

4\. governance state;

5\. Evidence Precedence output.



The verifier must distinguish these sources of support.



A claim about document conflict may require an evidence set.



A claim about a factual statement may require one evidence item.



A claim that human review is required may derive directly from governance state.



\---



\## Day 4 Detection Targets



Day 4 should detect at least:



1\. unsupported numbers;

2\. unsupported mandatory wording;

3\. unsupported actors;

4\. unsupported actions;

5\. unsupported prohibitions;

6\. negation mismatch;

7\. hidden uncertainty;

8\. causal overstatement;

9\. universal overstatement;

10\. fabricated thresholds;

11\. unsupported policy authority;

12\. conflict suppression;

13\. governance authority increase;

14\. substantive advice inside ABSTAIN;

15\. citation-valid but evidence-unsupported claims.



\---



\## Groundedness Decision Model



Claim-level statuses:



\### GROUNDED



All material claim elements are supported.



\### PARTIALLY\_GROUNDED



The core topic is supported but one or more material modifiers or details are

unsupported.



\### UNGROUNDED



The substantive claim cannot be justified by the approved evidence.



\### NOT\_APPLICABLE



The statement is genuinely non-substantive.



\---



\## Answer-Level Decision



\### PASS



All material claims are GROUNDED.



\### REVIEW\_REQUIRED



At least one material claim is:



\- PARTIALLY\_GROUNDED;

\- UNGROUNDED;

\- authority-increasing;

\- uncertainty-suppressing.



\### ABSTAIN



Upstream governance requires abstention and no safe substantive answer can be

supported.



Groundedness must never upgrade upstream governance.



\---



\## Relationship to Existing Citation Verification



The existing citation verifier already protects against several high-risk

mismatches.



Day 4 should reuse and extend those controls.



The new groundedness layer should not duplicate logic unnecessarily.



Existing controls include checks for:



\- unsupported numbers;

\- unsupported mandatory wording;

\- unsupported actors;

\- unsupported actions;

\- negation mismatch;

\- unsupported prohibitions.



Day 4 adds answer-level and evidence-set interpretation around those controls.



\---



\## Benchmark Relationship



The Week 25 benchmark already contains adversarial cases relevant to Day 4,

including:



\- unsupported operational claims;

\- partially supported claims;

\- overstated claims;

\- conflicting evidence;

\- ignored conflict;

\- hidden uncertainty;

\- review authority increase;

\- unsafe abstention;

\- fabricated thresholds.



The benchmark must remain authoritative.



Golden expectations must not be weakened to improve the score.



Day 4 should improve implementation until the benchmark passes for the intended

reason.



\---



\## Safety Properties



Day 4 must preserve these rules:



1\. Citation presence never proves groundedness by itself.

2\. Semantic similarity cannot override high-risk mismatches.

3\. Unsupported numbers fail closed.

4\. Unsupported operational actions fail closed.

5\. Unsupported mandatory language fails closed.

6\. Unsupported actors fail closed.

7\. Unsupported prohibitions fail closed.

8\. Hidden uncertainty must not be treated as harmless paraphrase.

9\. Conflict must not be silently resolved.

10\. REVIEW\_REQUIRED must not become authoritative advice.

11\. ABSTAIN must not contain substantive operational recommendations.

12\. Groundedness cannot override Evidence Precedence.

13\. Groundedness cannot override governance.

14\. External general knowledge cannot fill missing evidence.

15\. Human review remains authoritative where required.



\---



\## Day 4 Implementation Boundary



Day 4 will add:



1\. deterministic groundedness assessment;

2\. unsupported-claim detection;

3\. overstatement detection;

4\. uncertainty-preservation checks;

5\. answer-level hallucination resistance;

6\. integration with existing benchmark cases;

7\. adversarial regression tests.



Day 4 will not:



\- use unrestricted model judgement as a safety control;

\- infer missing policy;

\- invent source relationships;

\- weaken benchmark expectations;

\- override governance;

\- override lifecycle controls;

\- override Evidence Precedence.



\---



\## Acceptance Criteria



Day 4 is complete only when:



\- existing Week 25 tests remain green;

\- the 18-case benchmark remains green;

\- unsupported numbers are detected;

\- unsupported actions are detected;

\- unsupported actors are detected;

\- unsupported mandatory language is detected;

\- hidden uncertainty is detected;

\- overstatement is detected;

\- conflict suppression is detected;

\- REVIEW\_REQUIRED authority increase is detected;

\- substantive advice inside ABSTAIN is detected;

\- full repository regression passes;

\- all changes are documented and committed with a clean working tree.



\---



\## Engineering Principle



> A cited answer is not necessarily a grounded answer.



A trustworthy healthcare RAG system must prove not only:



\- where the answer came from;



but also:



\- whether the wording stayed inside the evidence;

\- whether uncertainty was preserved;

\- whether authority was preserved;

\- whether operational actions were justified;

\- and whether the answer remained inside governance boundaries.

