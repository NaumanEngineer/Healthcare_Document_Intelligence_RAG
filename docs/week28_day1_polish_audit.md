# Week 28 Day 1 — End-to-End RAG Polish Audit

## Purpose

Week 28 begins from the completed Week 27 governed RAG application.

Day 1 audits the existing application from four perspectives:

- NHS operational manager
- recruiter
- technical interviewer
- future developer

The goal is to identify usability, documentation, reproducibility and
portfolio-presentation weaknesses without changing the protected governance
and assurance architecture.

---

## Protected Baseline

Starting commit:

`f070543 Complete Week 27 end-to-end governed RAG application`

Week 27 full regression:

`1580 passed`

Verified portfolio demo:

- application status: COMPLETED
- final outcome: ANSWER
- observability: COMPLETED
- observed events: 11
- authority increased: False

The Week 25–26 assurance subsystem and Week 27 application architecture remain
protected baselines.

---

## Current Runtime Health

No P0 runtime defect was identified during the Day 1 audit.

The controlled Week 27 portfolio demo continues to produce:

- COMPLETED
- ANSWER
- observability completed
- 11 observed events

The normal local application entry point also completes safely when no usable
local evidence corpus is available.

In that condition it returns:

- COMPLETED
- ABSTAIN
- observability completed
- 11 observed events

This is desirable fail-safe behaviour.

The problem is not the governance decision.

The polish problem is that the current console summary does not explain the
reason for the outcome or the next action to the user.

---

# Audit Findings

## P0 — Must Fix

No P0 correctness or safety defect was identified during Day 1.

Week 28 should not invent architectural work where none is required.

---

## P1 — High-Value Polish

### P1.1 — Root README is behind the actual architecture

The README explains the project well through retrieval, evidence, provenance
and governance.

However, its main architecture still reflects an earlier project stage.

It does not prominently represent the current end-to-end application:

Question
→ governed retrieval
→ evidence packet
→ provenance / lifecycle / precedence
→ pre-generation governance
→ answer contract
→ answer context
→ deterministic or controlled generation
→ response selection
→ citation / faithfulness assurance
→ final governance
→ observability
→ safe application result

This hides some of the strongest engineering work completed in Weeks 24–27.

### Required Week 28 action

Rewrite the portfolio-facing README so that the current system can be
understood quickly by recruiters, NHS managers and technical interviewers.

---

### P1.2 — README chronology dominates the product story

The README contains a detailed Week 23 section.

This is useful development history but should not dominate the main portfolio
story now that the application is considerably more mature.

### Required Week 28 action

Lead with:

1. operational problem
2. product value
3. current architecture
4. governed outcomes
5. demo
6. assurance
7. test evidence
8. limitations
9. economic-value hypothesis

Keep weekly implementation history secondary.

---

### P1.3 — Current CLI outcome is too terse for an operational user

The current console interface reports items such as:

- application status
- final outcome
- observability status
- event count

This is useful technically but insufficient for a manager.

For an ABSTAIN result, the manager should also understand:

- why the system did not answer
- whether the problem was missing evidence, conflict, lifecycle or scope
- what information would be required to continue
- whether human review is appropriate

For REVIEW_REQUIRED, the user should understand:

- why review is required
- what should be reviewed
- whether the system produced a bounded evidence summary

For ANSWER, the user should understand:

- that the response passed the governed release path
- the evidence basis
- whether human review is still required

### Required Week 28 action

Improve safe user-facing presentation without exposing raw prompts,
unrestricted evidence text, internal exceptions or sensitive material.

---

### P1.4 — Three governed outcomes are not yet presented as one portfolio story

The architecture supports:

- ANSWER
- REVIEW_REQUIRED
- ABSTAIN

The current portfolio demo prominently demonstrates ANSWER.

Week 28 should demonstrate all three outcomes through real governed application
paths where possible.

### Required Week 28 action

Create a deterministic three-outcome demonstration:

Question
→ ANSWER

Question
→ REVIEW_REQUIRED

Question
→ ABSTAIN

The demonstrations must use the real application controls and must not force or
override governance simply to obtain a desired result.

---

### P1.5 — Economic value is not prominent enough

The project currently demonstrates strong technical governance.

Its operational value needs to be equally obvious.

Primary value hypothesis:

Reduce avoidable staff time spent:

- searching multiple documents
- checking document currency
- reconciling overlapping guidance
- confirming provenance
- identifying conflicts
- deciding whether escalation or review is required

