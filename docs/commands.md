<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Command reference

Every script in this repository, and the `model` and `markdown-deck` commands a pattern uses, with every flag as its `--help` prints it.

`<skills>` is the folder the skills are installed in, such as `.agents/skills`. Paths below assume you run from the workspace root. On macOS and Linux, use `python3` if `python` is not on your path.

## The pattern skill's scripts

### publish.py

Publish every model in a folder: render its views, animate its scenarios, build its deck and PDF.

```
python <skills>/pattern/scripts/publish.py <folder> [--recursive] [--no-pdf] [--force] [--dry-run]
       [--thumbnails] [--scenario-images] [--no-animate] [--render auto|always|never]
       [--no-regions] [--no-deck] [--json]
```

A model is a document that declares its diagram in front matter (`model: diagram: components.drawio`); a document without one is not published. For each model, `publish.py` runs `model scan` to validate it, prints the composition of a composite pattern, notes endpoints that carry an id without a name, then writes beside the document:

| Output | When |
|---|---|
| `<stem>.svg`, with `<stem>.svg.render.json` | Always: the Structure layer, plus the Participating patterns layer when the diagram has one |
| `scenarios.html` (`<stem>-scenarios.html` beside a document not named `index.md`) | When the model has scenarios, built before the deck so a `deck:html` slide embeds a current one |
| `<stem>-s1.svg`, `<stem>-s2.svg`, ... | Only with `--scenario-images` |
| `dist/<name>/deck.html` and `deck.pdf` | When the document has deck tags. `<name>` is the file stem, or the folder name for `index.md` |

| Option | Effect |
|---|---|
| `folder` | The folder holding the documents to publish |
| `--recursive` | Also publish the documents in every folder below it |
| `--no-pdf` | Build the HTML deck only |
| `--force` | Publish models that fail validation. Otherwise they are skipped and their errors listed |
| `--dry-run` | Say what would be done, and do nothing |
| `--thumbnails` | The deck's slide index shows thumbnails; the default is titles only |
| `--scenario-images` | Also render one static image per scenario. The walkthrough replaces them; use this for a medium that cannot run it |
| `--no-animate` | Do not build the walkthrough |
| `--render auto` | The default. Render a view only when it is missing or older than its diagram and draw.io desktop is installed; otherwise require it to be current |
| `--render never` | Never call draw.io. Every view must be committed and stamped, or the model fails naming each view to export. For a build machine without draw.io |
| `--render always` | Re-render every view. Needs draw.io desktop |
| `--no-regions` | Render the structure without the Participating patterns layer |
| `--no-deck` | Render the views and the walkthrough only. For a site build that builds its own decks: run it with `--recursive` first, so no deck embeds a missing or stale view |
| `--json` | Print the results as JSON instead of the report: `folder`, `theme`, `results` (each `doc`, `status` of `ok`, `failed` or `skipped`, `notes`, and `composition` for a composite pattern) and `undeclared` (documents with no declared diagram) |

The theme is the document's `deck_theme` if it sets one, else `[suite.pattern] deckTheme`, else whatever markdown-deck chooses; see [configuration](configuration.md#decktheme).

Exit codes: 0 all published; 1 a model failed or was skipped; 2 usage, or `model scan` failed; 3 `model`, `markdown-deck` or `node` missing.

### check.py

The post-install check. Run from the workspace root; it takes no arguments.

```
python <skills>/pattern/scripts/check.py
```

It confirms `model` and `markdown-deck` are installed where an agent would find them, runs `model doctor --skill pattern` on the workspace's bindings, prints the patterns root and approved statuses composing will use, and fails if the installed `model` is older than 0.8.0. A missing draw.io desktop is a warning. `SKILL_DIR` names the installed skill; it defaults to the folder above the script.

Exit codes: 0 correct (warnings may be printed); 1 problems, one line each; 2 usage or environment error, including Python older than 3.11. `--help` prints its description.

### name-endpoints.py

Fill in the names of bare identifiers in the Interfaces table's Provider and Consumer columns and each scenario's Actor and Target columns, from the Building Blocks table.

```
python <skills>/pattern/scripts/name-endpoints.py <file-or-folder>... [--check]
```

