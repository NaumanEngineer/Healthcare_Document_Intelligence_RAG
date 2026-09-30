\# Week 20 Day 3 — Microsoft Fabric, Azure and Enterprise Deployment Review



\## Objective



Review which parts of the current NHS AI architecture should remain local/open-source and which parts should move toward enterprise-grade Microsoft infrastructure.



The review focuses on:



\- local development;

\- PostgreSQL;

\- Microsoft Fabric;

\- OneLake;

\- Lakehouse / Warehouse patterns;

\- Power BI;

\- Microsoft Foundry;

\- managed agent runtime;

\- Microsoft Entra ID;

\- managed identity;

\- RBAC;

\- private networking;

\- auditability;

\- enterprise deployment.



The goal is not to move everything to cloud.



The goal is to identify where managed Microsoft infrastructure adds genuine operational, security and economic value.



\---



\## Core Day 3 Principle



\*\*Prototype locally. Industrialize selectively.\*\*



Local development remains useful for:



\- rapid experimentation;

\- low-cost iteration;

\- debugging;

\- synthetic data;

\- unit testing;

\- benchmarking;

\- governance logic development.



Cloud infrastructure should be introduced where it adds:



\- enterprise scale;

\- shared access;

\- security;

\- identity;

\- managed runtime;

\- monitoring;

\- resilience;

\- governed data access.



\---



\## Current Local Architecture



Current development stack:



Synthetic / operational data

→ PostgreSQL

→ SQL analysis

→ Python retrieval and governance

→ RAG / evidence pipeline

→ local testing

→ GitHub



This remains a strong development and learning environment.



\---



\## Keep Local



Decision:



KEEP LOCAL FOR DEVELOPMENT



Components:



\- Python development;

\- governance logic;

\- retrieval experiments;

\- synthetic datasets;

\- benchmark datasets;

\- unit tests;

\- regression tests;

\- rapid prototypes;

\- GitHub workflow.



Reason:



These components benefit from:



\- low cost;

\- fast iteration;

\- direct debugging;

\- full control;

\- reproducibility.



\---



\## PostgreSQL



Decision:



KEEP



Role:



PostgreSQL remains valuable for:



\- relational modelling;

\- SQL learning;

\- operational database design;

\- constraints;

\- data quality;

\- reproducible analysis;

\- local prototyping.



Microsoft Fabric should not be treated as a replacement for PostgreSQL at this stage.



Preferred interpretation:



PostgreSQL

= operational / prototype database



Fabric

= future enterprise analytics and integration layer



\---



\## Microsoft Fabric



Decision:



STRONG ENTERPRISE ADOPTION CANDIDATE



Fabric should be understood as a future enterprise data platform rather than a replacement for current learning tools.



Potential role:



Multiple operational data sources

→ Fabric ingestion / pipelines

→ OneLake

→ governed data products

→ Power BI

→ AI



Potential source domains:



\- A\&E;

\- beds;

\- workforce;

\- incidents;

\- weather;

\- finance;

\- operational performance.



\---



\## OneLake



Role:



Provide a common enterprise analytics data layer.



Potential value:



\- shared governed data;

\- reduced unnecessary duplication;

\- common source for Power BI and AI;

\- easier reuse across analytical workloads.



Preferred principle:



\*\*Power BI and AI should consume trusted governed data rather than maintaining separate uncontrolled copies.\*\*



\---



\## Fabric Operational Value



Potential operational improvements:



\- fewer disconnected data pipelines;

\- reduced manual reconciliation;

\- easier reuse of trusted datasets;

\- simpler integration with Power BI;

\- shared data governance;

\- improved lineage.



The value of Fabric should be judged by whether it reduces operational complexity and analyst effort.



\---



\## Fabric Economic Value



Fabric introduces platform cost.



Potential economic value comes from reducing:



\- duplicate infrastructure;

\- repeated data movement;

\- maintenance effort;

\- manual integration;

\- analyst reconciliation time;

\- separate reporting pipelines.



Economic question:



\*\*Does the reduction in engineering and operational complexity justify the platform cost?\*\*



This should be measured rather than assumed.



\---



\## Fabric Learning Decision



For the current training roadmap:



