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

Python 3.11 or newer and Node 18 or newer. PDF export additionally needs [Playwright](https://playwright.dev/) (`npm install playwright` where `markdown-deck` is installed); it prints with Microsoft Edge or Google Chrome where either is installed, so no browser download is needed on Windows. draw.io desktop is optional.

## Install

Install `pattern`, `model` and `markdown-deck` wherever your agent reads skills: VS Code with GitHub Copilot, Cursor, Claude Code, Codex, Gemini CLI or any other agent that reads the Agent Skills format. See the [repository README](https://github.com/dermot-obrien/architecture-pattern#install) for every route.

```bash
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
```

## Use

Copy `assets/template.md` into a new folder as `index.md` and fill it in. Then:

```bash
python ../model/bin/model.py emit index.md --to drawio --out components.drawio   # once
python ../model/bin/model.py sync index.md components.drawio                     # thereafter
python ../model/bin/model.py validate index.md --against components.drawio
python ../model/bin/model.py render components.drawio --out components.svg --layer Structure
node ../markdown-deck/bin/markdown-deck.mjs build index.md --out dist --pdf
```

Or let `scripts/publish.py <folder>` do all of it for every pattern in a folder.

[examples/knowledge-retrieval](./examples/knowledge-retrieval) is a complete worked example with a `run.sh` that produces every output.

## Tying it to capabilities

A pattern may declare `realises: [CAP-NNN]` in its front matter, with optional `flows` and `references` of type `cost-model` and `evidence`. A capability model can then count it as evidence of how far each capability has been defined. See `SKILL.md`.

## What makes it hold together

The document owns what exists and what connects to what. The diagram owns where things sit. Neither is a copy of the other, and `sync` is what keeps both true at once.

Identifiers live on the draw.io object wrapper, not the cell id, because cell ids do not survive copy and paste. That one convention is what lets a shape be matched to a table row across edits, and it is why duplicate detection works at all.

Scenarios are layers, not pages. Generated from the steps table, they are contiguous and endpoint-correct by construction.

## Licence

Content under [CC BY 4.0](LICENSES/CC-BY-4.0.txt) and code under [Apache-2.0](LICENSES/Apache-2.0.txt). See [LICENSE](./LICENSE), and keep [NOTICE](./NOTICE) with any copy or derivative.
