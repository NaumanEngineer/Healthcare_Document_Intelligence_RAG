\# Week 20 Day 4 — NHS Governance, Regulation and Deployment Readiness Review



\## Objective



Assess whether the Healthcare Document Intelligence / RAG Assistant and future NHS Sovereign Operational Intelligence \& Evidence Copilot are being designed in a way that could survive real NHS governance and deployment scrutiny.



The review focuses on:



\- intended purpose;

\- risk boundary;

\- clinical safety;

\- DCB0129 / DCB0160 mindset;

\- DPIA and privacy;

\- UK GDPR;

\- data minimisation;

\- human oversight;

\- auditability;

\- accountability;

\- regulatory status;

\- deployment readiness;

\- procurement readiness;

\- change control.



The goal is not to claim formal compliance.



The goal is to design the project so formal assurance can be built on top of it later.



\---



\## Intended Purpose



Current intended purpose:



\*\*An operational decision-support system for NHS managers that combines operational data and policy evidence to explain service pressure, retrieve relevant guidance, and prepare governed management briefings.\*\*



The system is intended to:



\- summarise operational pressure;

\- compare operational metrics;

\- retrieve relevant policy evidence;

\- identify potentially relevant escalation guidance;

\- explain uncertainty;

\- prepare management briefings;

\- route uncertain or consequential cases for human review.



\---



\## Explicit Risk Boundary



The system is not intended to:



\- diagnose patients;

\- recommend treatment;

\- prescribe;

\- make autonomous clinical decisions;

\- automatically trigger high-risk operational actions;

\- override accountable NHS professionals.



Core principle:



\*\*The AI supports the decision. The authorised NHS professional remains accountable for the decision.\*\*



\---



\## Autonomy Boundary



Preferred pattern:



AI can:

\- analyse;

\- retrieve;

\- compare;

\- summarise;

\- flag;

\- prepare evidence.



Human must:

\- approve consequential action;

\- escalate;

\- intervene where required;

\- retain accountability.



\---



\## Uncertainty Behaviour



The system should not force an answer when evidence is weak.



Preferred states:



\- AUTO\_ANSWER

\- REVIEW\_REQUIRED

\- ABSTAIN



AUTO\_ANSWER:

Use for low-risk, evidence-supported informational outputs.



REVIEW\_REQUIRED:

Use where evidence is ambiguous, consequences are material, or human judgement is required.



ABSTAIN:

Use where evidence is insufficient, unsafe, out of scope, or unreliable.



\---



\## Clinical Safety Mindset



DCB0129:

Clinical risk-management responsibilities associated with development / manufacture of health IT.



DCB0160:

Clinical risk-management responsibilities associated with deployment and use within a healthcare organisation.



Simplified interpretation:



DCB0129:

"Did we build the system safely?"



DCB0160:

"Can this organisation use the system safely in its real environment?"



\---



\## Current Controls That Support Clinical Safety



Existing controls include:



\- lifecycle filtering;

\- evidence sufficiency;

\- citation verification;

\- high-risk claim guard;

\- evidence-set reasoning;

\- corrective false-premise validation;

\- AUTO / REVIEW / ABSTAIN;

\- regression testing;

\- version control.



These controls should be preserved as future safety evidence.



\---



\## Example Hazard Mapping



| Hazard | Potential harm | Existing / planned control |

|---|---|---|

| Superseded policy used | Manager acts on obsolete guidance | Lifecycle filtering |

| Unsupported escalation instruction | Incorrect operational action | High-risk claim guard |

| Weak evidence treated as certainty | Poor management decision | Evidence sufficiency + ABSTAIN |

| False conflict accepted | Wrong policy interpretation | Evidence-set reasoning |

| Incorrect citation | False confidence | Citation verification |

| Consequential ambiguity auto-answered | Unsafe decision support | REVIEW\_REQUIRED |

| Out-of-scope clinical question answered | Inappropriate system use | Scope boundary + ABSTAIN |



\---



\## Safety Case Mindset



Future safety documentation may include:



Clinical Risk Management Plan

→ Hazard Log

→ Risk Controls

→ Test Evidence

→ Residual Risk

→ Clinical Safety Case



The training project does not claim formal DCB0129 or DCB0160 compliance.



The project is designed to produce evidence that could support later formal assurance.



\---



\## Clinical Safety Officer



A real NHS deployment would require appropriate clinical-safety leadership.



The project developer should provide:



\- architecture;

\- hazards;

\- controls;

\- test evidence;

\- known limitations.



Formal safety acceptance should not be self-declared by the developer.



\---



\## DPIA and Privacy



A future deployment should use a Data Protection Impact Assessment where required.