Fabric awareness

→ IMPORTANT



Fabric mastery immediately

→ NOT REQUIRED



Hands-on mini-project

→ YES



Future enterprise data layer

→ STRONG CANDIDATE



Power BI integration

→ HIGH VALUE



AI + governed operational data

→ HIGHLY RELEVANT



\---



\## Microsoft Foundry



Decision:



STRONG ENTERPRISE AI ADOPTION CANDIDATE



Foundry should be considered the future managed AI runtime for:



\- hosted orchestrator;

\- model access;

\- tool orchestration;

\- managed identity;

\- deployment;

\- monitoring;

\- session/runtime infrastructure.



\---



\## What Foundry Should Replace



Potentially managed by Microsoft:



\- hosting;

\- scaling;

\- model access;

\- session persistence;

\- runtime infrastructure;

\- deployment management;

\- identity plumbing;

\- monitoring.



This reduces the need to build undifferentiated AI infrastructure manually.



\---



\## What Foundry Should Not Replace



Keep ownership of:



\- NHS-specific workflow logic;

\- evidence sufficiency;

\- citation verification;

\- lifecycle controls;

\- high-risk claim validation;

\- evidence-set reasoning;

\- corrective false-premise handling;

\- AUTO / REVIEW / ABSTAIN logic;

\- human-review routing;

\- evaluation.



These are core project assets.



\---



\## Enterprise Identity



Microsoft Entra ID should be the future identity layer.



User pattern:



NHS user

→ Entra authentication

→ role / permission check

→ authorised tools and data



AI pattern:



Foundry agent

→ managed identity

→ only approved resources



Core principle:



\*\*The AI should not have a master key to all organisational data.\*\*



Use least-privilege access.



\---



\## RBAC



Role-based access should control:



\- who can use the system;

\- who can manage the system;

\- what datasets can be accessed;

\- what operations each user can perform.



Different users may require different data access.



Example:



Trust analyst

→ operational data



Workforce manager

→ workforce data



Senior operational manager

→ broader system view



Administrator

→ system configuration



\---



\## Data Permission Principle



Application access and data access are separate concerns.



A user may be authorised to use the Copilot but not authorised to see every dataset.



The AI must respect the user's underlying data permissions.



Bad design:



User cannot see data directly

but

AI can retrieve and reveal it.



Preferred design:



User identity

→ permissions

→ authorised data only

→ AI reasoning

→ answer within same access boundary.



\---



\## Private Networking



Decision:



IMPORTANT FOR ENTERPRISE TARGET



Potential controls:



\- private endpoints;

\- VNet isolation;

\- restricted outbound access;

\- no public egress where justified.



Purpose:



Keep sensitive data traffic inside controlled enterprise routes.



\---



\## Auditability



Future enterprise deployment should make it possible to answer:



\- who asked the question;

\- when it was asked;

\- what data was accessed;

\- which documents were used;

\- which model was used;

\- what answer was returned;

\- whether human review was triggered;

\- whether the system abstained.



This aligns strongly with the existing governance architecture.



\---



\## Security Economic Interpretation



Security introduces implementation cost.



However, weak security can create significantly larger costs through:



\- remediation;

\- deployment delays;

\- data exposure;

\- compliance investigation;

\- trust loss;

\- duplicated manual controls.



Preferred principle:



\*\*Build security into the architecture instead of relying on repeated manual workarounds.\*\*



\---



\## Target Hybrid Architecture



\### Development Layer



Local development:



\- Python;

\- governance logic;

\- retrieval experiments;

\- synthetic data;

\- unit and regression tests;

\- GitHub.



\### Enterprise Data Layer



Microsoft Fabric:



\- OneLake;

\- pipelines;

\- Lakehouse / Warehouse;

\- governed operational data;

\- Power BI.



\### Enterprise AI Layer



Microsoft Foundry:



\- hosted orchestrator;

\- model access;

\- approved tools;

\- managed runtime;

\- identity;

\- monitoring.



\### Assurance Layer



Project-owned:



\- lifecycle validation;

\- evidence sufficiency;

\- citation verification;

\- high-risk claim guard;

\- evidence-set reasoning;

\- false-premise correction;

