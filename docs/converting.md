<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Converting existing material

Most architecture already exists somewhere: a draw.io file on a shared drive, an SVG pasted into a wiki, a PNG exported from a slide, with a page of notes beside it or nothing at all. The `convert` skill turns that material into a document of the right pattern type, which the `pattern` and `use-case` skills then own: they regenerate its diagram from its tables, check that the two agree, animate its scenarios and publish it.

## What it produces

Every pattern type has the same essence, so conversion looks for the same four things in every source:

| Part | In the source | In the document |
|---|---|---|
| A diagram | The draw.io, SVG or PNG | `components.drawio`, generated from the tables or adopted from the source's own drawing, and its view `components.svg` |
| The boxes | Shapes and their labels; a components table or list in the text | Building Blocks, or Participants |
| The links | Arrows and their labels; a From and To table, or `A -> B: what flows` | Interfaces, or Interactions |
| The sequences | Numbered arrows, a scenario layer, a mermaid sequence diagram, a numbered list of steps | Scenarios, S1 onwards, with the animated walkthrough |

It drafts one of four types:

| Type | When | Template |
|---|---|---|
| Architecture pattern | The boxes are capabilities, services and logical containers, ABBs | `pattern`'s `architecture-pattern` |
| Reference architecture | The boxes name products and technologies, SBBs | `pattern`'s `reference-architecture` |
| Use case | Someone has a goal: actors, "as a ... I want ... so that" | `use-case`'s template |
| Collaboration | Participants working together, without building-block rigour: teams, boards, handovers | `pattern`'s `collaboration` |

