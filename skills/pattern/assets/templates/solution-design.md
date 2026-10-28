---
# The portfolio signature: the continuum front matter standard says what this document is.
kind: pattern
sidebar_label: Solution Design Template
status: Draft
# The pattern type, as your repository binds it. A solution design: one solution for one
# consumer, built from products and services, instantiating a reference architecture or an
# architecture pattern.
pattern_type: solution-design
# The reference architecture or architecture pattern this solution instantiates. Every
# building block there is accounted for in Pattern Realisation below.
implements: [RA-NNN]
version: "0.1.0"
last_modified: 2026-10-28
author: "<your name>"
owner: "<the team accountable for the solution>"
# Who uses or can reach the solution: staff, customers-or-partners, public or
# external-agents. The widest that applies.
exposure: staff
# The capabilities this solution realises. Add flows to scope it to some of a capability's
# flows; omit flows to cover all of them.
realises: [CAP-NNN]
flows: []
references:
  - { type: cost-model, path: "<path to the cost model>" }
  - { type: evidence, path: "<path to the evaluation>" }
provenance:
  origin: ai-generated
  review_state: ai-raw
---

# SD-NNN Solution Name

<!--
HOW TO USE THIS TEMPLATE
- This is the solution design template: one solution, for one consumer, that a team will
  build and run. Its boxes are products, services and stores, each realising a building
  block of the reference architecture or architecture pattern named in `implements`.
- It carries everything a reference architecture does, and what a solution adds: who uses
  it, where it sits, its data and trust zones, how it realises its pattern, its models and
  agents and their evals, its operations, and the evidence for it.
- Every section is a table on purpose. Each table's columns are the fields an assessment
  reads, so a design specification can be produced from this document row by row, with no
  interpretation. The architecture skill's specify flow recognises this template and
  translates it table by table. Where a column offers a choice of words, use one of them:
  they are the specification's own vocabulary.
- A cell that holds several items (concerns, alternatives, options) separates them with
  semicolons. A cell that has nothing to say, such as a decision with no departure, says
  None; a blank cell is read as a question still to answer. A blank cell is an unanswered question, not an omission: leave it blank
  rather than guess, and it will be asked.
- Two things do not belong here. Whether a building block is target state is attested by
  the responsible architect when the assessment is triaged, not claimed by the design. And
  assessment outcomes belong to the assessment, not to the design.
- Guidance lives in HTML comments, which Markdown renderers do not display. Delete each one
  as you complete its section.
- Identifiers below are written as SBB-NNN for solution building blocks, ABB-NNN for
  architecture building blocks, IF-NN for interfaces, TZ-NN for trust zones, DS-NN for data
  sets, EVAL-NN for evals and RA-NNN or AP-NNN for patterns. They are local to this
  document. Your repository's own series come from its
  binding file. A box with no catalogue entry yet takes a local number such as 07 and a
  row in Catalogue Mapping; never invent a catalogue identifier.
- Write each endpoint (Provider, Consumer, Actor, Target, and Building Block in the facet
  tables) as the identifier followed by the name. On an interface the Consumer calls the
  Provider: a request goes from the Consumer to the Provider. A data set's Owner is the
  building block that holds it. The model reads only the leading
  identifier; scripts/name-endpoints.py fills in names from Building Blocks.
- Never hyperlink identifiers in body text. Publishing rewrites them into links.
- A solution design is longer than a pattern, because it answers more questions. Keep the
  prose to what is architecturally significant; the tables carry the rest.
-->

<!-- deck:cover subtitle="One-line subtitle for the cover slide" -->

## Context

<!--
MANDATORY. The problem this solution solves, for whom, and what done looks like. One or
two paragraphs. Name the consumer: the team, product or business unit it is built for.
-->

### Goals and Non-Goals

<!--
MANDATORY. What the solution must achieve, each with how it will be measured, and what it
is explicitly not for. Three to five of each.
-->

| Kind | Statement | Measure |
|---|---|---|
| Goal | What the solution achieves | How it is measured |
| Non-goal | What it is explicitly not for | |

### Who Uses It

<!--
MANDATORY. Every kind of user or calling system, how each reaches the solution, and from
where. The widest reach sets `exposure` in the front matter.
-->

