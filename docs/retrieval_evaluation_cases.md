# Retrieval Evaluation Cases

## Purpose

Define test queries with expected evidence so retrieval quality
can be measured independently from answer generation.

## Q001 — Direct Escalation

Query:

`What actions are required during operational escalation?`

Expected:

- Operational Escalation Policy
- Active version
- relevant escalation section/page

## Q002 — Workforce

Query:

`What actions are required during workforce pressure?`

Expected:

- Workforce Escalation Procedure
- Active version

## Q003 — Capacity

Query:

`Which guidance covers bed capacity escalation?`

Expected:

- Bed Capacity Management Procedure
- Active version

## Q004 — Governance

Query:

`What responsibilities belong to operational leadership?`

Expected:

- Operational Governance Standard or relevant escalation policy
- Active version

## Q005 — Superseded Content

Test condition:

A Superseded document has a stronger semantic similarity score
than the current Active version.

Expected:

The Superseded document must not be returned by default.

## Q006 — Insufficient Evidence

Query:

`What medication should be prescribed during operational escalation?`

Expected:

No supported policy evidence.

The retrieval layer should not force an unrelated chunk into the
evidence set.
