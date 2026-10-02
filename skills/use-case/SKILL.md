---
name: use-case
description: Author a use case as one Markdown document that is also the model and also the deck. A use case says what a solution does for someone and what it needs, before anyone designs how it is built. Creates the document from a template, generates the draw.io diagram of its participants and interactions and an animated walkthrough of its main flow from its own tables, validates that the diagram and the document agree, and publishes HTML slides and a PDF. Use when asked to write, specify, scope, review or publish a use case, a solution idea, a user journey with its participants, or the case for building something, including what it returns, its scope, data, dependencies, measures, risks and next step.
license: CC-BY-4.0 AND Apache-2.0. Content under CC BY 4.0, code under Apache-2.0; see LICENSE and NOTICE.
compatibility: Python 3.11+ and Node 18+. Requires the `pattern` skill (this repository), the `model` skill (diagram-model repository) and the `markdown-deck` skill (markdown-deck repository), installed wherever the agent reads skills. draw.io desktop is optional; without it, views are exported by hand and stamped. PDF export needs playwright.
metadata:
  version: "0.1.0"
  homepage: https://github.com/dermot-obrien/architecture-pattern
  x-skill-requires: "pkg:generic/dermot-obrien/architecture-pattern/pattern ^0.10.3, pkg:generic/dermot-obrien/diagram-model/model ^0.8.2, pkg:generic/dermot-obrien/markdown-deck/markdown-deck ^0.6.0"
---

# Use case

A use case says what a solution does for someone and what it needs, before anyone designs how it is built. A pattern says how it is built, and a use case names the patterns that realise it. Like a pattern, one document is the source: the diagram and the walkthrough are generated from its tables, the deck from its sections, and both are checked against it.

People learning the skill, rather than agents running it, start from https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/use-cases.md.

## Step 0, before anything else

Run the resolver and use only the paths it prints:

```bash
python <skills>/model/bin/model.py doctor --skill use-case --json
```

`<skills>` is the directory this skill is installed in, where `model` and `pattern` usually sit beside it. If there is no `<skills>/model`, look in the other skills directories agents read (`.agents/skills`, `.github/skills`, `.cursor/skills`, `.claude/skills` in the project, and the same under the home directory, plus `~/.copilot/skills`). If it is in none of them, stop and tell the user to install it from https://github.com/dermot-obrien/diagram-model. The command prints the sibling skills wherever they are installed, the resolved paths for every binding, and a `result` of `ok`, `warn` or `error`.

`python scripts/check.py`, run from the workspace root, is the post-install check: it confirms `pattern`, `model` and `markdown-deck` are installed, then runs the same `doctor`.

Do not proceed on an error, and do not guess a path. Every path this skill needs comes from that output:

| Binding | Used for |
|---|---|
| `siblings.model` | The model CLI, at `<that>/bin/model.py` |
| `siblings.pattern` | `publish.py`, at `<that>/scripts/publish.py` |
| `siblings.markdown-deck` | Used by `publish.py` to build the deck |
| `outputDir` | Where a new use case folder is created |
| `idSeries` | The prefix for a new use case's id, `UC` by default. Take the next free number in it |
| `template` | The repository's own template, if it declares one. Otherwise use `assets/template.md` from this skill |

The contract is declared in `inputs.toml` beside this file. The repository answers it in `[suite.use-case]` of its `.agents/skill-bindings.toml`.

## Prerequisites

| Skill | Why |
|---|---|
| `pattern` | Its `publish.py` renders the view, animates the flows and builds the deck, for use cases exactly as for patterns |
| `model` | Generates and validates the diagram from the document's tables, and resolves the bindings above |
| `markdown-deck` | Turns tagged sections into HTML slides and a PDF |

If `doctor` does not list all three under `siblings`, stop and tell the user to install the missing one. Do not improvise a substitute.

## The tables the model reads

The repository's binding file must map the template's Participants and Interactions sections, alongside any pattern tables. Add these to `.agents/skill-bindings.toml`, or to a `model.toml` beside the use case:

```toml
[[markdown.tables]]
section    = "Participants"
entity     = "node"
id_pattern = 'ABB-[0-9]{3}|SBB-[0-9]{3}'
columns    = { id = "Participant", label = "Participant", group = "Kind" }

[[markdown.tables]]
section    = "Interactions"
entity     = "edge"
id_pattern = 'IF-[0-9]{2,3}'
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }
```

With `local_pattern` set under `[model]`, participants can be local roles (`01 Architect`) until a catalogue entry exists. Kind (actor, solution, product, external) becomes the box's group, which a layout can colour by. The Scenarios binding is the one patterns use.

## Procedure

### 1. Create the document

Copy the template into `<outputDir>/<ID>-<slug>/index.md`, using the `template` binding if the repository declares one and `assets/template.md` from this skill if it does not. Fill it in this order, which is not document order:

1. The solution in one sentence: [who] uses [what] to [do what], so that [outcome]; the problem today; what is different afterwards. If it will not fit one sentence, it is two use cases.
2. Participants, five to eight, each with a kind. Write each as the identifier followed by the name (`01 Architect`).
3. Interactions: every real call or handover between participants, each with a purpose short enough to be an arrow label.
4. S1, the main flow, five to eight steps over those interactions. Add `S2` only for a materially different path, such as a set-up or an exception that changes who acts.
5. What it returns, Scope (first version, later, out), Data it needs, Systems it reads or acts on, Dependencies and Measures.
6. Risks and assumptions and Open decisions, which are the residue of everything above, then the Next step.

### 2. Generate and check the diagram

```bash
python <model>/bin/model.py emit index.md --to drawio --out components.drawio
python <model>/bin/model.py validate index.md
```

Arrange the generated grid in draw.io and save; from then on use `model sync index.md components.drawio`, never `emit`. Report every finding `validate` makes.

### 3. Publish

```bash
python <pattern>/scripts/publish.py <use case folder>
```

It renders `components.svg`, builds the animated walkthrough `scenarios.html` of S1 and S2, and builds `dist/<name>/deck.html` and `deck.pdf` from the template's deck tags. Every flag the pattern skill documents applies: `--render never` on a machine without draw.io, `--no-deck` for a site build that builds its own decks, `--recursive` over a folder of use cases.

## Use cases and patterns

A use case lists the patterns that realise it in its front matter, `realised_by: [PAT-004]`, and in its header table. A pattern that serves a use case can say so in its Intent. Write the use case first when the question is whether to build something; write the pattern first when the question is how. Neither validates the other yet.

## Rules that are easy to get wrong

A participant is someone or something that acts or is acted on, not a step. If a box has no interaction, it does not belong on the diagram.

A use case does not design. When its interactions start naming databases, queues and endpoints, that detail belongs in the pattern that realises it.

A scenario is a straight-line flow. Branches, loops and failures go in prose or in a pattern's sequence diagram.

Every claim in Risks and assumptions has a test, and every open decision has an owner and a date. A use case whose next step is "proceed" with an open decision on its critical path is not ready.

## Reporting back

Say which use case was created or changed, where its deck and walkthrough were published, what `validate` reported, and every open decision and unverified assumption the document still carries.