| User or system | How it reaches the solution | From where |
|---|---|---|
| Staff | Chat client | Corporate devices on the internal network |

### Where It Sits

<!--
MANDATORY. The catalogue identifiers that place this solution: the capabilities it
realises, the platform it belongs to, its bounded contexts, the outcomes and use cases it
serves and the products it is part of. Ask for an identifier you do not have; never coin
one.
-->

| Kind | Identifier and name |
|---|---|
| Capability | CAP-NNN Capability name |
| Platform | PL-NNN Platform name |
| Bounded context | BC-NNN Context name |
| Outcome | OC-NNN Outcome name |
| Use case | UC-NNN Use case name |

### Stakeholders

| Stakeholder | Concerns |
|---|---|
| Role or group | First concern; second concern |

### Constraints, Assumptions and Obligations

<!--
MANDATORY. Each constraint and assumption with where it comes from, and each obligation
(a law, regulation, policy or contract) with how that instrument classes this solution,
for example a risk category or a data classification.
-->

| Kind | Statement | Source | Classification under it |
|---|---|---|---|
| Constraint | What limits the design | Policy, contract or decision | |
| Assumption | What the design takes as true | Who said so | |
| Obligation | What must be complied with | The instrument | How it classes this solution |

<!-- deck:slide label="Component View" -->

## Diagram

<!--
MANDATORY. One draw.io source beside this file, holding the component view on the base
layer and one layer per scenario, generated from the tables with model emit and kept in
step with model sync. The pattern skill's other templates carry the full drawing rules;
the ones that matter most:
- Every shape carries its identifier as a custom attribute; every connector carries its
  interface identifier and a label saying what flows.
- Scenarios are layers, not pages.
- Draw the trust zones as labelled boundaries, so the reader sees which connectors cross
  one.
- Every diagram carries a key.

    ![SD-NNN components](./components.svg)
-->

## Patterns Applied

<!--
MANDATORY. The reference architecture or architecture pattern this solution instantiates,
and any narrower patterns it also applies.
-->

| Pattern | Role in this solution |
|---|---|
| RA-NNN Pattern Name | The pattern this solution instantiates |

## Trust Zones and Data

<!--
MANDATORY. The trust zones the solution spans, and every data set it reads, writes,
stores or sends, including logs, telemetry and audit records. A data set used to ground,
fine-tune or evaluate a model says so in Used for AI.
-->

| Trust zone | Trust | What it holds |
|---|---|---|
| TZ-01 Zone name | trusted / partially trusted / untrusted | One clause |

| Data set | Owner | Classification | Personal data | Residency | Retention | Where it comes from | Used for AI |
|---|---|---|---|---|---|---|---|
| DS-01 Data set name | SBB-NNN Official Name | Internal | No | Region | Period | The source and how it is copied | Grounding |

<!-- deck:slide label="Building Blocks" -->

## Building Blocks

<!--
MANDATORY. Every box on the diagram, as a row; the diagram is generated from this table
and validated against it. Kind is one of actor, external-system, local-role, abb, sbb,
technology, service, store or deployment-node. Realises names the building block of the
implemented pattern that this one makes concrete. Source says which pattern the box comes
from, or loose for one no pattern owns.
-->

| Building Block | Role in this solution | Kind | Realises | Bounded context | Owner | Trust zone | Deployed to | Source |
|---|---|---|---|---|---|---|---|---|
| SBB-NNN Official Name | What it does here, one clause | sbb | ABB-NNN Official Name | BC-NNN | Owning team | TZ-01 | Environment or node | RA-NNN |
| 07 Local role name | A role with no catalogue entry yet | local-role | ABB-NNN Official Name | BC-NNN | Owning team | TZ-01 | | loose |

### Pattern Realisation

<!--
MANDATORY. Every building block of the pattern in `implements`, and how this solution
realises it. A building block realised differently from the pattern, or not at all, is a
departure: name the decision that accepts it.
-->

| Pattern building block | Realised here by | Departure | Decision |
|---|---|---|---|
| ABB-NNN Official Name | SBB-NNN Official Name | None | |
| ABB-NNN Official Name | Not realised | Why not | DEC-NN |

### Model-Backed Components

