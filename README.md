# Healthcare Document Intelligence RAG

## Project Overview

Healthcare Document Intelligence RAG is a governed operational evidence assistant designed for NHS-style environments.

Its purpose is to help operational staff find current guidance, understand which evidence supports a response, and avoid unsupported or unsafe automation when the available evidence is weak, conflicting, superseded, out of scope, or requires human review.

The project is not designed as a generic chatbot.

It is designed as a controlled evidence workflow for operational guidance.

---

## NHS Operational Problem

Operational teams may need to work across multiple documents such as:

- escalation policies
- workforce procedures
- bed-capacity guidance
- winter-pressure plans
- ambulance handover guidance
- severe-weather plans
- business-continuity procedures
- operational governance standards

Common risks include:

- time lost searching multiple documents
- staff finding outdated guidance
- inconsistent interpretation
- weak provenance
- uncertainty about which source supported a conclusion
- conflicting or superseded documents being combined incorrectly
- AI systems generating plausible but unsupported responses
- automation continuing when human review is more appropriate

This project addresses those risks through governed retrieval, structured evidence, provenance verification, precedence assessment and explicit human-review controls.

---

## Current System Capability

The current prototype can:

- ingest synthetic operational documents
- preserve lifecycle and source metadata
- split documents into traceable evidence chunks
- generate semantic embeddings
- perform semantic, keyword and hybrid retrieval
- enforce query-scope controls
- exclude inappropriate lifecycle states from normal evidence use
- detect stale or inconsistent evidence metadata
- rank and rerank candidate evidence
- stop when evidence is insufficient
- use bounded retrieval refinement where appropriate
- create structured Evidence Objects
- build question-level Evidence Packets
- verify evidence provenance against a canonical document register
- summarise lifecycle state
- assess conflict, supersession and precedence
- distinguish safe evidence combination from answer authority
- preserve existing governance decisions
- route cases to `AUTO_ANSWER`, `REVIEW_REQUIRED` or `ABSTAIN`
- produce deterministic manager-facing evidence briefs
- prevent manager-ready status when governance or evidence conditions are unsafe
- record benchmark and audit outputs
- run regression tests across the full project

---

## Plain-English Example

A manager asks:

> How should severe weather pressure and ambulance handover disruption be considered together?

The system can:

1. check whether the question is within the approved operational domain
2. retrieve relevant current evidence
3. assess whether the available evidence is sufficient
4. convert retrieved chunks into structured Evidence Objects
5. verify where each piece of evidence came from
6. check lifecycle status
7. assess whether the evidence can safely be combined
8. apply governance rules
9. create a manager-readable evidence brief
10. require human review when automation is not appropriate

If the evidence is weak, out of scope or unsuitable for automatic use, the system abstains or routes the case for review rather than guessing.

---

## Architecture

```mermaid
flowchart TD
    A[Operational Documents] --> B[Document Ingestion]
    B --> C[Cleaning and Metadata]
    C --> D[Chunking]
    D --> E[Embeddings and Retrieval]

    E --> F[Scope Gate]
    F --> G[Architecture v2 Retrieval Orchestrator]

    G --> H1[Return Initial Evidence]
    G --> H2[Hybrid Rescue]
    G --> H3[Bounded Agentic Retrieval]
    G --> H4[Stop Insufficient]
    G --> H5[Stop Out of Scope]

    H1 --> I[Evidence Sufficiency]
    H2 --> I
    H3 --> I

    I --> J[Structured Evidence Objects]
    J --> K[Evidence Packet]
    K --> L[Provenance Verification]
    L --> M[Lifecycle Assessment]
    M --> N[Conflict / Supersession / Precedence]
    N --> O[Governance]

    O --> P1[AUTO_ANSWER]
    O --> P2[REVIEW_REQUIRED]
    O --> P3[ABSTAIN]

    P1 --> Q[Manager Evidence Brief]
    P2 --> Q
    P3 --> Q

    Q --> R1[BRIEF_READY]
    Q --> R2[BRIEF_REVIEW_REQUIRED]
    Q --> R3[BRIEF_UNAVAILABLE]

## Week 23 ? Grounded Communication v2

Week 23 extended the governed evidence workflow into a controlled communication layer.

The end-to-end architecture is now:

Retrieval
-> Evidence Packet
-> Answer Contract
-> Answer Context
-> Grounded Response
-> Claim-to-Citation Linking
-> Review / Abstention UX

### Frozen 75-Case Benchmark

The complete Week 23 communication stack was evaluated across the frozen benchmark.

Results:

- 75 total cases
- 14 AUTO_ANSWER
- 33 REVIEW_REQUIRED
- 28 ABSTAIN
- 141 supported claims
- 0 unsupported claims
- 141 citations used
- 3.0 average citations per AUTO_ANSWER
- 3.0 average supported claims per AUTO_ANSWER
- 33 manager review UX cases
- 28 safe abstention UX cases

### Safety Results

The benchmark produced:

- 0 governance overrides
- 0 expected-abstention auto-answers
- 0 review cases presented as authoritative
- 0 abstention evidence leaks
- 0 unsupported material claims
- 0 unknown citations
- 0 lifecycle-unsafe automated citations
- 0 unsafe cases overall

**Week 23 benchmark result: SAFETY PASS**

Full regression:

**690 tests passed**

### Why This Matters

The project is no longer simply a healthcare document retrieval system.

It now demonstrates:

- governed answer permissions
- evidence-grounded communication
- claim-level citation traceability
- human-review preservation
- safe abstention
- lifecycle-aware evidence use
- auditable manager-facing outputs

The current progression is:

**Smart Retrieval -> Trusted Evidence -> Trusted Communication**

### Current Limitation

The grounded-generation layer is currently deterministic.

This is intentional and provides a controlled safety baseline before introducing live LLM-assisted generation.

The current zero-unsupported-claim result therefore applies to the deterministic benchmarked communication layer and should not be interpreted as proof that an unrestricted LLM would always produce zero unsupported claims.

Future LLM-assisted generation must pass the same governance, citation and safety benchmark before promotion.
