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

An illustrative wider-scope pattern that chains another. Answering a question is a solved problem here, so the step that does it calls the worked example PAT-900 Knowledge Retrieval rather than repeating it. Carrying out an action is not solved yet, so its step is an open child flow. The identifiers and names are invented; the tables are trimmed to what chaining reads, and the diagram a real pattern carries is left out.

## Context

A staff member asks the assistant a question, gets an answer grounded in content they may see, and may ask it to act on the answer once they confirm.

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-900 Knowledge Retrieval | Answers the question from permitted content, with citations; called by S1 step 2 |
| TBD confirmed action | Carries out an action the staff member has confirmed; S1 step 4, not yet written |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Assistant | The chat surface staff use | loose |
| ABB-908 Model Gateway | Routes the question and composes the grounded prompt | PAT-900 |
| ABB-901 Retrieval Service | Returns cited passages or an explicit no-answer | PAT-900 |
| 02 Action runner | Carries out an action once it is confirmed | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-11 | ABB-908 Model Gateway | 01 Assistant | the question in, the cited answer out |
| IF-12 | ABB-901 Retrieval Service | ABB-908 Model Gateway | cited passages for the prompt |
| IF-13 | 02 Action runner | ABB-908 Model Gateway | a proposed action, and its outcome |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Ask, then act

Step 2 is the whole of PAT-900 S1: it enters at the Model Gateway, as that scenario's first step does, and leaves at the Retrieval Service, where that scenario's last step starts. Step 4 is an open child flow.

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Assistant | ABB-908 Model Gateway | send the question with the staff member's token | IF-11 | |
| 2 | ABB-908 Model Gateway | ABB-901 Retrieval Service | ground the question in content the caller may see | | PAT-900 S1 Grounded answer |
| 3 | ABB-901 Retrieval Service | ABB-908 Model Gateway | return cited passages for the answer | IF-12 | |
| 4 | ABB-908 Model Gateway | 02 Action runner | carry out the action the staff member confirmed | | TBD confirmed action |
| 5 | 02 Action runner | 01 Assistant | report the outcome with the answer | IF-13 | |
