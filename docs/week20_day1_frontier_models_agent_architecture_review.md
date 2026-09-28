\# Week 20 Day 1 — Frontier Models and Agent Architecture Review



\## Objective



Review whether recent developments in frontier models and agent platforms should change the architecture of the Healthcare Document Intelligence / RAG Assistant and the future NHS Sovereign Operational Intelligence \& Evidence Copilot.



This review deliberately separates:



\- intelligence capability;

\- evidence assurance;

\- operational governance.



The goal is not to adopt new technology because it is fashionable.



The goal is to identify which changes genuinely improve:



\- operational usefulness;

\- safety;

\- maintainability;

\- cost;

\- latency;

\- auditability;

\- deployability.



\---



\## Architecture v1 Baseline



The Week 19 governed architecture was:



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

→ AUTO\_ANSWER / REVIEW\_REQUIRED / ABSTAIN



Latest verified regression baseline:



\- 338 tests passed



This architecture is used as the comparison baseline for Week 20.



\---



\## Key Technology Shift



Frontier models and managed agent platforms are becoming better at:



\- long-context reasoning;

\- multi-step tool use;

\- structured outputs;

\- computer-use workflows;

\- context management;

\- long-running tasks;

\- subagent coordination;

\- dynamic reasoning.



This reduces the need for some custom orchestration.



However, stronger models do not remove the need for:



\- evidence provenance;

\- lifecycle/version control;

\- citation verification;

\- deterministic high-risk checks;

\- abstention;

\- human review;

\- auditability.



\---



\## Core Architecture Principle



\### Simplify the intelligence layer, preserve the assurance layer.



In practical terms:



Simplify:



\- unnecessary specialist agents;

\- duplicated orchestration;

\- excessive prompt scaffolding;

\- custom runtime infrastructure where managed services already provide it.



Preserve:



\- evidence sufficiency;

\- lifecycle checks;

\- citation verification;

\- high-risk claim checks;

\- evidence-set reasoning;

\- corrective false-premise handling;

\- human review;

\- abstention;

\- auditability.



\---



\## Economic Interpretation



A more complex AI architecture is not automatically a better system.



Too many agents can increase:



\- token usage;

\- latency;

\- infrastructure cost;

\- debugging effort;

\- maintenance effort;

\- failure points.



The preferred direction is:



one strong orchestrator

\+

bounded specialist tools

\+

managed runtime where appropriate

\+

deterministic assurance controls



This should reduce unnecessary AI operating cost while preserving trust and governance.



The business principle is:



\*\*Spend money on useful intelligence and NHS-specific assurance, not unnecessary AI plumbing.\*\*



\---



\## NHS Manager Interpretation



The system is being redesigned to remove unnecessary AI handoffs while keeping the controls that protect the organisation.



The objective is not to replace managers.



The objective is to reduce the time required to:



\- gather information;

\- reconcile multiple data sources;

\- search policy documents;

\- interpret operational pressure;

\- prepare management briefings.



The AI prepares an evidence-backed briefing.



The manager remains accountable for the decision.



\---



\## Agent Architecture Review



\### Earlier pattern



Potentially overcomplicated:



Manager Agent

→ Retrieval Agent

→ Policy Agent

→ Governance Agent

→ Citation Agent

→ Reporting Agent



This introduces:



\- more model calls;

\- more handoffs;

\- additional state management;

\- harder debugging;

\- weaker end-to-end traceability.



\### Preferred direction



One governed orchestrator

→ specialist tools

→ deterministic assurance layer



Specialist subagents should only be introduced when tasks are genuinely independent and benefit from parallel execution.



Examples:



\- workforce analysis;

\- bed pressure analysis;

\- incident analysis;

\- external pressure analysis.



Sequential governance checks should remain deterministic and tightly controlled rather than being separated into autonomous agents.



\---



\## Tool versus Agent Principle



\### Agents



Use for:



\- flexible reasoning;

\- planning;

\- coordination;

\- synthesis;

\- independent analytical workstreams.



\### Tools



Use for:



\- retrieval;

\- SQL queries;

\- calculations;

\- policy lookup;

\- lifecycle checks;

\- evidence validation;

\- citation verification;

\- deterministic governance.



\### Governance



Use for:



\- final safety decisions;

\- human-review routing;

\- abstention;

\- auditability.



\---



\## Long-Context Review



Long-context capability is a genuine upgrade opportunity.



Potential benefits include:



\- stronger cross-document analysis;

\- fewer context-fragmentation problems;

\- better policy comparison;

\- richer reasoning over retrieved evidence.



However, long context does not automatically replace retrieval.



Retrieval is still useful for:



\- evidence selection;

\- provenance;

\- lifecycle filtering;

\- cost control;

\- reducing irrelevant evidence;

\- citation traceability.



Decision:



\- Long context: UPGRADE CANDIDATE

