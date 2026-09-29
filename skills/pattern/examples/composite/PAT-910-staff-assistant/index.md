---
title: "PAT-910 Staff Assistant"
description: "A staff assistant that answers from permitted content and carries out confirmed actions"
document_type: pattern
pattern_scope: capability-area
status: Draft
version: "0.1"
last_modified: 2026-09-30
provenance:
  origin: ai-generated
  review_state: ai-raw
---

# PAT-910 Staff Assistant

An illustrative composite pattern: its scenario steps run other patterns' flows. Answering a question is a solved problem here, so the step that does it runs the worked example PAT-900 Knowledge Retrieval, a participating pattern, rather than repeating it. Carrying out an action is not solved yet, so its step runs an open participating pattern. The identifiers and names are invented; the tables are trimmed to what composing reads, and the diagram a real pattern carries is left out.

## Context

A staff member asks the assistant a question, gets an answer grounded in content they may see, and may ask it to act on the answer once they confirm.

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-900 Knowledge Retrieval | Answers the question from permitted content, with citations; run by S1 step 2, its Model Gateway bound to 03 Assistant gateway here |
| TBD confirmed action | Carries out an action the staff member has confirmed; S1 step 4, an open participating pattern, not yet written |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Assistant | The chat surface staff use | loose |
| 03 Assistant gateway | Routes the question and composes the grounded prompt | loose |
| ABB-901 Retrieval Service | Returns cited passages or an explicit no-answer | PAT-900 |
| 02 Action runner | Carries out an action once it is confirmed | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-11 | 03 Assistant gateway | 01 Assistant | the question in, the cited answer out |
| IF-12 | ABB-901 Retrieval Service | 03 Assistant gateway | cited passages for the prompt |
| IF-13 | 02 Action runner | 03 Assistant gateway | a proposed action, and its outcome |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Ask, then act

Step 2 is the whole of PAT-900 S1. That scenario declares its Start, ABB-908 Model Gateway, and its Finish, ABB-901 Retrieval Service. The binding `(ABB-908=03)` says this pattern's local 03 Assistant gateway plays PAT-900's Model Gateway, so the flow enters at 03 and leaves at ABB-901, the step's Actor and Target. Step 4 runs an open participating pattern.

Start: 01 Assistant

Finish: 01 Assistant

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Assistant | 03 Assistant gateway | send the question with the staff member's token | IF-11 | |
| 2 | 03 Assistant gateway | ABB-901 Retrieval Service | ground the question in content the caller may see | | PAT-900 S1 (ABB-908=03) Grounded answer |
| 3 | ABB-901 Retrieval Service | 03 Assistant gateway | return cited passages for the answer | IF-12 | |
| 4 | 03 Assistant gateway | 02 Action runner | carry out the action the staff member confirmed | | TBD confirmed action |
| 5 | 02 Action runner | 01 Assistant | report the outcome with the answer | IF-13 | |
