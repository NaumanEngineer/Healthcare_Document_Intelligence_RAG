# Week 28 Day 5 — Interview and Manager Story



## Healthcare Document Intelligence RAG



This document provides concise explanations of the project for different

audiences.



The same system should be explainable clearly to:



- an NHS operational manager

- a recruiter

- a technical interviewer

- an AI / data engineering hiring manager



The objective is to communicate value without overstating what the prototype

has proven.



---



# 30-Second Recruiter Summary



Healthcare Document Intelligence RAG is a governed AI evidence assistant for

NHS-style operational guidance.



Instead of sending retrieved documents directly to a language model, the

system checks scope, evidence sufficiency, provenance, lifecycle status and

precedence before generation is allowed.



It can produce three explicit outcomes:



- ANSWER

- REVIEW_REQUIRED

- ABSTAIN



The project also includes citation and faithfulness assurance, adversarial

testing, deterministic fallback, structured observability, reproducible

runtime configuration and a clean-start test path.



The current repository regression baseline is:



```text

1639 passed