<!--
WHERE ANY BOX CALLS A MODEL. One row per box that does. Role is one of generative,
predictive, classifier, embedding, retrieval, reranker, judge or guard. Input trust is
trusted, mixed or untrusted. Human oversight is in-the-loop, on-the-loop, after-the-fact
or none. Delete the section if no box calls a model.
-->

| Building Block | Role | Model and provider | Version pinned | Hosting | Input trust | Human oversight | Fallback |
|---|---|---|---|---|---|---|---|
| SBB-NNN Official Name | generative | Model, provider | No | Managed platform | mixed | on-the-loop | What happens when it fails |

<!--
How each model-backed box is grounded and what happens to what it produces. Access
control says whose permissions decide what it retrieves: the asking user's, or its own.
Freshness says how soon a change at the source reaches it. Drift monitoring says how a
change in behaviour over time is noticed.
-->

| Building Block | Grounded on | Retrieval | Access control | Freshness | Output shown as | Disclosure | Drift monitoring |
|---|---|---|---|---|---|---|---|
| SBB-NNN Official Name | DS-01 | Hybrid search | The asking user's permissions | Within 15 minutes | Text with citations | How users are told it is AI | How drift is noticed |

### Agents

<!--
WHERE ANY MODEL CALLS TOOLS. One row per box whose model chooses and calls tools. A
configured assistant with no tools is not an agent, whatever the vendor calls it.
Started by is user, event, schedule or self. Tools lists each tool and whether it only
reads or can change something. Acts as is the identity the tools run under: the user's
own, or the agent's.
-->

| Building Block | Started by | Tools, and what each can change | Acts as | Limits | Guardrails |
|---|---|---|---|---|---|
| SBB-NNN Official Name | user | Search (read only) | The user | Steps, time, cost per run | Where each is enforced |

### Evals

<!--
WHERE ANY BOX CALLS A MODEL. How each model-backed box is shown to be good enough, before
release and in service. Positive is the class the eval looks for. Name each kind of error
separately with its own ceiling, because a false positive and a false negative rarely cost
the same. Must never happen is the zero-tolerance error, such as leaking content to someone
not entitled to it, with how it is tested. Sample size says how many cases, which sets how
confident a pass can be.
-->

| Eval | Building Block | Kind | Dataset | Metric | Threshold | Positive | False positive: meaning and ceiling | False negative: meaning and ceiling | Must never happen | Gates release | Sample size |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVAL-01 Name | SBB-NNN Official Name | offline / online / red-team / human review / LLM judge / trajectory | What it is run on | What is measured | The pass mark | What a positive is | What it means, at most N% | What it means, at most N% | The error, and its test | Yes | N cases |

<!-- deck:slide label="Interfaces" -->

## Interfaces

<!--
MANDATORY. Every connector on the diagram, as a row. Contract names the interface and its
version (an API specification, a schema, a connector and its version). Authentication says
how the consumer proves who it is; Authorisation, what decides what it may do. Untrusted
content is yes where the payload can carry text someone outside the solution could have
written or changed, such as documents, web pages, emails or user input, because a model
that reads it can be steered by it.
-->

| Interface | Provider | Consumer | Purpose | Style | Protocol | Contract | Authentication | Authorisation | Data carried | Untrusted content | Errors and retry |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IF-01 | SBB-NNN Official Name | 07 Local role name | What flows and why | request-response | HTTPS | API name v1 | OAuth 2.0, user token | Source system permissions | DS-01 | Yes | Timeout 5s, retry 3x on 503 |

## Quality, Failure and Misuse Scenarios

<!--
MANDATORY. What the solution promises under load, under failure and under attack, each
with a measure that can be tested. Kind is quality, failure or misuse. Importance and
Difficulty are high, medium or low: how much the scenario matters to the stakeholders,
and how hard the design finds it to meet. At least one of
each kind, and a quality scenario for every goal with a measure.
-->

| Scenario | Kind | Quality attribute | Source | Stimulus | Environment | Artefact | Response | Response measure | Importance | Difficulty |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 Name | quality | Performance | Staff | 200 users ask at once | Normal operation | The assistant | Answers returned | p95 under 8s | high | low |
| F1 Name | failure | Availability | The source system | It is unavailable | Business hours | The assistant | Says it cannot answer, and why | No invented answer | high | medium |
| M1 Name | misuse | Security | Someone outside | A document carries hidden instructions | Normal operation | The assistant | Instructions ignored | Zero actions taken on them | high | high |

