\# Week 24 Day 4 — Deterministic Fallback Policy



\## Purpose



This policy defines what the system should do when model-assisted generation cannot be safely accepted.



The fallback path must preserve:



\- governance

\- response type

\- human-review requirements

\- abstention

\- citations

\- evidence boundaries

\- deterministic safety behaviour



The fallback should use the existing Week 23 grounded communication layer.



\---



\# Core Principle



A failed model call must not become a failed user experience.



The system should continue with the deterministic governed response whenever model-assisted generation is:



\- unavailable

\- malformed

\- rejected

\- unsafe

\- inconsistent with governance



\---



\# Fallback Triggers



Fallback should be used when:



\- provider execution fails

\- provider returns free-form output

\- output cannot be parsed

\- packet identity changes

\- governance changes

\- response type changes

\- human-review state changes

\- unknown citations appear

\- duplicate citations appear

\- prohibited sections appear

\- generation status is invalid

\- model output violates abstention

\- model output weakens review requirements



\---



\# Fallback Source



The fallback source is the existing deterministic Week 23 grounded response.



The fallback must not invent new content.



It should reuse the already-governed communication output produced from:



Answer Contract

→ Answer Context

→ Grounded Response

→ Claim-to-Citation Linking

→ Review / Abstention UX



\---



\# Authority Preservation



Fallback must preserve the original governance state.



Examples:



AUTO\_ANSWER remains ANSWER.



REVIEW\_REQUIRED remains REVIEW.



ABSTAIN remains ABSTENTION.



Fallback must never increase authority.



\---



\# AUTO\_ANSWER Fallback



If model-assisted generation fails during AUTO\_ANSWER:



use the deterministic Week 23 grounded response.



The final result may still contain:



\- management summary

\- evidence-based explanation

\- operational implication

\- caveats

\- sources



provided these are already allowed by the deterministic response.



\---



\# REVIEW\_REQUIRED Fallback



If model-assisted generation fails during REVIEW\_REQUIRED:



use the deterministic review summary.



The final result must still:



\- require human review

\- remain non-authoritative

\- preserve review focus

\- preserve uncertainty

\- preserve sources



\---



\# ABSTAIN Fallback



If model-assisted generation fails during ABSTAIN:



use the deterministic abstention response.



The final result must still:



\- contain no substantive answer

\- contain no hidden evidence

\- contain no citations

\- explain missing information

\- provide a safe next step



\---



\# Fallback Metadata



The system should record:



\- model\_execution\_status

\- fallback\_used

\- fallback\_reason

\- provider\_name

\- model\_name

\- governance\_decision

\- packet\_id

\- final\_response\_source



Possible final\_response\_source values:



\- MODEL

\- DETERMINISTIC\_FALLBACK



\---



\# No Silent Authority Repair



The system must not silently modify unsafe model output into a more acceptable answer.



Examples of prohibited repair:



\- changing REVIEW to ANSWER

\- deleting an unknown citation and accepting the rest

\- changing governance fields

\- removing human-review requirements



Unsafe model output should be rejected as a whole.



Then deterministic fallback should be used.



\---



\# Auditability



Fallback use must be visible in system metadata.



This helps measure:



\- provider reliability

\- validation rejection rate

\- fallback rate

\- model quality

\- operational cost



\---



\# Economic Importance



Fallback protects economic value because it prevents model instability from interrupting workflows.



Without fallback:



\- staff may need to restart tasks

\- model failures create delays

\- trust falls

\- manual work returns



With fallback:



\- the workflow continues

\- safety is preserved

\- provider failures become operationally manageable



\---



\# Day 4 Principle



> The model may fail. The governed workflow must not.