| Option | Effect |
|---|---|
| `paths` | Markdown files, or folders searched recursively (skipping hidden folders, `node_modules` and `dist`) |
| `--check` | Change nothing; exit 1 if any cell would change |

A cell `02` becomes `02 Order service`. A cell that already has a name, or whose id has no Building Blocks row, is left alone; the second is reported on stderr. Line endings are preserved. `publish.py` runs it with `--check` and adds a note when a document needs it.

## model commands a pattern uses

The `model` skill's CLI, `python <skills>/model/bin/model.py <command>`. Every command that reads a document takes `--config <file>` to name the binding file instead of searching upward for it. Exit codes: 0 success; 1 validation found something at or above the fail threshold; 2 usage error or unreadable input; 3 an external tool (draw.io, PyYAML) missing or failed. [diagram-model](https://github.com/dermot-obrien/diagram-model) documents them in full.

| Command | What it does | Options |
|---|---|---|
| `doctor` | Check how the skills are bound to the repository | `--skill pattern` checks `[suite.pattern]` against the pattern contract; `--near <dir>` resolves the binding file from there; `--doc <file>` also shows what each box's link rules resolve to; `--json` |
| `emit <doc> --to drawio --out components.drawio` | Write the diagram from the tables, once | `--to drawio\|markdown\|json\|yaml\|csv`; `--force` overwrites an existing diagram, discarding its layout |
| `sync <doc> <drawio>` | Reconcile the diagram with the document, keeping the layout | `--prune` deletes shapes with no row instead of marking them; `--dry-run`; `--adopt` tags unidentified shapes whose label matches a row, for a hand-drawn diagram; `--json` |
| `validate <doc>` | Check the model, and the document against its declared diagram | `--against <file>` compares with another representation; `--fail-on error\|warn\|never` (default `error`); `--json` |
| `composition <doc>` | Print the patterns a composite pattern's scenarios run | `--json` |
| `render <drawio> --out <file>` | Export layers with draw.io desktop, and write the render record | `--layer <name>` (repeatable; omit for all); `--format svg\|png\|pdf\|jpg`; `--scale`; `--width`; `--transparent`; `--no-regions`; `--theme light\|dark\|auto` (default `light`); `--drawio-bin <path>`; `--timeout <s>` (default 120) |
| `stamp <image>` | Record a hand-exported view against its diagram | `--diagram <drawio>`; `--layer <name>` (repeatable); `--check` exits 0 only if the record matches the diagram |
| `animate <doc>` | Write the walkthrough, `scenarios.html` | `--diagram`; `--out`; `--image <svg-or-png>` to use a given view; `--render auto\|always\|never`; `--accent #RRGGBB`; `--interval <s>`; `--force` animates despite validation errors; `--drawio-bin` |
| `scan <folder>` | Find and validate every document that declares a diagram | `--recursive`; `--json`; `--fail-on error\|warn\|never` |
| `rename <doc> <old> <new>` | Change an identifier in the document and its diagram, such as promoting local `02` to `COMP-002` | `--drawio <file>`; `--dry-run` |
| `extract <input>` | Read a model from `.md`, `.drawio`, `.json` or `.yaml` | `--format json\|yaml\|csv`; `--out <file>` |
| `layers <drawio>` | List the layers with their indexes | `--json` |
| `drawio` | Say where draw.io desktop is; exit 1 if it is not installed | `--drawio-bin <path>` |

## markdown-deck commands

`publish.py` runs `build` for you. To build one deck by hand:

```
node <skills>/markdown-deck/bin/markdown-deck.mjs build index.md --out dist --theme default --pdf
```

