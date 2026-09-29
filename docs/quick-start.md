<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Quick start

From an empty folder to two published patterns in about ten minutes: a small pattern with its diagram, animated scenario walkthrough, HTML deck and PDF, then a composite pattern whose scenario runs the first one.

You run the commands yourself here, so you can see what each tool does. Once it works, an agent does the same steps for you when you ask it for a pattern (step 11).

Commands are shown for PowerShell (Windows) and bash (macOS, Linux, and Git Bash on Windows). Where only one block is shown, it is the same in both. On macOS and Linux, type `python3` wherever this guide says `python` if `python` is not on your path.

## 1. Check the prerequisites

```
python --version
node --version
git --version
```

You need Python 3.11 or newer, Node 18 or newer and any recent git. draw.io desktop is optional: with it, the diagram is rendered for you; without it, you export one image by hand (step 7 says how).

## 2. Make a workspace and install the three skills

`pattern` does its work through two other skills, `model` (from the diagram-model repository) and `markdown-deck`. Install all three into `.agents/skills/`, the project folder most agents read. [Install](../README.md#install) lists the other folders and installers; this guide copies them with git so it works the same everywhere.

PowerShell:

```powershell
New-Item -ItemType Directory pattern-quickstart | Out-Null
Set-Location pattern-quickstart
git clone --depth 1 --branch pattern--v0.10.0 https://github.com/dermot-obrien/architecture-pattern.git _src/architecture-pattern
git clone --depth 1 --branch model--v0.8.0 https://github.com/dermot-obrien/diagram-model.git _src/diagram-model
git clone --depth 1 --branch markdown-deck--v0.6.4 https://github.com/dermot-obrien/markdown-deck.git _src/markdown-deck
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Copy-Item -Recurse _src/architecture-pattern/skills/pattern .agents/skills/
Copy-Item -Recurse _src/diagram-model/skills/model .agents/skills/
Copy-Item -Recurse _src/markdown-deck/skills/markdown-deck .agents/skills/
Remove-Item -Recurse -Force _src
```

bash:

```bash
mkdir pattern-quickstart && cd pattern-quickstart
git clone --depth 1 --branch pattern--v0.10.0 https://github.com/dermot-obrien/architecture-pattern.git _src/architecture-pattern
git clone --depth 1 --branch model--v0.8.0 https://github.com/dermot-obrien/diagram-model.git _src/diagram-model
git clone --depth 1 --branch markdown-deck--v0.6.4 https://github.com/dermot-obrien/markdown-deck.git _src/markdown-deck
mkdir -p .agents/skills
cp -r _src/architecture-pattern/skills/pattern _src/diagram-model/skills/model _src/markdown-deck/skills/markdown-deck .agents/skills/
rm -rf _src
```

git prints a "detached HEAD" note for each clone, and may warn that the tag "is not a commit". Both are expected when cloning a release tag.

Then install markdown-deck's Node dependencies, once:

```
npm install --prefix .agents/skills/markdown-deck --no-audit --no-fund
```

You should see `added 13 packages`, give or take. This installs Playwright for the PDF. It prints with Microsoft Edge or Google Chrome, so on Windows nothing more is needed; elsewhere, if neither browser is installed, run `npx playwright install chromium` from `.agents/skills/markdown-deck`.

## 3. Bind the skills to the workspace

The skills know nothing about your folders or your tables until a binding file tells them. Create the folder patterns will go in:

PowerShell:

```powershell
New-Item -ItemType Directory -Force patterns | Out-Null
```

bash:

```bash
mkdir -p patterns
```

Then create `.agents/skill-bindings.toml` in your editor with this content:

```toml
bindingsVersion = "1.0"

# How the pattern template's tables become a model. Paths are relative to this file.
[model]
node_id_attrs = ["component_id"]
edge_id_attr  = "iface_id"
local_pattern = '[0-9]{1,3}'

[[markdown.tables]]
section    = "Building Blocks"
entity     = "node"
id_pattern = 'COMP-[0-9]{3}'
columns    = { id = "Building Block", label = "Building Block", group = "Source" }

[[markdown.tables]]
section    = "Interfaces"
entity     = "edge"
id_pattern = 'IF-[0-9]{2,3}|COMP-[0-9]{3}'
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }

[markdown.scenarios]
section = "Scenarios"

# What the pattern skill needs from this workspace.
[suite.pattern]
outputDir = "../patterns"
```

`[model]` and the `markdown` tables tell the model skill which tables are boxes and which are lines. `local_pattern` lets a box without a catalogue entry take a plain number, `01 Web shop`. `[suite.pattern] outputDir` says where patterns live; it is relative to the binding file, which is in `.agents/`, hence `../patterns`. The [configuration reference](configuration.md) covers every key.

Run the skill's post-install check:

```
python .agents/skills/pattern/scripts/check.py
```

The last lines should read:

```
  result       : ok
patterns root: <your folder>\patterns [suite.pattern.outputDir]; approved statuses: Final, Approved, Active, Published
pattern: ok
```

A `warning:` line about draw.io desktop is fine if you do not have it.

## 4. Write a small pattern

Create `patterns/PAT-001-order-intake/index.md`. PowerShell: `New-Item -ItemType Directory -Force patterns/PAT-001-order-intake | Out-Null`; bash: `mkdir -p patterns/PAT-001-order-intake`. Then give it this content:

```markdown
---
title: "PAT-001 Order Intake"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# PAT-001 Order Intake

<!-- deck:cover subtitle="Take an order once, store it once" -->

<!-- deck:slide label="Intent" -->

## Intent

An order submitted twice must be stored once. The web shop retries on a timeout, so the order service accepts a client order key and stores each key at most once.

<!-- deck:slide label="Component view" -->

## Diagram

![PAT-001 components](./components.svg)

<!-- deck:slide label="Building blocks" -->

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Web shop | Takes the order from the customer | loose |
| 02 Order service | Checks the order key and stores the order | loose |
| 03 Order store | Holds each order once, keyed by its order key | loose |

<!-- deck:slide label="Interfaces" -->

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Order service | 01 Web shop | submit an order with its order key |
| IF-02 | 03 Order store | 02 Order service | insert the order if its key is new |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

Step through them in the [animated scenario walkthrough](./scenarios.html).

<!-- deck:html src="./scenarios.html" title="Scenario walkthrough" header="true" -->

### S1 Place an order

Start: 01 Web shop

Finish: 03 Order store

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Web shop | 02 Order service | submit the order with its order key | IF-01 |
| 2 | 02 Order service | 03 Order store | insert the order unless the key exists | IF-02 |

<!-- deck:slide label="Risks" -->

## Risks and Trade-offs

| Risk/Trade-off | Mitigation |
|---|---|
| A key reused for a different order is rejected | The web shop makes a new key per basket |
```

This is a trimmed copy of the full template, `.agents/skills/pattern/assets/template.md`, which has every section and the guidance for each. What matters here:

- The Building Blocks table is the boxes, the Interfaces table the lines, and each scenario's steps table a numbered flow over them.
- `model: diagram:` in the front matter declares the diagram, so every later command finds it.
- `Start:` and `Finish:` say where S1's flow enters and leaves, so another pattern can run it (step 9).
- The `deck:` comments choose what goes on slides. They are invisible when the Markdown is rendered.

## 5. Generate the diagram and check it

```
cd patterns/PAT-001-order-intake
python ../../.agents/skills/model/bin/model.py emit index.md --to drawio --out components.drawio
python ../../.agents/skills/model/bin/model.py validate index.md
cd ../..
```

You should see:

```
  3 nodes, 2 edges, 1 group, 1 scenario (2 steps) -> components.drawio
  index.md: 3 nodes, 2 edges, 1 group, 1 scenario (2 steps); abstraction conceptual
```

`emit` wrote a draw.io file with one shape per building block, one labelled connector per interface, and a layer for S1 with its numbered steps. `validate` confirmed the document and the diagram agree, and derived the abstraction: every box is a local role, so the pattern is conceptual.

## 6. Optionally, arrange the layout

`emit` lays the boxes out on a plain grid. Open `components.drawio` in draw.io, move the boxes, and save. From now on use `sync`, never `emit`, so your layout is kept:

```
python .agents/skills/model/bin/model.py sync patterns/PAT-001-order-intake/index.md patterns/PAT-001-order-intake/components.drawio
```

It prints `rebuild  scen  S1  2 step(s)`: scenario layers are always regenerated from the steps tables, while the boxes and connectors keep the places you gave them.

## 7. Publish it

```
python .agents/skills/pattern/scripts/publish.py patterns/PAT-001-order-intake
```

With draw.io desktop installed you should see, in five seconds or so:

```
  draw.io desktop found; render mode auto
  ok       index.md
           rendered components.svg
           animated scenarios.html
           built dist\PAT-001-order-intake\deck.html
           built dist\PAT-001-order-intake\deck.pdf
  1 model(s), theme 'default'
```

(`/` rather than `\` on macOS and Linux.) In `patterns/PAT-001-order-intake/` you now have:

| File | What it is |
|---|---|
| `components.svg` | The component view, rendered from the diagram's Structure layer |
| `components.svg.render.json` | What the view was rendered from, so a stale view is caught |
| `scenarios.html` | The animated walkthrough: arrow keys step, space plays. Opens from disk |
| `dist/PAT-001-order-intake/deck.html` | The HTML slides, one per tagged section plus the cover and the walkthrough |
| `dist/PAT-001-order-intake/deck.pdf` | The same slides as a PDF, one 16:9 page each |

Without draw.io desktop, publish stops with `failed` and says `components.svg is missing ... Export the 'Structure' layer(s) by hand`. Open `components.drawio` in draw.io (desktop or https://app.diagrams.net), hide every layer but Structure, export as SVG to `components.svg` beside it, then record it and publish again:

```
python .agents/skills/model/bin/model.py stamp patterns/PAT-001-order-intake/components.svg --diagram patterns/PAT-001-order-intake/components.drawio --layer Structure
python .agents/skills/pattern/scripts/publish.py patterns/PAT-001-order-intake
```

Open the walkthrough and the deck. PowerShell:

```powershell
Start-Process patterns/PAT-001-order-intake/scenarios.html
Start-Process patterns/PAT-001-order-intake/dist/PAT-001-order-intake/deck.html
```

bash (use `xdg-open` on Linux, `start` in Git Bash):

```bash
open patterns/PAT-001-order-intake/scenarios.html
open patterns/PAT-001-order-intake/dist/PAT-001-order-intake/deck.html
```

## 8. See validation catch a drift

Add a row to Building Blocks, `| 04 Audit log | Records every order | loose |`, and validate without syncing:

```
python .agents/skills/model/bin/model.py validate patterns/PAT-001-order-intake/index.md
```

```
  warn  04: 04 has no row in Catalogue Mapping; say what it realises, or that it is a gap  [mapping_missing]
  warn  04: 04 is in the document but not on the diagram  [doc_not_in_diagram]
```

The document says a box exists that the diagram does not show. Delete the row again. To keep it instead, add `| 04 | gap | gap |` to Catalogue Mapping and run `sync`, which draws the new box. This is the point of the method: the tables and the picture cannot quietly disagree.

## 9. Compose: a pattern that runs another

A composite pattern's scenario steps run other patterns' flows. Here, checkout runs PAT-001's S1 to take the order, and leaves the customer notification as an open participating pattern, not written yet.

Create `patterns/PAT-002-checkout/index.md` (make the folder as in step 4) with:

```markdown
---
title: "PAT-002 Checkout"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-002 Checkout

<!-- deck:cover subtitle="A composite pattern: checkout runs order intake" -->

<!-- deck:slide label="Context" -->

## Context

A customer checks out and is told the order is placed. Taking the order is already solved by PAT-001 Order Intake, so this pattern runs it rather than repeating it. Telling the customer is not solved yet.

<!-- deck:slide label="Component view" -->

## Diagram

![PAT-002 components](./components.svg)

<!-- deck:slide label="Patterns applied" -->

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-001 Order Intake | Stores the order once; run by S1 step 1 |
| TBD customer notification | Tells the customer; S1 step 3, not yet written |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Checkout page | Where the customer confirms the basket | loose |
| 02 Order records | Every placed order | PAT-001 |
| 03 Notifier | Sends the confirmation | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-10 | 02 Order records | 03 Notifier | an order was placed |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

Step through them in the [animated scenario walkthrough](./scenarios.html).

<!-- deck:html src="./scenarios.html" title="Scenario walkthrough" header="true" -->

### S1 Check out

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Checkout page | 02 Order records | place the order once | | PAT-001 S1 (01=01, 03=02) |
| 2 | 02 Order records | 03 Notifier | announce the order | IF-10 | |
| 3 | 03 Notifier | 01 Checkout page | confirm to the customer | | TBD customer notification |
```

Step 1's Uses cell, `PAT-001 S1 (01=01, 03=02)`, says: this step is the whole of PAT-001's S1. The role binding in brackets joins the two patterns' local boxes, PAT-001's box on the left and this pattern's on the right: PAT-001's `01 Web shop` is played here by `01 Checkout page`, and its `03 Order store` by `02 Order records`. So the flow enters at the step's Actor and leaves at its Target, matching PAT-001 S1's declared Start and Finish. Step 3's `TBD customer notification` is an open participating pattern.

Print the composition, then generate and check the diagram:

```
cd patterns/PAT-002-checkout
python ../../.agents/skills/model/bin/model.py composition index.md
python ../../.agents/skills/model/bin/model.py emit index.md --to drawio --out components.drawio
python ../../.agents/skills/model/bin/model.py validate index.md
cd ../..
```

`composition` warns about the open participating pattern, then prints the tree:

```
  warn  S1 step 3: open participating pattern TBD customer notification: write it as its own pattern, then replace TBD with its id and scenario key  [participant_open]
  PAT-002 Checkout [Draft]
    S1 step 1 runs S1 of PAT-001 Order Intake [Draft]  (joined at its declared start and finish)  (bound 01=01, 03=02)
    S1 step 3 runs TBD customer notification  (open participating pattern)
  composition: 2 participation step(s) running 1 participating pattern(s), depth 1, 1 open (TBD)
```

`validate` passes with one warning, for the open participating pattern:

```
  warn  S1 step 3: open participating pattern TBD customer notification: write it as its own pattern, then replace TBD with its id and scenario key  [participant_open]
  0 error(s), 1 warning(s)
```

Now publish both patterns together, so the walkthrough's drill-in from PAT-002 step 1 opens PAT-001's walkthrough:

```
python .agents/skills/pattern/scripts/publish.py patterns --recursive
```

Both report `ok`, and PAT-002's notes start with its composition. Its `components.svg` shows a dashed region labelled PAT-001 Order Intake round the two boxes that play PAT-001's part, and one labelled `Open: customer notification`. In its `scenarios.html`, step 1 carries a boxed-plus badge: click it, or press D, to open PAT-001's walkthrough at S1.

## 10. See the approval gate

An approved pattern cannot rest on an unapproved or unwritten one. Change PAT-002's front matter to `status: Approved` and validate:

```
python .agents/skills/model/bin/model.py validate patterns/PAT-002-checkout/index.md
```

```
  error  S1 step 1: PAT-002 is Approved but rests on the participating pattern PAT-001, which is Draft; approved statuses are Final, Approved, Active, Published  [participant_unapproved]
  error  S1 step 3: PAT-002 is Approved but rests on the open participating pattern TBD customer notification  [participant_unapproved]
```

It exits 1, and `publish.py` would skip PAT-002 until it is fixed. Set the status back to `Draft`.

## 11. Let your agent do it

Everything above is what the `pattern` skill tells an agent to do. Open the workspace in VS Code with GitHub Copilot, Cursor, Claude Code, Codex, Gemini CLI or any agent that reads `.agents/skills/`, and ask, for example:

> Create a pattern for sending the order confirmation email, as PAT-003, and replace the TBD in PAT-002 with it. Publish both.

The agent runs `doctor` first, copies the template into `patterns/PAT-003-<slug>/index.md`, fills it, generates and validates the diagram, updates PAT-002's Uses cell, and publishes. In some agents you can also type `/pattern`.

## Where next

- [Concepts](concepts.md): what a pattern is, and the ideas behind the tables, the diagram and the deck.
- [Everyday workflow](workflow.md): arranging diagrams, promoting a local box to a catalogue id, working without draw.io, CI and site builds.
- [Composing patterns](composing.md): the Uses column, Start and Finish, role bindings and the approval gate in full.
- [Configuration](configuration.md) and [commands](commands.md): every key and every flag.
- [Troubleshooting](troubleshooting.md): what each error means and how to fix it.
