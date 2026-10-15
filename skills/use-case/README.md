<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# use-case

An agent skill for authoring a use case as one Markdown document that is also the model and also the deck. A use case says what a solution does for someone and what it needs, before anyone designs how it is built; a pattern, from the `pattern` skill beside this one, says how it is built.

The document's Participants and Interactions tables generate the draw.io diagram, its scenarios generate an animated walkthrough, and its tagged sections generate HTML slides and a PDF. Both are checked back against the document.

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

## Quick start

From an empty workspace with the skill installed:

```bash
# 1. Verify installation
python .agents/skills/use-case/scripts/check.py

# 2. Create a local use case
mkdir -p epics/EP-12/use-cases/EP-12-UC1-order-placement
cp .agents/skills/use-case/assets/template.md epics/EP-12/use-cases/EP-12-UC1-order-placement/index.md

# 3. Fill in the document, then generate the diagram
python .agents/skills/model/bin/model.py emit epics/EP-12/use-cases/EP-12-UC1-order-placement/index.md --to drawio --out components.drawio

# 4. Validate
python .agents/skills/model/bin/model.py validate epics/EP-12/use-cases/EP-12-UC1-order-placement/index.md

# 5. Publish
python .agents/skills/pattern/scripts/publish.py epics/EP-12/use-cases/EP-12-UC1-order-placement
```

See [docs/use-cases.md](../../docs/use-cases.md) for local vs endorsed use cases and the endorsement workflow.

## Use

Bind the workspace in `.agents/skill-bindings.toml`: the Participants and Interactions tables (the snippet is in `SKILL.md`), and `[suite.use-case] outputDir` if endorsed use cases should not go in the default `use-cases/` at the repository root. Copy `assets/template.md` into a new folder under that folder as `index.md`, fill it in, then:

```bash
python <skills>/model/bin/model.py emit index.md --to drawio --out components.drawio
python <skills>/model/bin/model.py validate index.md
python <skills>/pattern/scripts/publish.py .
```

`examples/uc-900` is a worked example. The guide is [docs/use-cases.md](../../docs/use-cases.md).

## Updating

To update after a new release:

### Automated Update (Recommended)

Use the update script from the repository root (automatically updates all dependencies):

**bash:**
```bash
./scripts/update-skills.sh             # Update workspace skills
./scripts/update-skills.sh --user      # Update user-level skills
```

**PowerShell:**
```powershell
.\scripts\update-skills.ps1            # Update workspace skills
.\scripts\update-skills.ps1 -User      # Update user-level skills
```

The script automatically updates `use-case`, `pattern`, `model`, and `markdown-deck` together with coordinated versions.

### Manual Update

1. **Delete old installations:**
   ```bash
   rm -rf .agents/skills/use-case .agents/skills/pattern .agents/skills/model .agents/skills/markdown-deck
   ```

2. **Reinstall all dependencies** (use-case needs pattern, which needs model and markdown-deck):
   ```bash
   gh skill install dermot-obrien/architecture-pattern use-case
   gh skill install dermot-obrien/architecture-pattern pattern
   gh skill install dermot-obrien/diagram-model model
   gh skill install dermot-obrien/markdown-deck markdown-deck
   npm install --prefix .agents/skills/markdown-deck
   ```

3. **Verify:**
   ```bash
   python .agents/skills/use-case/scripts/check.py
   python .agents/skills/model/bin/model.py doctor --skill use-case
   ```

**Important:** Always update `use-case`, `pattern`, `model`, and `markdown-deck` together - they have coordinated versions.

## Licence

Content under CC BY 4.0 and code under Apache-2.0; see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
