\# Week 20 — Technology \& Architecture Refresh Gate

\## Final Architecture Decision Record



\## Objective



Week 20 reviewed whether the existing Healthcare Document Intelligence / RAG architecture should change in response to developments in:



\- frontier models;

\- agent architecture;

\- modern retrieval;

\- long-context reasoning;

\- Microsoft Fabric;

\- Microsoft Foundry;

\- enterprise deployment;

\- NHS governance;

\- clinical safety;

\- regulation;

\- high-reliability operating models.



The purpose was not to chase new technology.



The purpose was to decide:



\- what to KEEP;

\- what to UPGRADE;

\- what to REPLACE;

\- what to IGNORE;

\- what to build next;

\- what to defer.



\---



\# 1. Architecture v1 Baseline



The tested Architecture v1 pipeline is:



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



The main strength of Architecture v1 is its assurance layer.



It does not rely only on retrieval and generation.



It explicitly checks:



\- scope;

\- source lifecycle;

\- evidence sufficiency;

\- citation support;

\- high-risk claims;

\- cross-document relationships;

\- false premises;

\- whether the answer should be automatically released, reviewed, or withheld.



Architecture v1 therefore remains the tested assurance baseline.



\---



\# 2. Week 20 Core Architecture Principle



The strongest conclusion from Week 20 is:



\*\*Simplify the intelligence layer, preserve the assurance layer.\*\*



Frontier models, orchestration, retrieval techniques and enterprise runtimes may change.



The evidence-governance layer remains a strategic asset.



Related principles:



\*\*Keep the model replaceable. Keep the assurance stable.\*\*



\*\*Prototype locally. Industrialize selectively.\*\*



\*\*Automate the checks, not the accountability.\*\*



\*\*Protect management attention.\*\*



\---



\# 3. Final KEEP / UPGRADE / REPLACE / IGNORE Decisions



| Component | Decision | Rationale |

|---|---|---|

| Semantic retrieval | KEEP | Strong retrieval baseline |

| Keyword / BM25 retrieval | KEEP | Important lexical complement |

| Hybrid retrieval | KEEP | Reliable foundation |

| RRF | KEEP | Useful result fusion |

| Hybrid Rescue | KEEP FOR NOW | Retain until better approaches prove superior |

| Dedicated reranking | UPGRADE | Strong next-step candidate |

| Bounded agentic retrieval | UPGRADE | Useful for complex evidence search |

| Long-context reasoning | UPGRADE AS COMPLEMENT | Useful after evidence selection |

| Relationship-aware retrieval | UPGRADE | Supports policy relationships and precedence |

| Full GraphRAG | IGNORE FOR NOW | Too much infrastructure complexity |

| Multi-agent architecture everywhere | REDUCE / REPLACE | Excess orchestration cost and complexity |

| Strong orchestrator + bounded tools | KEEP / UPGRADE | Preferred architecture |

| Evidence sufficiency | KEEP | Core assurance control |

| Lifecycle checking | KEEP | Core policy safety control |

| Citation verification | KEEP | Essential |

| High-risk claim guard | KEEP | Essential |

| Evidence-set relationship reasoning | KEEP | Important assurance capability |

| Corrective false-premise handling | KEEP | Important epistemic control |

| AUTO / REVIEW / ABSTAIN | KEEP | Core human-governance pattern |

| Local Python development | KEEP | Best current engineering environment |

| PostgreSQL | KEEP | Strong structured-data prototype |

| Power BI | KEEP | Important management-facing layer |

| Microsoft Fabric | ADOPT LATER | Strong enterprise data candidate |

| OneLake | ADOPT LATER | Useful within Fabric architecture |

| Microsoft Foundry | ADOPT LATER | Strong managed AI runtime candidate |

| Entra ID / RBAC | ADOPT FOR DEPLOYMENT | Enterprise access control |

| Private networking | ADOPT WHERE JUSTIFIED | Production security control |

| Microsoft Data Formulator | PILOT | Analyst accelerator, not core platform |

| Pre-Decision Safety Checklist | ADOPT | High-value assurance feature |

| AI Model Risk Register | ADOPT | Strong governance control |

| Exception / Severity Triage | ADOPT | High operational value |

| Operational Control Tower | ADOPT | Strong management product concept |

| Recovery / Lessons-Learned Loop | ADOPT LATER | Valuable later-stage capability |

| Industry-specific specialist agents | IGNORE | Unnecessary complexity |



\---



\# 4. Architecture v2



Architecture v2 is defined as:



\*\*A model-flexible, evidence-governed NHS operational intelligence architecture combining structured operational data, smarter retrieval, bounded AI orchestration, deterministic assurance, human review and exception-based management.\*\*



Target flow:



NHS User / Manager

→ Identity + Access

→ Governed Orchestrator

→ Structured Data / Policy Evidence / Analytics Tools

→ Selected Evidence Package

→ Optional Long-Context Reasoning

→ Pre-Decision Safety Check

→ Deterministic Assurance

→ AUTO / REVIEW / ABSTAIN

→ Human Decision

→ Operational Action / Review

→ Recovery Monitoring

→ Lessons Learned



