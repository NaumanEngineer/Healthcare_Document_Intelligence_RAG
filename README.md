# Healthcare Document Intelligence RAG

## Governed Operational Evidence Assistant for NHS-Style Environments

Healthcare Document Intelligence RAG is a governed retrieval-augmented generation system designed for operational policy and guidance workflows in NHS-style environments.

It helps users retrieve relevant approved evidence, assess whether that evidence is sufficient and safe to use, preserve provenance and lifecycle controls, and produce one of three governed outcomes:

- `ANSWER`
- `REVIEW_REQUIRED`
- `ABSTAIN`

The project is deliberately **not designed as a generic chatbot**.

It is designed as a controlled evidence and communication workflow where retrieval, generation and presentation remain bounded by governance and assurance.

---

# NHS Operational Problem

Operational teams may need to work across multiple documents such as:

- escalation policies
- workforce procedures
- bed-capacity guidance
- winter-pressure plans
- ambulance handover guidance
- severe-weather plans
- business-continuity procedures
- operational governance standards

Common operational risks include:

- staff spending time searching across multiple documents
- use of outdated or superseded guidance
- inconsistent interpretation
- weak provenance
- uncertainty about which source supports a conclusion
- incorrect combination of conflicting evidence
- AI systems generating plausible but unsupported responses
- automation continuing when human review is more appropriate

This project addresses those risks through governed retrieval, structured evidence, provenance verification, precedence assessment, controlled generation, citation assurance, faithfulness checks and explicit human-review controls.

---

# What the System Does

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
- assess document lifecycle state
- assess conflict, supersession and precedence
- distinguish evidence relevance from answer authority
- apply pre-generation governance
- build controlled answer contexts
- support deterministic generation
- support optional provider-neutral model execution
- validate model outputs before release
- fall back safely when provider execution fails or is rejected
- verify citations
- test claim-to-evidence faithfulness
- resist unsupported overstatement
- apply post-generation governance
- produce safe manager-facing responses
- expose structured observability
- preserve authority across all presentation layers
- route outcomes to `ANSWER`, `REVIEW_REQUIRED` or `ABSTAIN`
- run a deterministic three-outcome portfolio demonstration
- reproduce the application from a clean Python environment
- run automated regression testing across the full repository

---

# Current Canonical Architecture

```text
Question
    ↓
Input Validation
    ↓
Query Scope Gate
    ↓
Retrieval Orchestrator
    ↓
Evidence Sufficiency
    ↓
Structured Evidence
    ↓
Evidence Packet
    ↓
Provenance Verification
    ↓
Lifecycle / Precedence Assessment
    ↓
Pre-Generation Governance
    ↓
Answer Contract
    ↓
Answer Context
    ↓
Controlled Generation
    ↓
Optional Provider-Neutral Model Execution
    ↓
Model Output Validation
    ↓
Deterministic Fallback if Required
    ↓
Claim / Citation Assurance
    ↓
Faithfulness / Safety Assurance
    ↓
Post-Generation Governance
    ↓
Final Governed Outcome
    ↓
Manager-Facing Presentation
    ↓
ANSWER / REVIEW_REQUIRED / ABSTAIN
```

The governing principle is:

> **The model is optional. The assurance path is not.**

---

# Three Governed Outcomes

## ANSWER

The system may release an answer when:

- the question is within scope
- approved evidence is available
- evidence is sufficiently grounded
- provenance and lifecycle requirements are satisfied
- governance permits answer release
- citation and faithfulness controls pass
- downstream presentation does not increase authority

The manager-facing layer may display the supported answer and its existing citations.

---

## REVIEW_REQUIRED

The system routes a case for human review when relevant evidence exists but automatic authoritative release is not appropriate.

Examples may include:

- cross-document interpretation
- precedence uncertainty
- evidence relationships requiring judgement
- assurance restrictions
- governance conditions requiring human oversight

The manager-facing presentation does **not** convert this state into an answer.

---

## ABSTAIN

The system refuses to provide a substantive answer when sufficient approved evidence is unavailable or the governed pipeline cannot safely support release.

The application must not manufacture:

- evidence
- citations
- unsupported conclusions
- false confidence

The safe response instead explains that additional approved evidence or appropriate human review is required.

---

# Week 28 Portfolio Demo

The current deterministic portfolio demonstration exercises all three governed outcomes through the real application pipeline.

