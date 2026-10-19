\# Week 26 Day 1 Closeout — Adversarial Hardening Design



\## Objective



Week 26 Day 1 focused on expanding the citation and faithfulness threat model beyond the stable Week 25 benchmark.



No production logic was changed.



The purpose was to define the next adversarial assurance layer before implementation.



\## Core Principle



> Passing the existing benchmark is necessary, but not sufficient.



\## Work Completed



\### 1. Adversarial Threat Model



Defined new Week 26 threat classes including:



\- multi-source Frankenstein support;

\- citation flooding;

\- claim segmentation;

\- version-chain ambiguity;

\- temporal validity failure;

\- authority inference;

\- role-responsibility hallucination;

\- subtle modal strengthening;

\- prompt injection inside retrieved evidence;

\- long-answer partial grounding;

\- unsafe abstention formatting;

\- conflict compression.



\### 2. Benchmark Case Design



Designed 12 new adversarial benchmark cases:



\- W26-C001 — Frankenstein multi-source support

\- W26-C002 — Citation flooding

\- W26-C003 — Claim segmentation attack

\- W26-C004 — Superseded + active version chain

\- W26-C005 — Temporal validity failure

\- W26-C006 — Authority inference

\- W26-C007 — Role-responsibility hallucination

\- W26-C008 — Subtle modal strengthening

\- W26-C009 — Prompt injection inside evidence

\- W26-C010 — Long-answer partial grounding

\- W26-C011 — Unsafe abstention formatting

\- W26-C012 — Conflict compression



These cases remain design specifications until the Week 26 benchmark contract is finalised.



\### 3. Relationship-Aware Groundedness



Defined a stronger grounding model that separates:



\- claim materiality;

\- source-level support;

\- evidence relationship;

\- composite support;

\- final groundedness decision.



Proposed states include:



\- GROUNDED\_SINGLE\_SOURCE

\- GROUNDED\_MULTI\_SOURCE

\- PARTIALLY\_GROUNDED

\- UNGROUNDED

\- CONFLICT\_BLOCKED

\- RELATIONSHIP\_UNVERIFIED

\- NOT\_APPLICABLE



The design specifically prevents unrelated evidence fragments from creating artificial support.



\### 4. Version and Temporal Precedence



Defined reasoning requirements for:



\- ACTIVE;

\- SUPERSEDED;

\- DRAFT;

\- ARCHIVED;

\- effective dates;

\- superseded dates;

\- replacement relationships;

\- historical questions;

\- conflicting active documents.



Key principle:



> Recency is not the same as authority.



\### 5. Abstention Hardening



Defined controls to prevent hidden operational advice inside:



\- reason;

\- missing\_information;

\- what\_is\_needed\_to\_continue;

\- other abstention sections.



Proposed failure states include:



\- DIRECTIVE\_LEAKAGE

\- AUTHORITY\_LEAKAGE

\- UNSUPPORTED\_CERTAINTY

\- ACTION\_ASSUMPTION

\- INVALID\_ABSTENTION\_STRUCTURE



\### 6. Prompt-Injection Trust Boundary



Defined a strict separation between:



\#### Trusted control plane



\- governance;

\- application policy;

\- answer contract;

\- precedence;

\- assurance logic.



\#### Untrusted evidence plane



\- retrieved text;

\- uploaded documents;

\- OCR text;

\- external content.



Retrieved evidence may provide facts.



Retrieved evidence may not redefine system rules.



\## Day 1 Architecture Decision



Do not immediately modify the stable Week 25 production assurance stack.



Week 26 will use staged hardening:



1\. define the new benchmark contract;

2\. encode adversarial cases;

3\. build standalone Week 26 evaluators;

4\. compare them with Week 25 behaviour;

5\. integrate only after regression evidence is green.



This protects the existing 18 Week 25 benchmark cases as regression anchors.



\## Day 1 Acceptance Criteria



Day 1 is complete when:



\- existing Week 25 benchmark remains unchanged;

\- 12 new adversarial case designs exist;

\- relationship-aware groundedness is defined;

\- version and temporal precedence rules are defined;

\- abstention-hardening rules are defined;

\- prompt-injection trust boundaries are defined;

\- no production code has been weakened;

\- documentation passes Git whitespace validation.



\## Week 26 Day 1 Status



\*\*COMPLETE\*\*



\## Next



Week 26 Day 2:



\- define the Week 26 benchmark data contract;

\- create the separate Week 26 adversarial benchmark JSON;

\- validate case IDs and expected outcomes;

\- ensure Week 25 and Week 26 benchmarks remain independently auditable.