Illustrative scenario:

- 50 staff
- 15 minutes per working day
- 220 working days
- 2,750 staff hours annually
- illustrative £30 per staff hour
- approximately £82,500 annual activity
- 25% reduction represents approximately £20,625 of potentially released staff
  capacity

These figures are illustrative assumptions.

They are not validated NHS savings.

The appropriate management framing is released operational capacity, not a
guaranteed cash saving.

---

### P1.6 — Week 27 Markdown files contain stored formatting artefacts

UTF-8 source inspection confirmed that some Week 27 Markdown files contain
literal escaped Markdown and HTML spacing artefacts.

Confirmed examples include:

- headings stored as `\#` and `\##`
- separators stored as `\---`
- layout spacing stored as `&#x20;`

This is not only a PowerShell display issue.

Affected files confirmed during Day 1 include:

- `docs/week27_day5_application_entry_point_contract.md`
- `docs/week27_day6_portfolio_evidence.md`

These artefacts reduce readability on GitHub and weaken portfolio presentation.

### Required Week 28 action

Normalize the affected Week 27 Markdown files without changing their technical
meaning.

The cleanup should:

- remove unnecessary Markdown escapes;
- replace HTML spacing entities with ordinary spaces;
- preserve code fences;
- preserve technical content;
- preserve headings and section structure;
- avoid altering governance claims or benchmark results.

---

## P2 — Useful Enhancements

### P2.1 — Stable portfolio demo naming

Current demo modules use Week 27-specific names.

This is appropriate development history but eventually a stable command such
as a portfolio demo entry point may be easier for recruiters and interviewers
to understand.

This is not required for correctness.

---

### P2.2 — CLI discoverability

The current CLI help is technically understandable.

Future polish could include:

- example commands
- clearer configuration explanation
- demo command documentation
- explanation of governed outcomes

This should remain a thin presentation layer.

---

## Out of Scope for Week 28

Do not add:

- new citation detectors without demonstrated need
- new hallucination detectors without demonstrated need
- duplicate governance systems
- production NHS infrastructure
- live patient data
- autonomous clinical decision-making
- unsupported NHS cost-saving claims
- Azure production architecture ahead of the roadmap

---

# Perspective Audit

## NHS Operational Manager

Current strengths:

- the operational problem is relevant
- safe abstention exists
- human review exists
- lifecycle and provenance controls exist

Current weakness:

The console does not yet communicate outcome rationale and next action clearly
enough for a manager.

---

## Recruiter

Current strengths:

- substantial engineering depth
- healthcare-specific domain
- strong governance architecture
- extensive regression testing

Current weakness:

The README materially understates the current maturity of the project.

A recruiter could reasonably believe the project is still around the Week 23
communication layer.

---

## Technical Interviewer

Current strengths:

- canonical runtime
- separated dependencies
- fail-closed behaviour
- monotonic authority
- protected assurance path
- explicit observability boundary
- reproducible regression

Current Week 28 opportunity:

Demonstrate the three governance outcomes cleanly and package the architectural
story more efficiently.

---

## Future Developer

Current strengths:

- one canonical application entry point
- explicit runtime configuration
- application dependency boundary
- repeatable demo
- regression coverage

Current Week 28 opportunity:

Improve setup instructions, demo documentation and expected-result guidance.

---

# Day 1 Priority Backlog

## P0

None currently identified.

## P1

1. Modernize the root README.
2. Demonstrate ANSWER, REVIEW_REQUIRED and ABSTAIN.
3. Improve manager-facing outcome presentation.
4. Make economic value visible.
5. Verify and resolve documentation encoding/presentation artefacts.
6. Improve clean-start reproducibility documentation.

## P2

1. Introduce stable portfolio demo naming if useful.
2. Improve CLI examples and discoverability.
3. Condense historical weekly detail away from the main portfolio narrative.

---

# Week 28 Direction

Week 28 should polish the existing architecture rather than extend it
unnecessarily.

The target progression is:

Technically complete governed RAG
→ understandable governed RAG
→ demonstrable governed RAG
→ reproducible governed RAG
→ portfolio-ready healthcare AI application

---

# Day 1 Decision

The engineering core is sufficiently mature.

The primary Week 28 problem is now communication:

- communicate decisions to operational users
- communicate architecture to technical reviewers
- communicate value to managers
- communicate maturity to recruiters

No new safety subsystem is justified by the Day 1 audit.