Run:

```powershell
python -m src.application.week28_demo_runner
```

Expected cases:

```text
W28-DEMO-ANSWER-001
Actual outcome: ANSWER

W28-DEMO-REVIEW-001
Actual outcome: REVIEW_REQUIRED

W28-DEMO-ABSTAIN-001
Actual outcome: ABSTAIN
```

Expected summary:

```text
Cases: 3
Governance matched: 3
Presentation matched: 3
Authority preserved: 3
Overall verification: PASS
```

The demo uses synthetic, non-patient evidence.

Expected outcomes are used only for verification. They are not passed into governance to force the result.

---

# Manager-Facing Response Layer

The final governed result is converted into a management-friendly response without increasing authority.

Stable presentation fields include:

```text
outcome
headline
summary
answer
evidence_basis
confidence_message
next_action
human_review_required
citations
limitations
```

Presentation follows one core rule:

> **Improve presentation, not authority.**

For example:

- an `ANSWER` may contain a supported answer
- `REVIEW_REQUIRED` must not become an answer
- `ABSTAIN` must remain an abstention
- citations are preserved rather than invented
- presentation failures fail closed

---

# Safety and Assurance

The project contains layered assurance developed across the retrieval, evidence, generation and communication stack.

Key controls include:

- query-scope checking
- evidence sufficiency
- provenance verification
- lifecycle validation
- document precedence
- supersession handling
- citation verification
- citation completeness checks
- multi-source evidence assurance
- groundedness checks
- overstatement resistance
- hallucination resistance
- high-risk claim protection
- authority-preserving governance
- prompt-injection resistance
- safe abstention behaviour
- fail-closed execution
- deterministic fallback
- post-generation governance

The project also contains adversarial tests covering cases such as:

- unsupported evidence combinations
- citation flooding
- partial grounding
- superseded guidance
- temporal failures
- authority inference
- role hallucination
- modal strengthening
- prompt injection
- unsafe abstention
- conflict compression

The Week 25-26 assurance layer is treated as a protected subsystem rather than repeatedly rewritten during later application-polish work.

---

# Safe Observability

The application includes structured observability for governed execution.

Observability may describe:

- request lifecycle
- retrieval completion
- governance
- generation
- assurance
- final outcome
- controlled failures

It follows the principle:

> **Observability may describe a governed decision. Observability must never change that governed decision.**

The portfolio path avoids logging raw patient information, raw prompts, model credentials or unrestricted internal evidence content.

---

# Reproducibility

The project is designed so that a reviewer can reproduce its core governed behaviour locally without:

- NHS credentials
- patient data
- API keys
- production databases
- external model credentials
- private infrastructure

The deterministic portfolio path is intended to be reproducible from a clean Python environment.

Validated development baseline:

```text
Python 3.14.1
```

---

# Quick Start — Windows PowerShell

## 1. Clone the repository

```powershell
git clone https://github.com/NaumanEngineer/Healthcare_Document_Intelligence_RAG.git
cd Healthcare_Document_Intelligence_RAG
```

---

## 2. Create a virtual environment

```powershell
python -m venv ".venv"
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Confirm:

```powershell
python --version
```

---

## 3. Upgrade packaging tools

```powershell
python -m pip install --upgrade pip setuptools wheel
```

---

## 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

The Week 28 reproducibility baseline explicitly declares the project dependencies required by the repository.

---

## 5. Audit repository dependencies

```powershell
python scripts\audit_dependencies.py
```

Expected ending:

```text
Candidate count: 9
Missing locally: 0

Dependency audit: PASS
```

The audit maps Python import names to package distribution names where necessary.

For example:

```text
fitz → PyMuPDF
rank_bm25 → rank-bm25
sentence_transformers → sentence-transformers
sklearn → scikit-learn
```

---

## 6. Run the portfolio demo

```powershell
python -m src.application.week28_demo_runner
```

Expected final result:

```text
Cases: 3
Governance matched: 3
Presentation matched: 3
Authority preserved: 3
Overall verification: PASS
```

---

# Automated Verification

## Focused Week 28 Verification

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force ".pytest_tmp" | Out-Null
```

Then:

```powershell
python -m pytest -q `
"tests\test_week28_demo_data.py" `
"tests\test_week28_demo_dependencies.py" `
"tests\test_week28_demo_runner.py" `
"tests\test_week28_manager_response.py" `
--basetemp=".pytest_tmp\week28_clean_room" `
-p no:cacheprovider
```

Validated Week 28 result:

```text
59 passed
```

---

## Full Repository Regression

```powershell
Remove-Item -Recurse -Force ".pytest_tmp" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force ".pytest_tmp" | Out-Null
```

Then:

```powershell
python -m pytest -q `
--basetemp=".pytest_tmp\full_repo" `
-p no:cacheprovider
```

Validated clean-environment regression:

```text
1639 passed
```

---

# Clean-Room Reproducibility Proof

Week 28 validation was performed using a fresh isolated Python environment.

The sequence was:

```text
Fresh Python virtual environment
        ↓
Install from requirements.txt
        ↓
Dependency import verification
        ↓
Repository dependency audit
        ↓
Week 28 three-outcome demo
        ↓
59 focused Week 28 tests
        ↓
1639 full repository tests
```

The clean environment reproduced:

```text
ANSWER
REVIEW_REQUIRED
ABSTAIN
```

with:

```text
Overall verification: PASS
```

and:

```text
1639 passed
```

This provides evidence that the portfolio behaviour is reproducible independently of the developer's pre-existing global Python environment.

---

# Runtime Configuration

Example configuration:

```text
config/runtime_config.example.json
```

Runtime configuration controls settings such as:

- retrieval depth
- retrieval thresholds
- execution mode
- runtime metadata
- assurance policy

Supported execution modes include:

```text
DETERMINISTIC_ONLY
CONTROLLED_PROVIDER
```

The deterministic path is the preferred portfolio and reproducibility mode.

Runtime configuration is not intended to provide a mechanism for weakening mandatory assurance controls.

---

# Application Entry Point

The canonical application CLI can be inspected with:

```powershell
python -m src.application.app --help
```

Typical interface:

```text
--question
--config
--query-date
--log-jsonl
```

The CLI is an application boundary.

It does not duplicate:

- retrieval logic
- evidence construction
- governance
- assurance
- generation policy

Those remain inside the application architecture.

---

# Dependency Audit

The repository includes:

```text
scripts/audit_dependencies.py
```

The script scans:

```text
src/
tests/
```

and identifies direct third-party imports.

It separates:

- standard-library modules
- project-local modules
- third-party dependency candidates

It also reports installed package versions and fails when required package distributions are unavailable.

This prevents the dependency declaration from becoming a manually maintained guess.

---

# Core Technology Stack

The project currently uses technologies including:

- Python
- NumPy
- Sentence Transformers
- PyTorch
- scikit-learn
- BM25
- PyMuPDF
- DuckDB
- PyArrow
- pytest
- Git / GitHub

The architecture intentionally separates:

- retrieval
- evidence construction
- governance
- generation
- assurance
- observability
- user-facing presentation

---

# Synthetic Data and Safety Disclaimer

This repository is a portfolio and engineering prototype.

The demonstration corpus is synthetic.

It does not require or contain real patient data for the portfolio demonstration.

The project is not:

- a medical diagnostic tool
- a clinical decision-support system
- a replacement for professional judgement
- a production NHS deployment
- an autonomous operational decision-maker

Human review remains part of the architecture where governance requires it.

---

# Economic Value Hypothesis

The project targets information friction in operational work.

The value proposition is:

> Reduce avoidable time spent searching, reconciling and checking operational guidance while retaining human oversight when evidence or governance requires it.

An illustrative scenario is:

```text
50 staff
× 15 minutes per day
× 220 working days
= 2,750 hours of annual information-search activity
```

At an illustrative loaded activity cost of approximately:

```text
£30/hour
```

that represents:

```text
£82,500
```

of annual staff activity.

A hypothetical 25% reduction would correspond to approximately:

```text
£20,625
```

of potentially released staff capacity.

These figures are illustrative only.

They are **not validated NHS savings claims**.

Any real economic claim would require measurement of:

- current search time
- adoption
- task completion time
- reviewer burden
- error reduction
- avoided duplication
- operational workflow changes

---

# Why This Project Is Different From a Basic RAG Demo

A basic RAG system often follows:

```text
Question
→ retrieve documents
→ send context to model
→ generate answer
```

This project instead follows:

