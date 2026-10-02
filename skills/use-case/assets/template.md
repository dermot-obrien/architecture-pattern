---
document_type: use-case
status: Draft
version: "0.1"
last_modified: 2026-10-01
author: "<your name>"
realised_by: []            # optional: the patterns that design it, PAT-NNN
former_ids: []             # on endorsement: the local id it had, such as EP-12-UC1
model:
  diagram: components.drawio
provenance:
  origin: ai-generated
  review_state: ai-raw
---

# <ID> Use case name

<!--
HOW TO USE THIS TEMPLATE
- A use case says what a solution does for someone and what it needs, before anyone designs
  how it is built. A pattern says how it is built. A use case names the patterns that
  realise it in realised_by; a pattern can name the use cases it serves.
- A use case starts local to the container that needs it, such as an epic: copy this file
  to <container>/<localDir>/<ID>-<slug>/index.md, where <ID> is localIdFormat (by default
  {container}-UC{n}, such as EP-12-UC1). Only an endorsed use case takes a registered id
  from idSeries (UC by default) and lives under outputDir. Replace <ID> throughout.
- A use case has scenarios. S1 is the main success scenario; S2 onwards are alternative
  or extension scenarios, each one path through the use case (UML, Unified Process).
- The page is also the model and the deck, as a pattern is. The Participants, Interactions
  and Scenarios tables generate the diagram and the animated walkthrough; the deck: tags
  build the deck. The repository's binding file must map the Participants and Interactions
  sections (the use-case skill's SKILL.md has the snippet). Publish with the pattern skill's
  publish.py, exactly as a pattern.
- Fill it in this order: the one sentence, Participants, Interactions, the main success scenario, then
  what it returns, scope, data, dependencies and measures. Risks and decisions are the
  residue of the rest.
- Keep it to two or three pages. Tables carry the volume.
- Delete each guidance comment as you complete its section.
-->

<!-- deck:cover subtitle="The solution in one sentence" -->

| Field | Value |
|---|---|
| Use case | <ID> |
| Consumer | Who uses it |
| Owner | Who answers for the outcome |
| Outcome | What it is for, and how it will be recognised |
| Rests on | The hypothesis or assumption it depends on |
| Realised by | The pattern that designs it, or "none yet" |
| Date | |

<!-- deck:slide label="In one sentence" -->

## The solution in one sentence

[Who] uses [what] to [do what], so that [outcome].

<!-- The problem today, in two or three sentences: what it costs, who it depends on, why it is hard. -->

### What is different afterwards

<!-- What someone does differently once it exists. If nothing, say so. -->

<!-- deck:slide label="On one page" title="The solution on one page" -->

## Diagram

<!-- The view model render writes from the two tables below: ![<ID> participants and interactions](./components.svg) -->

## Participants

<!--
Every actor, the solution's own parts, and the products or systems it touches: five to
eight in all. A local id leads each name (01 Analyst) until a catalogue entry exists. Kind
is actor, solution, product or external, and colours the box.
-->

| Participant | Role in this use case | Kind |
|---|---|---|
| 01 Actor name | What they do here | actor |
| 02 Solution part | What it does here | solution |
| 03 Product or system | What it provides | product |

## Interactions

<!--
Every real call or handover between participants, provider to consumer. Purpose is the
arrow's label, so keep it to a few words. The data and systems tables refer to these ids.
-->

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Solution part | 01 Actor name | request in, answer out |
| IF-02 | 03 Product or system | 02 Solution part | what flows |

## Scenarios

<!--
S1 is the main success scenario: five to eight steps, each a real interaction. Add S2
only for a materially different path, such as an extension that changes who acts, or
setting the solution up. Branches and failures belong
in a sequence diagram; say so in one line under the flow. Link the walkthrough that
model animate writes: Step through the flows in the [animated walkthrough](./scenarios.html).
-->

<!-- deck:html src="./scenarios.html" title="The flow" header="true" -->

### S1 Main success scenario

| Step | Actor | Target | Action | Interface |
|---|---|---|---|---|
| 1 | 01 Actor name | 02 Solution part | asks | IF-01 |
| 2 | 02 Solution part | 03 Product or system | fetches what it needs | IF-02 |
| 3 | 02 Solution part | 01 Actor name | answers | IF-01 |

<!-- deck:slide label="What it returns" -->

## What it returns

| Output | Content |
|---|---|
| | |

## Scope

| First version | Later | Explicitly out of scope |
|---|---|---|
| | | |

## Data it needs

| Interface | Source | What | Sensitivity | Acts under whose permissions |
|---|---|---|---|---|
| | | | | |

## Systems it reads or acts on

| Interface | System | Reads or writes | Sync or async | Governed path today? |
|---|---|---|---|---|
| | | | | |

<!-- deck:slide label="Dependencies" -->

## Dependencies

<!--
What the solution needs from others: a product, a platform service, another team. The
route says what happens: use it as it is, ask for a change to it, or build something new.
A repository with a product register and maturity levels replaces this table with its own
in its bound template.
-->

| What it needs | From | Route | Ready? |
|---|---|---|---|
| | | Use as is, change, or build new | Ready, dependency or blocker |

<!-- deck:slide label="Measures" -->

## Measures

| Measure | Target for the first version |
|---|---|
| | |

<!-- deck:slide label="Risks and decisions" -->

## Risks and assumptions

| Claim that could be false | So what | How it will be tested |
|---|---|---|
| | | |

### Open decisions

| Decision, between named options | Who decides | By when |
|---|---|---|
| | | |

<!-- deck:slide label="Next step" -->

## Next step

<!--
One of three, with the reason, what would change it, and the effort to the first version:
proceed to design; settle the open decisions first; or go back to the idea.
-->

## Catalogue Mapping

<!-- What each local participant realises in the building block catalogue: realises, partial or gap. -->

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | | gap |