### Fitness Functions

<!--
RECOMMENDED. The automated checks that keep the promises above true after release: what
each measures, its threshold, when it runs (each build, each deploy, on a schedule or
continuously) and the scenarios it protects.
-->

| Fitness function | Characteristic | Measure | Threshold | Automated | Runs | Scenarios |
|---|---|---|---|---|---|---|
| FF-01 Name | Security | What is measured | Zero | Yes | deploy | M1 |

## Scenarios

<!--
RECOMMENDED. Two to four functional flows, each a straight line of five to ten steps,
tied to the use case it serves. They become the animated walkthrough. A flow with branches
or failure handling belongs in a sequence diagram; say so in one line.
-->

Step through them in the [animated scenario walkthrough](./scenarios.html): each step is numbered on the acting box, the arrow is drawn to its target and the rest of the diagram dims. It opens from disk; arrow keys step and space plays.

<!-- deck:html src="./scenarios.html" title="Scenario walkthrough" header="true" -->

### S1 Scenario name

<!-- One sentence on what this scenario proves, and the use case it serves: UC-NNN. -->

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 07 Local role name | SBB-NNN Official Name | What happens | IF-01 |

## Controls and Guardrails

<!-- MANDATORY. The enforceable controls this solution relies on, and where each is
enforced. -->

| Control | Source standard or policy | Enforcement point |
|---|---|---|
| Control statement | Standard or policy | Build / Release / Runtime |

### Cross-Cutting Concerns

| Concern | How it is discharged here |
|---|---|
| Identity | Which building block, which interface |
| Observability | What is logged and traced, and where it goes |

<!-- deck:slide label="Operations" -->

## Operations

<!--
MANDATORY. How the solution is run once it is live. Every row needs an answer before the
solution goes into production; an early design may leave some blank.
-->

| Aspect | What the design commits to |
|---|---|
| Service levels | Availability and response time objectives, and how they are measured |
| Observability | What is monitored, the alerts, and who receives them |
| Deployment | How a change reaches production, and how it is rolled back |
| Recovery | Recovery time and recovery point objectives, and how they are tested |
| Cost | The cost model, the expected monthly cost, and any cap |
| Support | Who supports it, during what hours, and how a user reaches them |
| Transition | How users and data move to it, and what it replaces |

## Decisions

<!--
RECOMMENDED. Each decision the solution rests on, with what was rejected and why, and how
hard it would be to reverse. Departure is set where the decision steps away from the
implemented pattern or a standard; say what it departs from, until when, and the way back.
-->

| Decision | Chosen | Alternatives rejected | Rationale | Reversibility | Departure |
|---|---|---|---|---|---|
| DEC-01 Decision title (accepted) | What was chosen | First alternative; second alternative | Why | Two-way door / costly / one-way door | None |

## Open Questions

<!-- MANDATORY. Every question the design has not yet answered, with who owns it. A design
with no open questions is not believed. -->

| Question | Options | Owner | Needed by |
|---|---|---|---|
| What is not yet decided | First option; second option | Who decides | Date |

## Risks and Trade-offs

| Risk or trade-off | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Risk statement | Low / medium / high | Low / medium / high | Mitigation | Who owns it |

## Evidence

<!--
RECOMMENDED. What has been produced to show the design works: tests, eval runs, load
tests, proofs of concept, reviews. Each with its date and the version of this design it was
produced for, so stale evidence is visible.
-->

| Evidence | Kind | Date | Design version | Outcome |
|---|---|---|---|---|
| Link or path | eval report / load test / threat model / cost model / other | 2026-10-28 | 0.1.0 | passed / passed with conditions / failed |

## Catalogue Mapping

<!-- WHERE ANY BOX HAS A LOCAL NUMBER. What each local box realises, partly covers, or
leaves as a gap, until its catalogue entry exists. Delete if every box is catalogued. -->

| Local ID | Maps To | Relationship | Note |
|---|---|---|---|
| 07 | ABB-NNN Official Name | partial | What is missing |