\- AUTO / REVIEW / ABSTAIN.



\### Access Layer



Microsoft Entra ID + RBAC:



\- identity;

\- least privilege;

\- authorised data access;

\- role-based permissions.



\### Networking Layer



Where justified:



\- private endpoints;

\- VNet isolation;

\- restricted outbound access.



\---



\## Target Flow



NHS User

→ Entra ID

→ Role / Permission Check

→ Foundry-Hosted Orchestrator

→ Approved Tools

→ Fabric / OneLake

\+ Policy Retrieval

→ Evidence Package

→ Project Assurance Layer

→ AUTO\_ANSWER / REVIEW\_REQUIRED / ABSTAIN

→ Audited NHS Manager Response



\---



\## Structured Data and Policy Evidence



The future Copilot should combine two major evidence domains.



\### Structured Operational Data



Fabric:



\- beds;

\- A\&E;

\- workforce;

\- incidents;

\- weather;

\- finance;

\- operational metrics.



\### Document Evidence



RAG / retrieval:



\- policies;

\- procedures;

\- escalation guidance;

\- governance documents.



The orchestrator should bring both together.



Example question:



"Why is operational pressure high today and what policy applies?"



Potential flow:



query structured data

→ retrieve relevant policy

→ combine evidence

→ run assurance

→ generate governed briefing.



\---



\## Day 3 Decision Table



| Component | Decision |

|---|---|

| Python local development | KEEP LOCAL |

| Governance logic | KEEP OWNERSHIP |

| Unit / regression tests | KEEP LOCAL |

| Synthetic data | KEEP LOCAL |

| PostgreSQL | KEEP |

| GitHub | KEEP |

| Microsoft Fabric | STRONG FUTURE ADOPTION CANDIDATE |

| OneLake | FUTURE ENTERPRISE DATA LAYER |

| Power BI | KEEP |

| Fabric pipelines | ADOPT LATER |

| Microsoft Foundry | STRONG FUTURE ADOPTION CANDIDATE |

| Foundry-hosted orchestrator | ADOPT LATER |

| Managed model access | ADOPT LATER |

| Managed identity | ENTERPRISE REQUIREMENT |

| Microsoft Entra ID | ENTERPRISE REQUIREMENT |

| RBAC | ENTERPRISE REQUIREMENT |

| Private endpoints | IMPORTANT WHERE JUSTIFIED |

| VNet isolation | IMPORTANT WHERE JUSTIFIED |

| Custom agent runtime | REDUCE / REPLACE WHERE MANAGED SERVICES ADD VALUE |

| Full cloud migration now | DEFER |



\---



\## Economic Architecture Principle



The architecture should separate:



\### What the project should own



\- NHS-specific business logic;

\- evidence rules;

\- governance;

\- evaluation;

\- workflow design;

\- human-review logic.



\### What managed platforms may provide



\- hosting;

\- scaling;

\- identity infrastructure;

\- networking;

\- model access;

\- runtime;

\- monitoring.



Core principle:



\*\*Spend engineering effort on the parts that differentiate the NHS product. Use managed infrastructure for commodity platform work where economically justified.\*\*



\---



\## Emerging Enterprise USP



The project is evolving toward:



\*\*A governed NHS operational intelligence platform where Microsoft Fabric provides trusted operational data, Microsoft Foundry runs the AI workflow, and a project-owned assurance layer determines whether outputs are safe enough to use.\*\*



This is not intended to replace accountable NHS managers.



The system should reduce the time required to:



\- gather evidence;

\- reconcile operational data;

\- search policy;

\- prepare briefings;

\- identify escalation issues.



The manager retains accountability for the final decision.



\---



\## Day 3 Final Principle



\*\*Prototype locally. Industrialize selectively. Keep ownership of the NHS-specific assurance layer.\*\*



\---



\## Next Review



Day 4 will focus on:



\- healthcare regulation;

\- NHS AI governance;

\- clinical safety;

\- DCB0129 / DCB0160 relevance;

\- DPIA;

\- human oversight;

\- auditability;

\- procurement and deployment expectations.



Central question:



\*\*Is the project merely technically impressive, or is it being designed in a way that could survive real NHS governance and deployment scrutiny?\*\*