Around the entire system:



\- model risk;

\- change control;

\- versioning;

\- auditability;

\- security.



\---



\# 5. Intelligence Layer



Preferred design:



Strong Orchestrator

\+

Bounded Tools



Avoid:



Large numbers of agents coordinating with other agents without clear need.



The orchestrator may decide:



\- which tools are required;

\- whether retrieval should be refined;

\- whether structured and unstructured evidence are both required;

\- whether long-context reasoning is justified;

\- when enough evidence has been collected.



The deterministic assurance layer remains separate.



\---



\# 6. Retrieval Architecture v2



Preferred retrieval flow:



Hybrid Retrieval

→ Optional Reranker

→ Optional Bounded Agentic Retrieval

→ Relationship-Aware Expansion

→ Lifecycle Filtering

→ Selected Evidence Package

→ Reasoning



Core principle:



\*\*Do not replace a strong hybrid retrieval foundation. Add smarter behaviour around it.\*\*



RAG and long context are complementary:



\*\*RAG finds the right evidence. Long context reasons across a larger selected evidence set. Governance verifies the resulting answer.\*\*



\---



\# 7. Assurance Layer



The assurance layer remains project-owned.



Core controls:



\- scope gating;

\- lifecycle validation;

\- evidence sufficiency;

\- citation verification;

\- high-risk claim checks;

\- relationship validation;

\- corrective false-premise handling;

\- post-generation governance;

\- AUTO\_ANSWER;

\- REVIEW\_REQUIRED;

\- ABSTAIN.



A stronger frontier model must not replace these controls.



\---



\# 8. Enterprise Data and AI Path



\## Current Development Layer



KEEP:



\- Python;

\- PostgreSQL;

\- GitHub;

\- Power BI;

\- synthetic datasets;

\- benchmark datasets;

\- automated tests.



\## Future Enterprise Data Layer



Strong candidate:



Microsoft Fabric

→ OneLake

→ Lakehouse / Warehouse

→ Power BI

→ AI workloads



Fabric is not required for current prototype development.



\## Future Managed AI Runtime



Strong candidate:



Microsoft Foundry



Potential managed responsibilities:



\- model access;

\- hosting;

\- scaling;

\- runtime;

\- deployment;

\- identity integration;

\- monitoring.



The project retains ownership of:



\- NHS workflow logic;

\- evidence rules;

\- safety controls;

\- review routing;

\- evaluation;

\- governance.



\---



\# 9. Security and Access



Future enterprise architecture should consider:



\- Entra ID;

\- RBAC;

\- managed identity;

\- least privilege;

\- private endpoints where justified;

\- network controls;

\- auditability.



Principle:



\*\*The AI should only have access to the data and actions required for the current task.\*\*



The Copilot must inherit and respect authorised user permissions rather than bypass them.



\---



\# 10. NHS Governance Position



The intended system is:



\*\*An operational decision-support system for NHS managers that combines operational data and policy evidence to explain service pressure, retrieve relevant guidance and prepare governed management briefings.\*\*



It is not intended to:



\- diagnose;

\- prescribe;

\- make autonomous treatment decisions;

\- trigger high-risk operational actions without human authority;

\- replace accountable NHS professionals.



Principle:



\*\*AI supports and prepares the decision. The authorised NHS professional remains accountable.\*\*



\---



\# 11. Clinical Safety and Deployment Readiness



The project should continue learning toward DCB0129-style clinical-risk management and understand DCB0160 deployment responsibilities.



Real deployment would require appropriate formal safety, governance and organisational processes.



Potential safety evidence includes:



Clinical Risk Management Plan

→ Hazard Log

→ Risk Controls

→ Test Evidence

→ Residual Risk

→ Clinical Safety Case



The prototype must not claim:



\- NHS approval;

\- clinical safety certification;

\- regulatory compliance;

\- production readiness.



\---



\# 12. Privacy and Information Governance



Core principle:



\*\*Use the minimum data necessary for the operational question.\*\*



Preferred development data:



\- synthetic;

\- anonymised;

\- aggregated where possible.



Future production use requires appropriate:



\- lawful processing;

\- DPIA;

\- access controls;

\- retention controls;

\- auditability;

\- security;

\- organisational approval.



Privacy principle:



\*\*The cheapest sensitive data to govern is the sensitive data that is never ingested.\*\*



\---



\# 13. Cross-Industry Operating Model



Week 20 adopted operating principles from several high-reliability sectors.



\## Aviation



Borrow:



\- structured pre-decision checks;

\- visible readiness state;

\- challenge culture;

\- explicit escalation.



Principle:



\*\*Automate the checks, not the accountability.\*\*



\## Banking



Borrow:



\- model risk register;

\- independent validation;

\- controlled AI change management;

\- usage limits.



\## Cybersecurity



Borrow:



Detect

→ Triage

→ Contain

→ Recover

→ Learn



\## Logistics and Manufacturing



Borrow:



\- control towers;

\- exception management;

\- trend-aware escalation;

\- dependency awareness;

\- root-driver analysis.



\---



\# 14. Five Cross-Pollinated Capabilities



Carry forward:



1\. Operational Control Tower