Its other commands are `pdf <deck.html>`, `publish [<root>]` for every document marked `deck_publish: true`, and `themes`. `build` takes `--title`, `--subtitle`, `--date`, `--footnote`, `--eyebrow`, `--logo`, `--mermaid`, `--partials`, `--table-rows`, `--thumbnails`, `--comments`, `--feedback-to`, `--feedback-subject`, `--deck-id`, `--html-name`, `--refresh` and `--pdf`/`--no-pdf`. `node <skills>/markdown-deck/bin/markdown-deck.mjs --help` prints them all (and exits 1); the [markdown-deck README](https://github.com/dermot-obrien/markdown-deck) explains each.

## The worked example's run.sh

`skills/pattern/examples/knowledge-retrieval/run.sh` regenerates every output of that example: extract, sync (emit first if there is no diagram), validate, render the structure and one image per scenario, build the deck and print its PDF. Run it from that folder, in bash:

```bash
cd skills/pattern/examples/knowledge-retrieval
MODEL=<skills>/model/bin/model.py MARKDOWN_DECK=<skills>/markdown-deck/bin/markdown-deck.mjs ./run.sh
```

`MODEL` and `MARKDOWN_DECK` default to the two skills installed beside `pattern`. It needs draw.io desktop.

## Repository checks

For contributors, from the repository root.

| Command | What it checks |
|---|---|
| `node scripts/validate-skills.mjs [skillsRoot]` | Each `<root>/<name>/SKILL.md` against the Agent Skills specification: front matter fields and lengths, `name` equal to the folder, relative links resolve, body length. Default root `./skills`. It takes no flags; an argument is read as the root |
| `node scripts/validate-bundle.mjs [bundleDir ...]` | `bundle.json` against its schema and the skills: every skill listed, versions and requirements equal to `SKILL.md`, purls, check commands, and the marketplace adapter at the same versions. Default `.` |
| `node scripts/validate-bundle.mjs --instance <file.json> --schema <$id\|file>[#pointer]` | One JSON document against a schema |
| `node scripts/validate-bundle.mjs --run-checks <workspace> [--skills <dir>] [bundleDir]` | Run each skill's post-install check as an installer would, from `<workspace>`, with `SKILL_DIR` set to `<skills dir>/<name>` |
| `--schemas <dir>` | On any form of `validate-bundle.mjs`, load more schemas by `$id`; repeatable |
| `skills-ref validate skills/pattern` | The specification's reference validator. Install it as the [README](../README.md#agent-skills-conformance) shows; on Windows set `PYTHONUTF8=1` first |

### Running what CI runs, locally

CI's `example` job clones diagram-model and markdown-deck, points `AGENT_SKILLS_PATH` at them, and checks the two examples. To do the same, with both repositories cloned beside this one and `npm install` run in `markdown-deck/skills/markdown-deck`:

bash:

```bash
export AGENT_SKILLS_PATH="$PWD/skills:$PWD/../diagram-model/skills:$PWD/../markdown-deck/skills"
MODEL=../diagram-model/skills/model/bin/model.py
python "$MODEL" doctor --skill pattern --json
cd skills/pattern/examples/knowledge-retrieval
python "../../../../$MODEL" validate index.md --against components.drawio
for v in components scenario-s1 scenario-s2; do python "../../../../$MODEL" stamp --check "$v.svg"; done
cd ../composite
python "../../../../$MODEL" composition PAT-910-staff-assistant/index.md
python "../../../../$MODEL" validate PAT-910-staff-assistant/index.md
```

PowerShell:

```powershell
$env:AGENT_SKILLS_PATH = "$PWD\skills;$PWD\..\diagram-model\skills;$PWD\..\markdown-deck\skills"
$MODEL = (Resolve-Path ..\diagram-model\skills\model\bin\model.py).Path
python $MODEL doctor --skill pattern --json
Push-Location skills/pattern/examples/knowledge-retrieval
python $MODEL validate index.md --against components.drawio
foreach ($v in "components", "scenario-s1", "scenario-s2") { python $MODEL stamp --check "$v.svg" }
Set-Location ../composite
python $MODEL composition PAT-910-staff-assistant/index.md
python $MODEL validate PAT-910-staff-assistant/index.md
Pop-Location
```

`doctor` reports an error, because this repository binds no `outputDir`; CI ignores that and checks only that `siblings` lists `model` and `markdown-deck`. Everything after it should pass, with one `participant_open` warning for PAT-910's open participating pattern. [.github/workflows/ci.yml](../.github/workflows/ci.yml) has the rest: the model extract comparison, the sync round trip, the deck build and the approval-gate check.