The DPIA should identify:



\- what personal data is processed;

\- why it is needed;

\- lawful basis;

\- special-category condition where relevant;

\- who can access it;

\- where it is stored;

\- retention period;

\- model/provider processing;

\- risks to individuals;

\- mitigating controls.



\---



\## Data Minimisation



Core privacy principle:



\*\*Use the minimum data necessary to answer the operational question.\*\*



Preferred data pattern:



\- aggregated operational data;

\- anonymised / de-identified data where possible;

\- only necessary fields;

\- no unnecessary identifiers.



Avoid unnecessary use of:



\- patient names;

\- NHS numbers;

\- addresses;

\- full clinical notes;

\- unrelated personal data.



\---



\## Development / Production Separation



Development:



\- synthetic data;

\- anonymised data where appropriate;

\- local testing;

\- benchmarks;

\- experiments.



Production:



\- authorised operational data;

\- identity controls;

\- RBAC;

\- DPIA;

\- auditing;

\- monitoring;

\- approved processing environment.



Development should not depend on real patient data where synthetic data is sufficient.



\---



\## Privacy-by-Design Principle



The architecture should ask:



\*\*Can the operational objective be achieved with less personal data?\*\*



If yes, redesign toward the smaller data footprint.



Economic interpretation:



The cheapest sensitive data to govern is the sensitive data that is never ingested.



\---



\## Audit Logging



Auditability should allow reconstruction of significant interactions.



Potential audit fields:



\- user identity;

\- timestamp;

\- model version;

\- retrieval version;

\- governance version;

\- policy corpus version;

\- evidence IDs;

\- data sources accessed;

\- decision outcome;

\- human-review status;

\- reviewer identity;

\- reviewer action.



Avoid indiscriminate logging of unnecessary sensitive raw content.



\---



\## Human Oversight



Human oversight must be meaningful rather than a rubber-stamp.



A reviewer should be able to:



\- inspect supporting evidence;

\- see uncertainty;

\- inspect relevant policy;

\- reject the AI output;

\- modify the conclusion;

\- request more evidence;

\- escalate.



\---



\## Human Review Interface Concept



Potential workflow:



Question

→ AI summary

→ supporting evidence

→ citation / lifecycle / sufficiency checks

→ risk reason

→ REVIEW\_REQUIRED

→ human accepts / rejects / modifies / requests evidence

→ action recorded



\---



\## Accountability Model



SYSTEM:

gathers and analyses evidence.



ASSURANCE LAYER:

determines whether conditions for answering are met.



HUMAN REVIEWER:

evaluates consequential outputs.



ACCOUNTABLE NHS ROLE:

owns the final operational decision.



Responsibility must not disappear because AI contributed to the decision.



\---



\## Selective Human Oversight



Do not require human review for every low-risk question.



Do not allow autonomous action for every question.



Preferred principle:



\*\*Automate the routine. Escalate the consequential.\*\*



\---



\## Regulatory Position



The project should not claim:



\- medical-device status;

\- exemption from medical-device regulation;

\- formal regulatory compliance.



Regulatory classification should be assessed against the final intended purpose, functionality and deployment context.



Operational decision support may have a different regulatory profile from diagnostic or treatment software, but formal classification should be performed before production deployment.



\---



\## Regulatory Change



Healthcare AI regulation continues to evolve.



The architecture should therefore keep these modular:



\- model layer;

\- retrieval layer;

\- governance layer;

\- policy corpus;

\- deployment configuration;

\- version identifiers.



This allows regulatory or policy changes to be absorbed without rebuilding the entire system.



\---



\## Version and Change Control



Future production releases should record:



\- model\_version;

\- retrieval\_version;

\- governance\_version;

\- policy\_corpus\_version;

\- prompt / orchestrator version;

\- deployment version.



Changes should be evaluated rather than silently introduced.



\---



\## Technical Readiness



Current strengths:



\- version-controlled repository;

\- reproducible architecture;

\- synthetic benchmark;

\- governed retrieval;

\- citation verification;

\- lifecycle controls;

\- regression testing;

\- documented limitations.



Latest verified full regression baseline:



\- 338 tests passed



This remains test evidence for the current controlled prototype.



\---



\## Remaining Technical Evidence Needed for Real Deployment



Future evidence should include:



\- representative NHS-style testing;

\- real operational workflow evaluation;

\- latency;

\- cost;

\- usability;

\- accessibility;

\- failure-mode testing;

\- monitoring;

\- rollback;

\- security testing.



\---



\## Deployment Readiness Categories



\### Technically Ready



Questions:



\- Is the system reproducible?

\- Are failure modes tested?

\- Is rollback possible?

