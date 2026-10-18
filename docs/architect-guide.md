<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Architect's guide: edit, check and publish architecture patterns and reference architectures

This page is for architects who want to change an architecture pattern or a reference architecture, check it, and publish its pages and slides on their own machine. You don't need to know how the tools work inside. Everything you need is on this page.

There are two kinds of document:

| Kind | Identifier | What its boxes are |
|---|---|---|
| Architecture pattern | `AP-001`, `AP-002`, ... | Technology-agnostic: architecture building blocks (ABBs) and local roles such as `01 Gateway` |
| Reference architecture | `RA-001`, `RA-002`, ... | Technology-specific: mainly solution building blocks (SBBs) and products. It names the architecture pattern it makes concrete |

Each one is a folder named after its identifier, such as `AP-007-order-intake/`. The folder holds one Markdown document, `index.md`, which is the source of everything else:

| File | What it is | Who changes it |
|---|---|---|
| `index.md` | The document. Its tables are the model: Building Blocks are the boxes, Interfaces are the lines, and each scenario's steps table is a numbered flow | You |
| `components.drawio` | The diagram, generated from the tables. You can move boxes around in draw.io | You, for the layout only |
| `components.svg` | The picture of the diagram shown on the page and the slides | Generated |
| `scenarios.html` | An animated walkthrough of the scenarios | Generated |
| `dist/<folder>/deck.html` and `deck.pdf` | The slides and their PDF | Generated |

The commands work the same in PowerShell (Windows) and bash (macOS, Linux, Git Bash). Where they differ, both are shown. Run every command from the root of your repository. On macOS and Linux, use `python3` if `python` is not found.

## 1. Check what you have installed

```
python --version
node --version
git --version
```