\- Controlled retrieval/RAG: KEEP FOR NOW



\---



\## Model Routing Opportunity



A future architecture may route questions according to complexity and risk.



Example:



Simple factual query

→ lower-cost model or reasoning mode



Complex cross-document analysis

→ stronger reasoning model



High-risk ambiguous question

→ stronger reasoning + assurance layer + human review



This creates a possible future capability:



\### Risk- and complexity-aware model routing



Potential benefits:



\- lower operating cost;

\- better latency;

\- higher reasoning effort only where justified.



\---



\## Computer-Use Opportunity



Future frontier models may allow the system to do more than answer questions.



Potential controlled workflow:



Operational issue detected

→ gather evidence

→ prepare escalation summary

→ populate management report

→ prepare workflow action

→ human approval



This supports the longer-term shift from:



chatbot



to



operational copilot.



Computer-use capability should only be introduced with explicit permissions, auditability and human oversight.



\---



\## KEEP / UPGRADE / REPLACE / IGNORE Decisions



| Component | Decision | Rationale |

|---|---|---|

| Strong primary orchestrator | UPGRADE | Cleaner coordination with fewer unnecessary handoffs |

| Multiple specialist agents everywhere | REDUCE / REPLACE | Added cost and complexity unless workstreams are genuinely independent |

| Specialist capabilities as tools | UPGRADE | Easier to test, govern and audit |

| Custom agent runtime | REPLACE where appropriate | Managed platforms increasingly provide runtime infrastructure |

| Heavy prompt scaffolding | REDUCE | Critical controls should live in deterministic code |

| Hybrid retrieval / RAG | KEEP FOR NOW | Still valuable for provenance and controlled evidence selection |

| Long-context reasoning | UPGRADE CANDIDATE | Useful for cross-document reasoning |

| Citation verification | KEEP | Required for evidence integrity |

| Lifecycle/version control | KEEP | Protects against Draft, Superseded and Archived evidence |

| Evidence sufficiency | KEEP | Prevents unsupported answering |

| High-risk claim guard | KEEP | Protects against unsupported numbers, actors, actions and mandatory wording |

| Evidence-set reasoning | KEEP AND EXPAND LATER | Important for cross-policy relationships |

| Corrective false-premise handling | KEEP | Stops the model accepting unsupported user assumptions |

| AUTO / REVIEW / ABSTAIN | KEEP | Safe behaviour under uncertainty |

| Human review | KEEP | Required for consequential operational decisions |

| “Long context makes RAG obsolete” | IGNORE | Does not solve provenance or lifecycle issues |

| “Every capability needs an agent” | IGNORE | Complexity without demonstrated operational value |

| New technology only because it is fashionable | IGNORE | Technology must earn its place through measurable value |



\---



\## Architecture v2 — Provisional Direction



NHS Manager

↓

Governed Orchestrator

↓

Bounded Specialist Tools

↓

Evidence Package

↓

Assurance Layer

↓

Lifecycle Checks

\+ Citation Verification

\+ Evidence Sufficiency

\+ High-Risk Checks

\+ Evidence-Set Reasoning

↓

AUTO\_ANSWER / REVIEW\_REQUIRED / ABSTAIN

↓

Manager



\---



\## Model Replaceability



A key architectural goal is to avoid permanently coupling the product to one frontier model.



Preferred pattern:



Model A

↓

Governed interface

↓

Assurance layer



Later:



Model B

↓

same governed interface

↓

same assurance layer



A replacement model should only be adopted after evaluation against the existing benchmark and governance requirements.



\---



\## Emerging USP



The project is moving away from:



“a multi-agent RAG chatbot”



toward:



\*\*A model-flexible, evidence-governed NHS operational intelligence copilot that reduces unnecessary AI complexity while preserving auditability, policy safety and human accountability.\*\*



\---



\## Economic USP



The system should ultimately be evaluated on measurable operational value such as:



\- management preparation time saved;

\- analyst minutes saved;

\- manual data sources avoided;

\- policy-search time reduced;

\- citation accuracy;

\- unsafe answers blocked;

\- appropriate human escalations;

\- cost per governed query.



The aim is:



\*\*more useful intelligence per pound spent, with evidence and governance built in.\*\*



\---



\## Day 1 Decision



The provisional Week 20 architecture principle is:



\*\*Use frontier AI for flexible reasoning and orchestration. Use deterministic software for evidence assurance and safety-critical controls.\*\*



Architecture v1 remains the tested baseline.



Architecture v2 should simplify the intelligence layer while preserving and strengthening the assurance layer.



\---



\## Next Review



Day 2 will focus on:



\- RAG;

\- retrieval;

\- reranking;

\- long-context alternatives;

\- graph / relationship retrieval;

\- evidence architecture.



The question will be:



\*\*Which parts of our current retrieval architecture still earn their place, and which should be upgraded or replaced?\*\*

