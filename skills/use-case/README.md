<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# use-case

An agent skill for authoring a use case as one Markdown document that is also the model and also the deck. A use case says what a solution does for someone and what it needs, before anyone designs how it is built; a pattern, from the `pattern` skill beside this one, says how it is built.

The document's Participants and Interactions tables generate the draw.io diagram, its main flow generates an animated walkthrough, and its tagged sections generate HTML slides and a PDF. Both are checked back against the document.

## Requires

| Skill | Does | Comes from |
|---|---|---|
| [pattern](../pattern) | Its `publish.py` renders the view, animates the flows and builds the deck | This repository |
| [model](https://github.com/dermot-obrien/diagram-model) | Generates, syncs, validates and renders the diagram from the document's tables | diagram-model |
| [markdown-deck](https://github.com/dermot-obrien/markdown-deck) | Turns tagged sections into HTML slides and a PDF | markdown-deck |

`SKILL.md` declares all three in `metadata.x-skill-requires`. The skill checks for them and stops with an instruction rather than improvising.

## Install

```bash
gh skill install dermot-obrien/architecture-pattern use-case
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
```

## Use

Bind the workspace in `.agents/skill-bindings.toml`: `[suite.use-case] outputDir`, and the Participants and Interactions tables (the snippet is in `SKILL.md`). Copy `assets/template.md` into a new folder under `outputDir` as `index.md`, fill it in, then:

```bash
python <skills>/model/bin/model.py emit index.md --to drawio --out components.drawio
python <skills>/model/bin/model.py validate index.md
python <skills>/pattern/scripts/publish.py .
```

`examples/uc-900` is a worked example. The guide is [docs/use-cases.md](../../docs/use-cases.md).

## Licence

Content under CC BY 4.0 and code under Apache-2.0; see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
