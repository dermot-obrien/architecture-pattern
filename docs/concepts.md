<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Concepts

The ideas you need to use the `pattern` skill, in the order you meet them. The [quick start](quick-start.md) shows each one working.

## One document is the source

A pattern is one Markdown file, usually `<outputDir>/<ID>-<slug>/index.md`. It is three things at once:

| It is | Because |
|---|---|
| The document | People read it on a docs site or in the repository |
| The model | Its Building Blocks, Interfaces and scenario steps tables are the boxes, the lines and the flows |
| The deck | Its tagged sections become HTML slides and a PDF |

Everything else is generated from it and checked against it: the draw.io diagram, the rendered view, the animated walkthrough and the deck. Nothing generated is edited by hand except the diagram's layout.

## Three skills, one job

| Skill | Repository | Does |
|---|---|---|
| `pattern` | this one | The method: the template, the section structure, the procedure an agent follows, and `publish.py`, which runs the rest in order |
| `model` | [diagram-model](https://github.com/dermot-obrien/diagram-model) | Reads the tables, writes and syncs the draw.io diagram, validates the two against each other, renders views, animates scenarios, resolves compositions and reads the binding file |
| `markdown-deck` | [markdown-deck](https://github.com/dermot-obrien/markdown-deck) | Turns the `deck:` tags into HTML slides and a PDF |

`pattern` ships no engine of its own. It stops with an instruction if either of the others is missing, rather than improvising a substitute, because the identifier conventions and the tag vocabulary are what keep the three parts in agreement.

## Bindings: the skills know nothing about your repository

A published skill cannot know where your patterns go, what your identifiers look like or which theme your decks use. The repository says so in one file, `.agents/skill-bindings.toml`, found by searching upward from the document. Each skill declares what it needs in its `inputs.toml`; `pattern` asks for `[suite.pattern]`, and `model` reads `[model]`, `[[markdown.tables]]` and the sections beside them. Relative paths in the file are relative to the file itself, never to where a command is run.

`model doctor --skill pattern` checks the bindings against the contract and prints every resolved path. An agent runs it before anything else. See the [configuration reference](configuration.md).

## What a pattern is

Every architecture model is a pattern: building blocks, the interfaces between them, and the scenarios that walk across them. It is reusable as a reference, where a solution design instantiates one for one consumer. What is often called a reference architecture is a pattern with a wide scope, authored the same way.

Patterns differ by semantic type, which has two parts.

Scope is what you declare in front matter as `pattern_scope`:

| Scope | Answers | Opens with |
|---|---|---|
| `problem` | One recurring problem. Usually short | `## Intent`: the problem, the forces, the invariant it enforces |
| `domain`, `capability-area`, `platform`, `hosting-profile`, `epic` | A composed design | `## Context` and `### Non-Goals`, then Patterns Applied names the narrower patterns it uses |

Abstraction is derived by `model validate` from the kinds of box, and never declared:

| Abstraction | When |
|---|---|
| `conceptual` | Every box is a local role such as `01 Gateway` |
| `logical` | The boxes are catalogued logical building blocks, with or without local ones |
| `physical` | Every box is a catalogued product |
| `mixed` | Anything else, including any box whose kind is unknown |

A conceptual pattern explains and scopes. One that a team will build from must be physical. A catalogue declares its level in the binding (`[[catalogues]] level`), which is how `validate` knows what a `COMP-001` is.

## The tables are the model

Three tables carry the model; the binding file names their sections and columns.

| Table | Becomes | Key columns in the template |
|---|---|---|
| Building Blocks | One shape per row | Building Block (id and name), Source (the group) |
| Interfaces | One labelled connector per row | Interface, Provider, Consumer, Purpose |
| A scenario's steps, under `### S1 <name>` in Scenarios | One numbered overlay step per row, on the scenario's own layer | Step, Actor, Target, Action, Interface, and Uses for a composite pattern |

Write each endpoint (Provider, Consumer, Actor, Target) as the identifier followed by the name, `COMP-001 Payment gateway` or `02 Order service`. The model reads only the leading identifier; the name is for the reader and the slide. `scripts/name-endpoints.py` fills in names from Building Blocks.

## Identifiers

A box carries either a catalogue identifier, matched by the table's `id_pattern` (`COMP-001` in the template), or a local id for a role with no catalogue entry yet. With `local_pattern = '[0-9]{1,3}'` a local id is a plain number leading its cell, `01 Web shop`. Each local box gets a row in `## Catalogue Mapping` saying what it `realises`, what it `partial`ly covers, or that it is a `gap`. Never invent a catalogue id to get past validation; when the entry exists, `model rename` promotes the local id in the document and the diagram together.

On the diagram, the identifier lives on the draw.io object wrapper as a custom attribute (`component_id`, `iface_id`, or whatever the binding names), not on the cell id, because draw.io regenerates cell ids on copy and paste. That one convention is what lets a shape be matched to its table row across edits, and why a copy-pasted shape is caught as a duplicate.

## The document owns what exists; the diagram owns where it sits

`model emit` writes the diagram once, on a plain grid. You arrange it in draw.io. From then on `model sync` reconciles: it adds shapes for new rows, marks (or with `--prune` deletes) shapes with no row, rebuilds the scenario layers, and keeps every position you set. `emit` again would throw the layout away, so it refuses to overwrite an existing diagram without `--force`.

`model validate` compares the two and reports what the eye misses: an interface wired one way in the table and another on the canvas, an overlay step whose endpoints disagree with its metadata, an identifier drawn twice.

## Scenarios are layers, and the walkthrough shows them

A scenario is a straight-line flow of roughly five to ten steps, drawn as numbered badges and arrows on its own layer over the Structure layer. Layers, not pages: duplicating a page regenerates every cell id, so overlay arrows would stop pointing at the real boxes.

A communication diagram cannot show branching, loops, concurrency or failure paths. Keep two to four scenarios of the happy path, and put real alternatives in a sequence diagram, saying so in one line where the reader expects the overlay.

The structure is the one static image, `components.svg`. The scenarios are shown by `scenarios.html`, a self-contained page generated by `model animate` that steps through each scenario on that image: the step's number on the acting box, the arrow to its target, the rest dimmed. Link it at the top of Scenarios and give it one `deck:html` slide. Scenario sections carry their steps table but no image and no slide of their own.

## Views are stamped

A rendered view has a record beside it, `components.svg.render.json`, naming the diagram and layers it was made from and the diagram's SHA-256 at the time. `model stamp --check` says whether the view is still current. `publish.py --render auto` re-renders a stale view when draw.io desktop is installed and otherwise refuses to publish it, so a deck never shows a picture of a diagram that has since changed. Without draw.io, export the view by hand and `model stamp` it.

## The deck is a selection

`<!-- deck:cover -->` after the H1 makes the cover. `<!-- deck:slide label="..." -->` before a heading makes that section a slide. `<!-- deck:skip -->` ... `<!-- /deck:skip -->` keeps detail in the document and off the slide, and `<!-- deck:note -->` makes presenter notes. Tag the six to twelve sections an audience needs; the rest stay document-only. The tags are HTML comments, invisible wherever the Markdown is rendered. markdown-deck's own documentation has the full vocabulary.

## Composite patterns

A composite pattern's scenario steps run other patterns' flows, its participating patterns. A `Uses` column on the steps table names, on a participation step, the participating pattern's id and scenario key, `PAT-001 S1`, optionally with a role binding of its boxes to this pattern's, `PAT-001 S1 (01=01, 03=02)`, or `TBD <name>` for one not yet written. A scenario another pattern runs declares `Start:` and `Finish:` under its heading. An approved pattern cannot rest on an unapproved or unwritten one. [Composing patterns](composing.md) covers it in full.

## Links from each box to its page

When the binding file has `[[links]]` rules, every declared identifier in the walkthrough and in draw.io links to its page on your docs site: a building block, a product, a pattern, a capability. Local ids never link. In body text, never hyperlink an identifier yourself; write the plain id and name, and let publishing rewrite them. See [configuration](configuration.md#links-from-boxes-to-pages).

## Capabilities and evidence

A pattern may name the capabilities it realises in front matter, `realises: [CAP-012]`, optionally scoped to some of their `flows`, with `references` of type `cost-model` and `evidence`. The skill records these and does not interpret them; a capability model that reads them decides what they are worth. A logical pattern shows a capability's building blocks are decided; a physical one with a cost model shows it can be built and costed; add evidence and it has been tried.

## The section structure

Each section of the template answers a documented failure mode or a standards requirement:

| Section | Why it is there |
|---|---|
| Intent, or Context and Non-Goals | Intent states what makes a pattern reusable. For a wide scope, adoption for legitimacy rather than fit is the dominant failure, and non-goals are the cheapest mitigation |
| Quality Attributes | Six-part scenarios with response measures, so conformance is testable |
| Diagram, Building Blocks | The component view: arc42's Building Block View, C4's Component level |
| Interfaces | TOGAF's minimum building-block specification includes interfaces, and integration points are the primary stability risk |
| Scenarios | Kruchten's "+1" view, whose stated purpose is validating the design |
| Cross-Cutting Concerns | Identity, security, observability and retry belong to no single component, so a components-and-interfaces structure loses them |
| Variation Points | A path with no escape hatch for legitimate edge cases is abandoned |
| Decisions, Risks | ISO/IEC/IEEE 42010 requires decisions and rationale. A document claiming no gaps is not believed |

Aim for at most about ten pages, far less for a problem-scope pattern. Tables carry the volume; prose is for the architecturally significant minority.
