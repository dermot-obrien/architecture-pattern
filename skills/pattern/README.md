<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# pattern

An agent skill for authoring an architecture pattern, at any scope from one recurring problem to a whole domain, as one Markdown document that is also the model and also the deck. What is often called a reference architecture is a wide-scope pattern.

The document's tables generate the draw.io diagram and its numbered scenario overlays. The document's tagged sections generate HTML slides and a PDF. Both are checked back against the document, so a diagram that drifts is caught rather than believed.

It began as part of [AI-Assisted Architecture](https://github.com/dermot-obrien/ai-assisted-architecture); see [NOTICE](./NOTICE).

## Requires

This skill is composition. The work is done by two others:

| Skill | Does | Comes from |
|---|---|---|
| [model](https://github.com/dermot-obrien/diagram-model) | Generates, syncs, validates and renders the diagram from the document's tables | Its own repository, diagram-model |
| [markdown-deck](https://github.com/dermot-obrien/markdown-deck) | Turns tagged sections into HTML slides and a PDF | Its own repository |

`SKILL.md` declares both in `metadata.x-skill-requires`. The Agent Skills specification has no dependency field yet and no agent installs dependencies from it, so this skill checks for them and stops with an instruction rather than improvising. It looks for each beside itself, then on `AGENT_SKILLS_PATH`, then in every project and user skills directory that VS Code with GitHub Copilot, Cursor, Claude Code, Codex and Gemini CLI read, then among Claude Code plugins.

## Requirements

Python 3.11 or newer and Node 18 or newer. Run `npm install` once where `markdown-deck` is installed; from markdown-deck 0.6.1 that also installs [Playwright](https://playwright.dev/) for PDF export, which prints with Microsoft Edge or Google Chrome where either is installed, so no browser download is needed on Windows. draw.io desktop is optional.

## Install

Install `pattern`, `model` and `markdown-deck` wherever your agent reads skills: VS Code with GitHub Copilot, Cursor, Claude Code, Codex, Gemini CLI or any other agent that reads the Agent Skills format. See the [repository README](https://github.com/dermot-obrien/architecture-pattern#install) for every route.

```bash
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
```

## Use

Bind the workspace in `.agents/skill-bindings.toml` (at least `[suite.pattern] outputDir`, and the tables the model reads), copy `assets/template.md` into a new folder under `outputDir` as `index.md`, fill it in, and declare `model: diagram: components.drawio` in its front matter. Then, with `<skills>` the folder the skills are installed in:

```bash
python <skills>/model/bin/model.py emit index.md --to drawio --out components.drawio   # once
python <skills>/model/bin/model.py sync index.md components.drawio                     # thereafter
python <skills>/model/bin/model.py validate index.md
python <skills>/pattern/scripts/publish.py <folder>                                     # view, walkthrough, deck, PDF
```

Or ask your agent for a pattern, and it follows `SKILL.md` to do all of it.

## Documentation

The repository's [docs](https://github.com/dermot-obrien/architecture-pattern/tree/main/docs) have a [quick start](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/quick-start.md) from an empty folder to a published pattern and a composite pattern, the [concepts](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/concepts.md), a [configuration reference](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/configuration.md) with a complete binding for the template, a [command reference](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/commands.md) and [troubleshooting](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/troubleshooting.md) for every error message.

[examples/knowledge-retrieval](./examples/knowledge-retrieval) is a complete worked example with a `run.sh` that produces every output.

## Composing patterns

A composite pattern's scenario steps run other patterns' flows through an optional Uses column, `PAT-905 S1`, or mark an open participating pattern, not yet written, `TBD <name>`, and may bind its boxes to the composite pattern's, `PAT-905 S1 (01=03)`. A scenario declares where its flow starts and finishes with `Start:` and `Finish:` lines. Each participating pattern is drawn as a dashed region on the diagram's `Participating patterns` layer, and a participation step carries BPMN's `[+]` call-activity marker. The notation follows UML 2.5.1 collaboration use and ports and BPMN 2.0.2 call activity and start and end events. Sketch a composite pattern top down with open participating patterns and solve each as its own pattern, or compose approved patterns. `model composition index.md` prints the composition tree, `validate` checks it and its approval gate, and the walkthrough drills into each participating pattern's. [examples/composite](./examples/composite) runs the knowledge-retrieval example. See `SKILL.md`, step 6.

## Tying it to capabilities

A pattern may declare `realises: [CAP-NNN]` in its front matter, with optional `flows` and `references` of type `cost-model` and `evidence`. A capability model can then count it as evidence of how far each capability has been defined. See `SKILL.md`.

## What makes it hold together

The document owns what exists and what connects to what. The diagram owns where things sit. Neither is a copy of the other, and `sync` is what keeps both true at once.

Identifiers live on the draw.io object wrapper, not the cell id, because cell ids do not survive copy and paste. That one convention is what lets a shape be matched to a table row across edits, and it is why duplicate detection works at all.

Scenarios are layers, not pages. Generated from the steps table, they are contiguous and endpoint-correct by construction.

## Licence

Content under [CC BY 4.0](LICENSES/CC-BY-4.0.txt) and code under [Apache-2.0](LICENSES/Apache-2.0.txt). See [LICENSE](./LICENSE), and keep [NOTICE](./NOTICE) with any copy or derivative.
