\# Week 26 Day 2 — Adversarial Benchmark Data Contract



\## Objective



Define the machine-readable contract for the Week 26 adversarial benchmark before creating benchmark JSON or production evaluators.



The existing Week 25 benchmark remains unchanged and continues to act as the regression anchor.



The Week 26 benchmark is an extension layer focused on more difficult adversarial behaviour.



\## Core Principle



> Define the safety contract before changing the implementation.



\---



\## Benchmark Identity



Suggested benchmark file:



`data/benchmark/week26\_adversarial\_faithfulness\_benchmark.json`



Suggested benchmark name:



`Week 26 Adversarial Faithfulness Benchmark`



Suggested benchmark version:



`1.0`



Initial case count:



`12`



Case IDs:



\- W26-C001

\- W26-C002

\- W26-C003

\- W26-C004

\- W26-C005

\- W26-C006

\- W26-C007

\- W26-C008

\- W26-C009

\- W26-C010

\- W26-C011

\- W26-C012



\---



\## Top-Level Benchmark Fields



The benchmark should contain:



\- benchmark\_name

\- benchmark\_version

\- benchmark\_purpose

\- synthetic\_data\_only

\- regression\_dependency

\- created\_for\_week

\- cases



\### Example



```json

{

&#x20; "benchmark\_name": "Week 26 Adversarial Faithfulness Benchmark",

&#x20; "benchmark\_version": "1.0",

&#x20; "benchmark\_purpose": "Adversarial citation, grounding, temporal, governance, abstention and prompt-injection assurance.",

&#x20; "synthetic\_data\_only": true,

&#x20; "regression\_dependency": "Week 25 18-case benchmark remains unchanged.",

&#x20; "created\_for\_week": 26,

&#x20; "cases": \[]

}

