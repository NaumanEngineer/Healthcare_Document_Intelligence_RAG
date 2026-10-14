\# Week 24 Day 1 — Model Input / Output Contract



\## Purpose



This contract defines exactly what information the model may receive and exactly what structure it must return.



The goal is to prevent free-form generation from bypassing the governed communication architecture.



\---



\# Input Contract



The model may receive only a controlled generation payload.



Required fields:



\- packet\_id

\- question

\- governance\_decision

\- response\_type

\- generation\_permitted

\- requires\_human\_review

\- allowed\_sections

\- safety\_constraints

\- evidence\_context

\- citation\_index

\- uncertainty\_context



\---



\# Governance Rules



\## AUTO\_ANSWER



Expected:



\- governance\_decision = AUTO\_ANSWER

\- response\_type = ANSWER

\- generation\_permitted = true

\- requires\_human\_review = false



The model may produce substantive grounded content.



\---



\## REVIEW\_REQUIRED



Expected:



\- governance\_decision = REVIEW\_REQUIRED

\- response\_type = REVIEW

\- generation\_permitted = false

\- requires\_human\_review = true



The model may produce only a review-oriented summary.



It must not produce an authoritative final answer.



\---



\## ABSTAIN



Expected:



\- governance\_decision = ABSTAIN

\- response\_type = ABSTENTION

\- generation\_permitted = false

\- requires\_human\_review = false



The model must not produce substantive evidence-based content.



\---



\# Evidence Input



Each evidence item may contain:



\- evidence\_id

\- document\_id

\- chunk\_id

\- title

\- document\_type

\- source\_file

\- version

\- status

\- page

\- evidence\_text

\- evidence\_role



No other evidence should be available to the model.



\---



\# Citation Input



The model receives a citation index containing valid citation IDs.



Example:



\- E1

\- E2

\- E3



The model must not invent additional citation IDs.



\---



\# Output Contract



The model output must be structured.



Required top-level fields:



\- packet\_id

\- governance\_decision

\- response\_type

\- requires\_human\_review

\- model\_generation\_status

\- sections

\- citations\_used

\- model\_safety\_notes



\---



\# AUTO\_ANSWER Output



Expected sections may include:



\- management\_summary

\- evidence\_based\_explanation

\- operational\_implication

\- caveats



Each substantive section should use citation IDs from the citation index.



\---



\# REVIEW\_REQUIRED Output



Expected sections may include:



\- evidence\_summary

\- why\_human\_review\_is\_required

\- review\_focus

\- evidence\_gaps\_or\_uncertainty



The output must remain clearly non-authoritative.



\---



\# ABSTAIN Output



Expected sections may include:



\- unable\_to\_answer\_safely

\- reason

\- missing\_information

\- what\_is\_needed\_to\_continue



No substantive answer section should be present.



\---



\# Identity Preservation



The model must return exactly the same:



\- packet\_id

\- governance\_decision

\- response\_type

\- requires\_human\_review state



that it received.



Any mismatch must fail validation.



\---



\# Citation Validation



Every citation in citations\_used must exist in the supplied citation index.



Unknown citations must fail closed.



Blank citations must fail closed.



Duplicate citations may be normalised or rejected according to validator policy.



\---



\# Section Validation



The model may only return sections that are permitted for the current response type.



Examples:



AUTO\_ANSWER must not return:



\- unable\_to\_answer\_safely



REVIEW\_REQUIRED must not return:



\- final\_decision

\- approved\_action



ABSTAIN must not return:



\- evidence\_based\_explanation

\- operational\_recommendation



Unexpected substantive sections must fail validation.



\---



\# Safety Notes



The model may return model\_safety\_notes for transparency.



These notes may record:



\- evidence limitations

\- unresolved ambiguity

\- citation uncertainty

\- formatting issue

\- generation limitation



Safety notes cannot override governance.



\---



\# Parsing Rule



The first Week 24 implementation should use structured deterministic parsing.



If model output cannot be parsed into the required schema:



\- reject the output

\- do not guess missing fields

\- do not silently repair authority fields

\- fall back to the deterministic baseline



\---



\# Fallback Rule



The deterministic Week 23 response remains the fallback.



Fallback must be used when:



\- model output is malformed

\- identity fields mismatch

\- unknown citations appear

\- prohibited sections appear

\- unsupported material claims appear

\- abstention leaks substantive content

\- review output becomes authoritative



\---



\# Day 1 Contract Principle



> The model does not return whatever it wants. It returns a governed object that must pass validation before use.