You need Python 3.11 or newer, Node 18 or newer, and git. draw.io desktop (https://www.drawio.com) is optional but recommended. With it, the picture of the diagram is drawn for you. Without it, you export one image by hand (step 9 says how).

## 2. Say where to get the tools from

Three tools do the work. They are called skills, and each one comes from its own git repository:

| Skill | What it does |
|---|---|
| `pattern` | Publishes a document: the picture, the walkthrough and the slides |
| `model` | Reads the tables, generates the diagram and checks the diagram and document agree |
| `markdown-deck` | Turns the document into slides and a PDF |

Set where each one comes from. The values below are the public repositories at their latest version. If your organisation keeps its own copies, or you want a fixed release, change the URL or the ref here and nowhere else. A ref is a branch name such as `main` or a release tag such as `markdown-deck--v0.6.8`.

PowerShell:

```powershell
$PatternRepo = "https://github.com/dermot-obrien/architecture-pattern.git"; $PatternRef = "main"
$ModelRepo   = "https://github.com/dermot-obrien/diagram-model.git";        $ModelRef   = "main"
$DeckRepo    = "https://github.com/dermot-obrien/markdown-deck.git";        $DeckRef    = "main"
```

bash:

```bash
PATTERN_REPO=https://github.com/dermot-obrien/architecture-pattern.git; PATTERN_REF=main
MODEL_REPO=https://github.com/dermot-obrien/diagram-model.git;          MODEL_REF=main
DECK_REPO=https://github.com/dermot-obrien/markdown-deck.git;           DECK_REF=main
```

These variables last only as long as the terminal window. Steps 3 and 13 use them, so set them again in a new window.

## 3. Install the three skills

This copies the three skills into `.agents/skills/` in your repository, then installs the slide tool's packages. If your repository already has these three folders under `.agents/skills/`, skip to step 4.

PowerShell:

```powershell
git clone --quiet --depth 1 --branch $PatternRef $PatternRepo _skills/architecture-pattern
git clone --quiet --depth 1 --branch $ModelRef   $ModelRepo   _skills/diagram-model
git clone --quiet --depth 1 --branch $DeckRef    $DeckRepo    _skills/markdown-deck
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Copy-Item -Recurse -Force _skills/architecture-pattern/skills/pattern .agents/skills/
Copy-Item -Recurse -Force _skills/diagram-model/skills/model          .agents/skills/
Copy-Item -Recurse -Force _skills/markdown-deck/skills/markdown-deck  .agents/skills/
Remove-Item -Recurse -Force _skills
npm install --prefix .agents/skills/markdown-deck --no-audit --no-fund
```

bash:

```bash
git clone --quiet --depth 1 --branch "$PATTERN_REF" "$PATTERN_REPO" _skills/architecture-pattern
git clone --quiet --depth 1 --branch "$MODEL_REF"   "$MODEL_REPO"   _skills/diagram-model
git clone --quiet --depth 1 --branch "$DECK_REF"    "$DECK_REPO"    _skills/markdown-deck
mkdir -p .agents/skills
cp -r _skills/architecture-pattern/skills/pattern _skills/diagram-model/skills/model _skills/markdown-deck/skills/markdown-deck .agents/skills/
rm -rf _skills
npm install --prefix .agents/skills/markdown-deck --no-audit --no-fund
```

A tag may print a "detached HEAD" note, which is fine. The last command prints `added ... packages`. It installs the PDF printer, which uses Microsoft Edge or Google Chrome. If you have neither, run `npx playwright install chromium` inside `.agents/skills/markdown-deck`.

Add `.agents/skills/` to your `.gitignore`. The skills are installed, not authored, so they don't belong in your repository's history.

## 4. Tell the skills about your repository

The skills read one settings file, `.agents/skill-bindings.toml`. It says which tables are boxes and lines, where patterns live, and the two kinds of document. If your repository already has this file, leave it alone and skip to step 5.

Otherwise create `.agents/skill-bindings.toml` with this content. The paths in it are relative to the `.agents` folder.

```toml
bindingsVersion = "1.0"

# Which tables are boxes and which are lines.
[model]
node_id_attrs = ["abb_id", "sbb_id"]
edge_id_attr  = "iface_id"
local_pattern = '[0-9]{1,3}'

[[markdown.tables]]
section    = "Building Blocks"
entity     = "node"
id_pattern = 'ABB-[0-9]{3}|SBB-[0-9]{3}'
columns    = { id = "Building Block", label = "Building Block", group = "Source" }

[[markdown.tables]]
section    = "Interfaces"
entity     = "edge"
id_pattern = 'IF-[0-9]{2,3}'
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }

[markdown.scenarios]
section = "Scenarios"

# Where patterns live, and the two kinds of document.
[suite.pattern]
outputDir = "../patterns"

[suite.pattern.types.architecture-pattern]
label    = "Architecture pattern"
idSeries = "AP"
physical = "none"

[suite.pattern.types.reference-architecture]
label    = "Reference architecture"
idSeries = "RA"
physical = "most"
```

Then make the folder patterns go in:

PowerShell:

```powershell
New-Item -ItemType Directory -Force patterns | Out-Null
```

bash:

```bash
mkdir -p patterns
```

## 5. Check the installation

```
python .agents/skills/pattern/scripts/check.py
```

The last line should be `pattern: ok`. A warning that draw.io desktop was not found is fine. If it says a skill is missing, repeat step 3.

## 6. Start a new pattern or reference architecture

Skip this step to edit one that already exists.

First get the next free identifier. Use `architecture-pattern` or `reference-architecture`:

```
python .agents/skills/pattern/scripts/register.py next --type architecture-pattern
```

It prints an identifier such as `AP-001`. Make a folder named after it plus a few words, copy in the blank document for that kind, and open it:

PowerShell:

```powershell
$Id = "AP-001-order-intake"
New-Item -ItemType Directory -Force patterns/$Id | Out-Null
Copy-Item (python .agents/skills/pattern/scripts/template.py which --type architecture-pattern) patterns/$Id/index.md
```

bash:

```bash
ID=AP-001-order-intake
mkdir -p patterns/$ID
cp "$(python .agents/skills/pattern/scripts/template.py which --type architecture-pattern)" patterns/$ID/index.md
```

Change the H1 and `title` to the identifier and the name, such as `AP-001 Order Intake`. For a reference architecture, set `implements:` in the front matter to the architecture patterns it makes concrete, such as `implements: [AP-001]`. Delete the guidance comments as you fill each section in. The front matter's `model: diagram: components.drawio` line tells the tools where the diagram is. Keep it.

The blank document's example rows, such as `ABB-NNN Official Name`, fail the check until you replace them with real rows. The check also says `components.drawio: not found` until you generate the diagram the first time (step 8).

## 7. Edit the document

Open `index.md` in any editor and change the text and the tables. The tables are the model:

| Table | What a row is |
|---|---|
| Building Blocks | One box. Its first column is a catalogue identifier, `ABB-024 Agent Registry` (`SBB-...` in a reference architecture), or a local role with a number, `01 Web shop` |
| Interfaces | One line between two boxes: `IF-01`, its Provider, its Consumer and what it carries |
| Catalogue Mapping | For each local role, what it maps to in the catalogue, or `gap` |
| Each scenario's steps (under `### S1 ...`) | One numbered step of the flow: Actor, Target, Action, and the Interface it uses |

Comments such as `<!-- deck:slide label="Interfaces" -->` choose which sections become slides. They don't show on the page. Put one directly before a heading to make that section a slide, and remove it to drop the slide.

After every change, check the document against itself:

```
python .agents/skills/model/bin/model.py validate patterns/AP-001-order-intake/index.md
```

It prints a summary such as `7 nodes, 9 edges, 3 scenarios (13 steps); abstraction logical`, then any problems. `error` lines must be fixed. `warn` lines are advice, such as a local role with no Catalogue Mapping row.

## 8. Generate and edit the diagram

**The first time only**, when the folder has no `components.drawio` yet, generate it from the tables:

```
python .agents/skills/model/bin/model.py emit patterns/AP-001-order-intake/index.md --to drawio --out patterns/AP-001-order-intake/components.drawio
```

Open `components.drawio` in draw.io (desktop, or https://app.diagrams.net) and arrange it. Moving boxes, resizing them, routing lines and changing colours are all safe. Don't add or delete boxes or lines in draw.io. Add or remove the table row in `index.md` instead, then sync.

**After every change to the tables**, bring the diagram up to date. Sync keeps your layout, adds new boxes and lines, and redraws the scenario layers from the steps tables:

```
python .agents/skills/model/bin/model.py sync patterns/AP-001-order-intake/index.md patterns/AP-001-order-intake/components.drawio
```

Never run `emit` again on a diagram you have arranged: it starts again from a plain grid.

Then run the same check as in step 7. Once the diagram exists, it also checks that the document and the diagram agree:

```
python .agents/skills/model/bin/model.py validate patterns/AP-001-order-intake/index.md
```

A line such as `04 is in the document but not on the diagram` means you need to sync.

## 9. Publish locally: the page, the walkthrough, the slides and the PDF

One command publishes a folder:

```
python .agents/skills/pattern/scripts/publish.py patterns/AP-001-order-intake
```

Or publish every pattern and reference architecture at once:

```
python .agents/skills/pattern/scripts/publish.py patterns --recursive
```

For each document it prints `ok` and what it wrote: `components.svg`, `scenarios.html`, `dist/<folder>/deck.html` and `dist/<folder>/deck.pdf`. A document that fails its check is skipped, with the reason. Fix it and publish again.

**Without draw.io desktop**, publish stops with `components.svg is missing` or `stale`. Draw the picture by hand: open `components.drawio`, hide every layer except `Structure`, export as SVG to `components.svg` in the same folder, record it, then publish again:

```
python .agents/skills/model/bin/model.py stamp patterns/AP-001-order-intake/components.svg --diagram patterns/AP-001-order-intake/components.drawio --layer Structure
python .agents/skills/pattern/scripts/publish.py patterns/AP-001-order-intake
```

To publish only the picture and walkthrough, without slides, add `--no-deck`. To skip the PDF, add `--no-pdf`.

## 10. Look at the result

PowerShell:

```powershell
Start-Process patterns/AP-001-order-intake/scenarios.html
Start-Process patterns/AP-001-order-intake/dist/AP-001-order-intake/deck.html
Start-Process patterns/AP-001-order-intake/dist/AP-001-order-intake/deck.pdf
```

bash (`xdg-open` on Linux, `start` in Git Bash):

```bash
open patterns/AP-001-order-intake/scenarios.html
open patterns/AP-001-order-intake/dist/AP-001-order-intake/deck.html
```

In the slides, the arrow keys move between slides, `I` shows or hides the slide list, and `F` presents full screen. In the walkthrough, the arrow keys step through a scenario and space plays it.

`dist/` folders are output. Add `dist/` to your `.gitignore` unless your team commits slides on purpose.

## 11. The everyday loop

1. Edit `index.md`.
2. Run `validate` (step 7).
3. If you changed a table, run `sync` (step 8) and adjust the layout in draw.io if needed.
4. Run `publish.py` (step 9) and look at the result (step 10).
5. Commit `index.md`, `components.drawio`, `components.svg` and `components.svg.render.json`. Don't commit `scenarios.html` or `dist/`, because they are rebuilt every time.

## 12. When something goes wrong

| Message | What to do |
|---|---|
| `X is in the document but not on the diagram`, or the other way round | Run `sync` (step 8) |
| `components.drawio: not found` | Generate the diagram the first time with `emit` (step 8) |
| `'ABB-NNN Official Name' ... matches no identifier rule` | An example row from the blank document is still there. Replace it with a real row, or delete it |
| `X has no row in Catalogue Mapping` | Add a row for the local role: what it maps to, or `gap` |
| `components.svg is missing` or `stale` | Install draw.io desktop, or export the picture by hand and `stamp` it (step 9) |
| `AP-002 is Approved but rests on ... which is Draft` | An approved document can only use approved documents. Approve the one it uses first, or set this one back to `Draft` |
| `... is a Reference architecture, which has mainly physical boxes ...`, or an SBB in an architecture pattern | The document's boxes don't fit its kind. Use ABBs and local roles in an `AP`, and SBBs or products in an `RA`, or change its `pattern_type` |
| `RA-001 implements AP-002, but there is no document for AP-002` | Correct `implements:` in the front matter, or write that architecture pattern first |
| `No module named ...`, or `node` errors from the slides | Re-run the `npm install` line in step 3 |
| `python` not found | Use `python3`, or install Python 3.11 or newer |

## 13. Update the skills

Set the sources again (step 2), delete the three folders, and install again (step 3):

PowerShell:

```powershell
Remove-Item -Recurse -Force .agents/skills/pattern, .agents/skills/model, .agents/skills/markdown-deck
```

bash:

```bash
rm -rf .agents/skills/pattern .agents/skills/model .agents/skills/markdown-deck
```

Your documents, diagrams and `.agents/skill-bindings.toml` are not touched.