The type is chosen from the content, and the conversion report says why, with the score each type earned. You can always name it instead. [The skill's types reference](../skills/convert/references/types.md) lists the evidence each type scores.

### The collaboration type

A collaboration is new in `pattern` 0.13.0. It is a pattern of participants, people, teams, boards, systems and outside parties, and what passes between them, with the four essential parts and very little else: Purpose, the diagram, Participants, Interactions and at least one scenario are required; Agreements, Open Questions and Catalogue Mapping are optional. Its tables are a use case's, so a workspace that binds use cases reads collaborations with no change. To number them in their own series, bind the type:

```toml
[suite.pattern.types.collaboration]
label    = "Collaboration"
idSeries = "CL"
```

## What it needs

| Skill | Why |
|---|---|
| `convert` | This skill |
| `pattern` 0.13.0 or later | Its templates, its `register.py` numbering, and `publish.py` |
| `use-case` | The use case template |
| `model` 0.9.0 or later | Reads an identified draw.io exactly, adopts identifiers onto a drawing, validates and stamps |
| `markdown-deck` | Only to build the deck when you publish |

Install them as the [README](../README.md#install) describes, with `convert` beside `pattern`, and run `python <skills>/convert/scripts/check.py` from the workspace root. Python 3.11 or newer, and git if originals are to be archived. draw.io desktop is optional.

## Pointing it at your own material

Ask your agent to convert the material, naming the folder or files: "convert everything in `old-diagrams/` into patterns", or "convert `payments.drawio` and `payments-notes.md` into a reference architecture". The agent runs the commands below, reads any picture itself, completes the documents and tells you what it found. To run them yourself, `<skills>` being where the skills are installed:

```bash
python <skills>/convert/scripts/convert.py run old-diagrams --dry-run
python <skills>/convert/scripts/convert.py run old-diagrams
```

The first prints the plan and changes nothing: each unit found, what was read, the type it would choose and why, where the document would go, and what happens to each original. The second carries it out.

### Arranging the sources

| You have | Do |
|---|---|
| A folder of diagrams, each with notes of the same name | Point at the folder. `payments.drawio` and `payments.md` are one unit |
| A folder per diagram, with a README | Point at the parent. A folder holding one diagram pairs it with every text in that folder |
| Notes that embed or link a picture, `![](payments.png)` | Nothing: a text that links to a diagram goes with it, wherever it is |
| The same diagram as `.drawio`, `.svg` and `.png` | Nothing: they are one unit, read from the most structured |
| Individual files from different places | Name each one: `convert.py run a.drawio notes/a.md b.svg` |
| A multi-page draw.io | Nothing: each page that draws anything is its own document, and the pages share a type |

A text that goes with no diagram is listed in the plan as unpaired and left alone. Rename it to match its diagram, or name both files, and run again.

### What gives the best result

| Source | Read | Tip |
|---|---|---|
| draw.io | Exactly, from its shapes, containers, labels, arrowheads and layers | The best source. Number the arrows of a flow, `1. submit order`, and they become a scenario; a layer holding only arrows becomes one too |
| SVG exported from draw.io with "Include a copy of my diagram" | As draw.io | Export with the copy included whenever you can |
| PNG exported from draw.io with the same option | As draw.io | As above |
| Any other SVG | Best-effort, from its shapes, lines and text | Check the comparison in the report; arrows drawn as separate shapes can be missed |
| A picture | By the agent, looking at it | The agent marks anything it cannot read for certain, and you check it against the picture |
| Markdown | A title and summary, descriptions from a components table or `Name: what it does` bullets, link labels, and scenarios from a mermaid `sequenceDiagram`, a steps table or a numbered list under a heading such as Flow or Steps | A numbered step that names its actor first and its target second, by the boxes' names, reads best |

### Where things go

Each run makes one conversion folder, `conversions/<date>-<name>/` at the repository root unless `[suite.convert] workDir` says otherwise:

| Item | Holds |
|---|---|
| `sources/` | A copy of every source, by unit |
| `manifest.json` | Where each source came from, its SHA-256, and where it was archived |
| `units/<unit>/source.json` | What was read from the source |
| `units/<unit>/unit.json` | What the document is drafted from; correct it and redraft |
| `report.md` | Per unit: how it was read, the type and why, the document, what validation and the comparison with the source found, and what is uncertain |

Documents go where the `pattern` and `use-case` skills put them, each type's `outputDir` (by default `patterns/` and `use-cases/` at the repository root), numbered in the type's series from the register when one is bound, and registered. `--out <folder>` puts them all in one folder instead.

### What the front matter says

A document is found by its front matter, never by its file or folder name, so every document convert writes opens with the same signature:

| Key | Value |
|---|---|
| `kind` | `pattern`, or `use-case` |
| `id`, `title` | The identifier and the name |
| `pattern_type`, `pattern_scope` | For a pattern: its type, and its scope. The scope is `problem` for up to eight boxes and `domain` above, unless the unit sets it, and the conversion notes ask you to confirm it |
| `status` | `Draft` |
| `provenance`, `converted_from` | `origin: ai-generated`, `review_state: ai-raw`, and where each source is now kept |

A source that cannot be converted yet, a picture waiting for the agent, gets a placeholder in its place: `kind: candidate`, `candidate_type` when the type is known, and `portfolio.state: needs-conversion` with the reason and the date, so a portfolio lists it as work outstanding. `convert.py draft` removes the placeholder when it writes the real document, unless someone has edited it.

### Archiving the originals

When git tracks a source, the run moves it with `git mv` into the archive folder, at the same path below it as below the repository root: `docs/old/payments.drawio` becomes `archive/docs/old/payments.drawio`. History follows it, and the new document's `converted_from` points at it. A source outside git, or one git does not track, is copied and left where it is. Nothing is ever deleted, and an archive path already taken is never overwritten.

`[suite.convert] archiveDir` moves the archive folder; unset, `[suite.portfolio] archiveDir` is used when bound, so one repository has one archive. `--no-archive` copies without moving; `convert.py archive <conversion folder>` archives later. The moves are staged, not committed: review them, then commit them with the new documents.

### After the run

Read `report.md`. For each unit:

1. A unit marked `needs-agent` is a picture. The agent reads it and writes its boxes, links and scenarios into `units/<unit>/unit.json`, then runs `convert.py draft <conversion folder>`. [The unit model](../skills/convert/references/unit-model.md) describes the file.
2. Check the type. If it is wrong, set `type` in `unit.json` and run `convert.py draft <conversion folder> --unit <unit> --force`, before anyone edits the document.
3. Check the comparison. "Agrees" means every box and line in the source is in the document and nothing else is; anything listed is a reading to fix or a decision to make.
4. Work through the `CONVERSION NOTES` comment under the document's H1, the `TBD` cells, and the `Notes from the source` section at the end, then complete the template's other sections from the source text.
5. Arrange the diagram in draw.io if it was generated, then `model sync`, never `emit`, after any table change. Render or export the view and stamp it, since the converted one is a plain preview where draw.io desktop was not installed.
6. Publish: `python <skills>/pattern/scripts/publish.py <folder>`, for every type.

## Bindings

All optional, in `[suite.convert]` of `.agents/skill-bindings.toml`, relative to that file:

| Key | Default | Sets |
|---|---|---|
| `workDir` | `conversions/` at the repository root | Where each run's conversion folder is made |
| `archiveDir` | `[suite.portfolio] archiveDir`, else `archive/` at the root of the repository holding each source | Where originals tracked by git are moved |

Where documents go, how they are numbered and which template each type uses are the `pattern` and `use-case` skills' own bindings. When the binding file maps the type's tables and sets `[model] local_pattern`, the document reads with it; otherwise a `model.toml` is written beside the document so it reads on its own, and the report says so.

## Commands

| Command | Does |
|---|---|
| `convert.py run <paths>... [--type T] [--out DIR] [--work DIR] [--name N] [--id ID] [--no-archive] [--dry-run] [--json]` | Plans, gathers, archives, reads, chooses, drafts, checks and reports |
| `convert.py draft <conversion folder> [--unit U] [--force] [--json]` | Drafts again from each `unit.json` |
| `convert.py read <diagram> [--text FILE ...]` | Prints the unit model read from one diagram and its texts |
| `convert.py verify <document> [--source source.json] [--json]` | Validates a document, and compares its regenerated diagram with a source |
| `convert.py archive <conversion folder> [--dry-run]` | Archives the originals of a run made with `--no-archive` |

`T` is `architecture-pattern`, `reference-architecture`, `use-case` or `collaboration`, or `AP`, `RA`, `UC`, `CL`. Exit codes: 0 every unit drafted and valid, 1 a unit needs the agent or did not draft or validate, 2 usage, 3 a skill this one needs is not installed.

## Examples

[skills/convert/examples](../skills/convert/examples/README.md) holds generic sources in every format, with rich, sparse and no text, and all four types, and the units an agent writes for its two pictures. The tests convert all of them and publish the results.
