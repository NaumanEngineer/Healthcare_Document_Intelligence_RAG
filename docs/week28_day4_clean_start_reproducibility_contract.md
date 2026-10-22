\# Week 28 Day 4 — Clean-Start Reproducibility Contract



\## Purpose



Week 28 Day 4 makes the Healthcare Document Intelligence RAG project

reproducible for another developer, technical interviewer, or reviewer.



The objective is:



> Clone → install → configure → run → verify



A user should not need knowledge of the project's development history to run

the current portfolio demonstration.



This work does not change:



\- retrieval logic

\- evidence construction

\- governance

\- generation

\- citation assurance

\- faithfulness assurance

\- final authority

\- manager-facing authority



Day 4 is operational packaging and reproducibility work.



\---



\# 1. Reproducibility Goal



A technically competent reviewer should be able to:



1\. clone the repository

2\. create an isolated Python environment

3\. install required dependencies

4\. confirm runtime configuration

5\. run the deterministic portfolio demo

6\. observe ANSWER

7\. observe REVIEW\_REQUIRED

8\. observe ABSTAIN

9\. run the focused verification tests

10\. understand common setup failures



without modifying application source code.



\---



\# 2. Supported Portfolio Path



The primary clean-start demonstration is:



```text

python -m src.application.week28\_demo\_runner