\- Is monitoring defined?

\- Are limitations documented?



\### Governance Ready



Questions:



\- Is intended purpose documented?

\- Is scope defined?

\- Are hazards documented?

\- Is human accountability clear?

\- Are ABSTAIN / REVIEW rules defined?



\### Security Ready



Questions:



\- Is identity controlled?

\- Is least privilege enforced?

\- Is RBAC implemented?

\- Are secrets protected?

\- Is logging appropriate?

\- Is incident response defined?



\### Regulatory Ready



Questions:



\- Has intended purpose been formally assessed?

\- Has medical-device relevance been assessed?

\- Are clinical-safety obligations known?

\- Is privacy impact understood?



\### Procurement Ready



Questions:



\- Who owns the system?

\- What does it cost?

\- Where is data hosted?

\- What support exists?

\- What service levels apply?

\- How are upgrades controlled?

\- What is the exit strategy?

\- Can data be exported?

\- What happens after incidents?



\---



\## Current Prototype Readiness



| Area | Current status |

|---|---|

| Architecture | GREEN |

| Git / version control | GREEN |

| Synthetic testing | GREEN |

| Citation / evidence governance | GREEN |

| Intended purpose | GREEN / evolving |

| Human-review architecture | GREEN / evolving |

| Real NHS user testing | RED |

| Real production-data validation | RED |

| Formal DPIA | RED |

| Formal DCB safety case | RED |

| Clinical Safety Officer sign-off | RED |

| Formal regulatory classification | RED |

| Production security testing | RED |

| Procurement pack | RED |



This is expected for a portfolio / prototype stage system.



RED does not mean failure.



It identifies evidence that would be required before real deployment.



\---



\## DTAC-Style Readiness Mindset



Future project review should consider areas such as:



\- clinical safety;

\- data protection;

\- technical security;

\- interoperability;

\- usability;

\- accessibility.



The project should gradually build an evidence pack around these areas.



\---



\## Procurement Evidence Pack



Future artefacts may include:



\- architecture diagram;

\- data-flow diagram;

\- security documentation;

\- DPIA;

\- hazard log;

\- clinical-safety material;

\- test evidence;

\- accessibility evidence;

\- interoperability documentation;

\- support model;

\- pricing / cost model;

\- change-management plan;

\- monitoring plan;

\- exit strategy.



\---



\## Economic Interpretation



The gap between:



working prototype



and



deployable NHS system



contains significant hidden cost.



Late discovery of:



\- privacy gaps;

\- security weaknesses;

\- regulatory issues;

\- safety problems;

\- procurement requirements



can force expensive redesign.



Preferred principle:



\*\*Build deployment evidence alongside the product rather than bolting governance on at the end.\*\*



\---



\## Day 4 Decision Table



| Capability | Decision |

|---|---|

| Intended purpose | KEEP AND FORMALISE |

| Operational decision-support boundary | KEEP |

| Autonomous high-risk action | AVOID |

| Human accountability | REQUIRE |

| AUTO / REVIEW / ABSTAIN | KEEP |

| DCB0129 mindset | ADOPT |

| DCB0160 understanding | REQUIRE |

| Formal DCB compliance claim now | DO NOT CLAIM |

| Hazard log | ADD |

| Safety case evidence | BUILD GRADUALLY |

| DPIA mindset | ADOPT |

| Data minimisation | REQUIRE |

| Synthetic development data | KEEP |

| Unrestricted patient-level access | AVOID |

| Auditability | REQUIRE |

| Model / retrieval / governance versioning | ADD |

| Regulatory-status review | ADD BEFORE DEPLOYMENT |

| DTAC-style readiness mapping | ADD |

| Procurement evidence pack | ADD LATER |

| Post-deployment monitoring | ADD LATER |



\---



\## Emerging Governance USP



The project is evolving toward:



\*\*A governed NHS operational intelligence copilot that does not simply generate answers, but actively evaluates evidence quality, lifecycle status, uncertainty, human-review requirements and auditability before allowing an answer to be used.\*\*



\---



\## Day 4 Final Principle



\*\*The safest and economically strongest NHS AI system is not one that claims to be always right. It is one that can prove what evidence it used, recognise uncertainty, escalate consequential cases and preserve clear human accountability.\*\*



\---



\## Next Review



Day 5 will focus on cross-pollination from other high-reliability industries.



Potential sectors:



\- aviation;

\- banking;

\- cybersecurity;

\- logistics;

\- manufacturing;

\- defence / command-and-control principles.



Central question:



\*\*Which proven operating principles from other high-reliability industries can improve NHS operational decision support without adding unnecessary AI complexity?\*\*