2\. Exception / Severity Triage

3\. Pre-Decision Safety Checklist

4\. AI Model Risk \& Change Register

5\. Recovery / Lessons-Learned Loop



These should remain capabilities inside the existing architecture rather than becoming separate industry-specific agents.



\---



\# 15. Final Operating Model



The emerging product workflow is:



\*\*Detect → Prioritise → Explain → Verify → Human Decide → Learn\*\*



This becomes a central operating principle for the future NHS Sovereign Operational Intelligence \& Evidence Copilot.



\---



\# 16. Emerging USP



The project is evolving toward:



\*\*A governed NHS operational control tower that detects meaningful exceptions, explains their likely drivers, retrieves relevant policy evidence, verifies the safety of the briefing and directs scarce management attention to cases that genuinely require human judgement.\*\*



This differentiates the project from:



\- generic dashboards;

\- prediction-only systems;

\- ordinary chatbots;

\- simple policy search.



\---



\# 17. Week 21 — MUST BUILD NEXT



Priority order:



1\. Dedicated reranker evaluation

2\. Bounded agentic retrieval

3\. Relationship-aware retrieval

4\. Cleaner orchestrator

5\. Architecture v2 integration testing

6\. Architecture v1 vs v2 benchmark



Week 21 central question:



\*\*Does Architecture v2 retrieve better evidence than Architecture v1 without increasing unsafe behaviour?\*\*



\---



\# 18. SHOULD BUILD LATER



Defer:



\- Fabric enterprise migration;

\- Foundry deployment;

\- Entra / enterprise RBAC integration;

\- private-network architecture;

\- full Operational Control Tower UI;

\- recovery monitoring;

\- lessons-learned workflow;

\- production model-risk workflow;

\- independent external validation;

\- real NHS production-data testing.



Design for these capabilities now without prematurely implementing them.



\---



\# 19. DO NOT BUILD



Do not currently build:



\- full GraphRAG infrastructure;

\- agent swarms;

\- aviation agent;

\- banking agent;

\- cybersecurity agent;

\- logistics agent;

\- autonomous operational actions;

\- autonomous escalation;

\- complex production infrastructure before evidence justifies it;

\- model-based replacements for deterministic assurance controls.



\---



\# 20. Architecture v2 Success Metrics



\## Technical



Track:



\- Top-1 retrieval accuracy;

\- Top-k retrieval accuracy;

\- reranker uplift;

\- agentic retrieval success;

\- relationship-aware retrieval success;

\- latency;

\- model calls;

\- token usage;

\- failure rate;

\- regression test pass rate.



\## Governance



Track:



\- citation accuracy;

\- unsupported claim rate;

\- false acceptance;

\- false rejection;

\- lifecycle violations;

\- high-risk claim escapes;

\- incorrect relationship reasoning;

\- false-premise correction accuracy;

\- appropriate abstention;

\- appropriate review routing.



\## Operational



Track:



\- management-briefing preparation time;

\- policy-search time;

\- investigation time;

\- number of manual sources checked;

\- number of analyst handoffs;

\- time to identify likely root driver;

\- time from signal to escalation;

\- user usefulness rating.



\## Economic



Track:



\- analyst minutes saved;

\- manager minutes saved;

\- cost per governed query;

\- briefing preparation cost;

\- model/token cost;

\- infrastructure cost;

\- unnecessary escalations avoided;

\- duplicated investigations avoided.



\## Management Attention



Track:



\- alerts generated;

\- useful alerts;

\- suppressed normal variation;

\- unnecessary escalations;

\- manager time spent reviewing low-value signals.



\## Human Oversight



Track:



\- REVIEW\_REQUIRED outcomes;

\- reviewer overrides;

\- reviewer disagreement;

\- AUTO\_ANSWER issues;

\- ABSTAIN resolutions.



\## Model Replaceability



When changing model:



\- retrieval quality;

\- safety;

\- latency;

\- cost;

\- governance stability



should be compared.



\---



\# 21. Final Week 20 Decision



Architecture v1 is not being discarded.



Its assurance layer becomes the foundation of Architecture v2.



Architecture v2 adds:



\- smarter retrieval;

\- simpler orchestration;

\- selective long-context reasoning;

\- enterprise deployment direction;

\- stronger identity/security thinking;

\- NHS governance readiness;

\- operational exception management;

\- economic and management-attention metrics.



Final principle:



\*\*Better evidence with equal or stronger governance.\*\*



The success of Architecture v2 will not be judged by how much AI it contains.



It will be judged by whether it:



\- retrieves stronger evidence;

\- produces safer outputs;

\- reduces unnecessary work;

\- protects management attention;

\- preserves human accountability;

\- remains economically sensible.



\---



\# 22. Week 20 Closeout



Week 20 Technology \& Architecture Refresh Gate:



\*\*COMPLETE\*\*



Next phase:



\## Week 21 — Architecture v2 Retrieval Upgrade



Initial engineering priorities:



1\. reranking;

2\. bounded agentic retrieval;

3\. relationship-aware retrieval;

4\. orchestrator simplification;

5\. regression testing;

6\. Architecture v1 vs v2 evaluation.