```text
Question
→ scope control
→ governed retrieval
→ evidence sufficiency
→ structured evidence
→ provenance
→ lifecycle
→ precedence
→ governance
→ controlled generation
→ validation
→ citation assurance
→ faithfulness assurance
→ final governance
→ safe presentation
```

The distinction is important.

The project is designed around the question:

> **Should the system answer at all?**

not merely:

> **Can the model generate something plausible?**

---

# Engineering Principles

The project is built around several principles.

## Evidence before generation

Generation should not determine whether the evidence is trustworthy.

## Governance before convenience

A more fluent answer does not justify increasing authority.

## Human review is a valid output

`REVIEW_REQUIRED` is a designed system state, not a failure.

## Abstention is a safety capability

A system that knows when not to answer is safer than one optimised only for response rate.

## Presentation cannot increase authority

A user-facing layer may simplify language but must not weaken governance.

## Deterministic fallback matters

Optional model execution must not become a single point of failure.

## Assurance is independent of the model

> The model is optional. The assurance path is not.

---

# Current Portfolio Position

The project has evolved through several engineering stages:

```text
Document ingestion
        ↓
Metadata and lifecycle controls
        ↓
Semantic / keyword / hybrid retrieval
        ↓
Evidence sufficiency
        ↓
Bounded retrieval refinement
        ↓
Structured evidence
        ↓
Evidence packets
        ↓
Provenance and precedence
        ↓
Governed communication
        ↓
Controlled model execution
        ↓
Citation and faithfulness assurance
        ↓
Adversarial safety hardening
        ↓
Canonical end-to-end RAG application
        ↓
Runtime configuration
        ↓
Safe observability
        ↓
Reproducible CLI
        ↓
Three-outcome portfolio demo
        ↓
Manager-facing governed responses
        ↓
Clean-start reproducibility
```

The project has therefore moved beyond a retrieval experiment into a reproducible governed RAG application prototype.

---

# Current Limitations

The project is intentionally not presented as production-ready NHS software.

Current limitations include:

- synthetic portfolio data
- no live NHS system integration
- no production identity/access-management layer
- no production secret-management infrastructure
- no production clinical-safety case
- no real operational impact evaluation
- no validated savings study
- deterministic portfolio demonstrations
- controlled provider integration rather than unrestricted autonomous model execution
- local demonstration infrastructure rather than cloud production deployment

These limitations are explicit because strong assurance depends on distinguishing a validated prototype from a production system.

---

# Production Evolution

Future stages may include:

- Azure healthcare AI services
- production secret management
- managed model providers
- secure document stores
- controlled identity and access
- deployment pipelines
- containerisation
- cloud observability
- monitoring
- evaluation dashboards
- human-review workflow integration
- governance reporting
- measured operational impact
- NHS deployment architecture

These production capabilities should extend the existing governance model rather than bypass it.

---

# Interview Summary

A concise technical explanation of the project is:

> I built a governed healthcare document intelligence system for NHS-style operational guidance. Instead of allowing a language model to answer immediately, the system first checks scope, retrieves approved evidence, assesses sufficiency, verifies provenance and lifecycle state, evaluates precedence, and decides whether an answer is permitted. Optional model output is validated through citation, groundedness and safety controls. The final system can release a supported answer, require human review, or abstain. I also packaged the application so that its three governed outcomes can be reproduced from a clean Python environment with automated regression testing.

A concise management explanation is:

> Instead of staff spending time searching through several policies and deciding which one is current, the system brings together the relevant approved information, checks whether it is sufficient and consistent, and gives either a supported answer, a review warning or a refusal to answer. The objective is to reduce avoidable search and reconciliation time while keeping human oversight.

---

# Current Validation Snapshot

Clean-environment portfolio validation:

```text
Three-outcome governed demo: PASS
Focused Week 28 tests: 59 passed
Full repository regression: 1639 passed
Dependency audit: PASS
```

The clean environment used:

```text
Python 3.14.1
```

and was installed from:

```text
requirements.txt
```

---

# Repository Philosophy

The project follows one central idea:

> **Trustworthy healthcare AI requires control over when the system answers, what evidence supports the answer, and when humans must remain in the loop.**

The target progression is:

```text
Smart Retrieval
        ↓
Trusted Evidence
        ↓
Governed Communication
        ↓
Assured Generation
        ↓
Reproducible Governed RAG
```