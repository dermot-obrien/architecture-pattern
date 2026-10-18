---
sidebar_label: Collaboration Template
status: Draft
# The pattern type, as your repository binds it. A collaboration: participants working
# together, drawn with the same diagram and scenarios as any pattern, without the
# building-block rigour of an architecture pattern or a reference architecture.
kind: pattern
pattern_type: collaboration
# problem, domain, capability-area, platform, hosting-profile or epic, as for any pattern.
pattern_scope: problem
version: "0.1"
last_modified: 2026-10-18
author: "<your name>"
model:
  diagram: components.drawio
provenance:
  origin: ai-generated
  review_state: ai-raw
---

# CL-NNN Collaboration Name

<!--
HOW TO USE THIS TEMPLATE
- A collaboration is a pattern of participants working together: people, teams, boards,
  systems and outside parties, and what passes between them. Use it where what matters is
  who does what with whom, in what order, rather than which building blocks a design is
  made of. When the participants become building blocks with interfaces worth specifying,
  it has become an architecture pattern or a reference architecture; when one participant
  is after an observable result, it is a use case.
- It has the four parts every pattern has, and little else: the diagram, the participants
  (the boxes), the interactions (the lines) and one or more scenarios (the sequences).
  Every other section is optional.
- The tables are the model, exactly as in a pattern: Participants and Interactions
  generate the diagram, each scenario's steps table its numbered overlay and the animated
  walkthrough. They read with the same bindings as a use case's tables (the use-case
  skill's SKILL.md has the snippet). Publish with the pattern skill's publish.py.
- Participants take local ids (01 Service desk) unless a catalogue entry exists. Kind is
  free: person, team, board, system, external, or the repository's own words. It colours
  the box.
- Keep it to one or two pages. Delete each guidance comment as you complete its section.
-->

<!-- deck:cover subtitle="Who works together, and to what end" -->

## Purpose

<!--
MANDATORY. What the participants achieve together, in two or three sentences, and why it
takes more than one of them. Name who relies on the outcome.
-->

<!-- deck:slide label="On one page" title="The collaboration on one page" -->

## Diagram

<!-- The view publish.py renders from the two tables below: ![CL-NNN participants and interactions](./components.svg) -->

## Participants

<!--
MANDATORY. Every participant on the diagram, one row each, written as its id and name.
-->

| Participant | Role in this collaboration | Kind |
|---|---|---|
| 01 Participant name | What they do here | team |
| 02 Another participant | What they do here | system |

## Interactions

<!--
MANDATORY. Every line on the diagram, provider to consumer: what one participant gives
another. Purpose is the arrow's label, so keep it to a few words.
-->

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 01 Participant name | 02 Another participant | what passes between them |

## Scenarios

<!--
MANDATORY. At least one: the sequence of what happens, five to ten steps, each over an
interaction. Add another only for a materially different sequence. A scenario is a
straight line; a branch or a failure belongs in prose under it.
-->

Step through them in the [animated scenario walkthrough](./scenarios.html).

<!-- deck:html src="./scenarios.html" title="Scenario walkthrough" header="true" -->

### S1 Scenario name

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Participant name | 02 Another participant | What happens | IF-01 |

## Agreements

<!-- OPTIONAL. What the participants have agreed with one another: a handover condition, a response time, who decides. Delete if none. -->

| Agreement | Between | What is agreed |
|---|---|---|
| | | |

## Open Questions

<!-- RECOMMENDED. What is not settled, who answers it and by when. -->

| Question | Who answers | By when |
|---|---|---|
| | | |

## Catalogue Mapping

<!-- OPTIONAL. What each local participant realises in a catalogue, if anything: realises, partial or gap. -->

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | | gap |
| 02 | | gap |
