<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Troubleshooting

Find the message you see, then the fix. Messages are quoted as the tools print them; `<path>` and the like stand for your values. Validation findings end with their rule id in square brackets, such as `[doc_not_in_diagram]`, and every rule's severity can be changed in the binding's `[rules]`.

Start with the post-install check, which catches most setup problems at once:

```
python <skills>/pattern/scripts/check.py
```

## Installation

### `the model skill is not installed in any skills directory an agent reads, nor on AGENT_SKILLS_PATH`

From `check.py`; `publish.py` says `! the model skill is not installed beside this one, on AGENT_SKILLS_PATH or in any agent skills directory (<path>)` and exits 3. The same for `markdown-deck`.

Install the missing skill ([Install](../README.md#install)). They need not be in the same folder: `pattern` looks beside itself, then in each folder on `AGENT_SKILLS_PATH`, then in every project and user skills folder of VS Code with GitHub Copilot, Cursor, Claude Code, Codex and Gemini CLI, then among Claude Code plugins. If yours is somewhere else, add its parent folder to `AGENT_SKILLS_PATH` (`;`-separated on Windows, `:` elsewhere).

### `the model skill installed is older than 0.8.0, so composite patterns (the Uses column) cannot be checked`

Update `model` from https://github.com/dermot-obrien/diagram-model to 0.8.0 or later; `pattern` 0.10 requires `^0.8.0`.

### `Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'gray-matter'`

`npm install` has not been run where `markdown-deck` is installed. `publish.py` shows it as `deck failed: ...`. Run, from the workspace root:

```
npm install --prefix <skills>/markdown-deck --no-audit --no-fund
```

### `! node is not on PATH; markdown-deck needs it`

From `publish.py`, exit 3. Install Node 18 or newer and open a new terminal.

### `Python <version> is too old: pattern needs 3.11 or newer.`

From `check.py`, exit 2. Also `! reading a config file needs Python 3.11 or newer (tomllib)` from `model`. Install Python 3.11 or newer; on macOS and Linux run `python3`.

### `pdf missing: ...`

The HTML deck built and the PDF did not. The PDF export drives Microsoft Edge, then Google Chrome, then Playwright's own Chromium. On Windows, Edge is always there. Elsewhere, install Chrome, or run `npx playwright install chromium` in `<skills>/markdown-deck`; `MARKDOWN_DECK_BROWSER` or `MARKDOWN_DECK_CHANNEL` picks a browser. If a proxy blocked the Playwright install, everything but the PDF still works: publish with `--no-pdf`.

### `warning: draw.io desktop was not found, so views are exported by hand and stamped with model stamp`

From `check.py`. Not an error. Install draw.io desktop (the installed build, not the portable one) to have views rendered for you, or export by hand as below. `model drawio` says where it looked; `--drawio-bin <path>` on `render` and `animate` names it explicitly.

## Bindings

### `error  suite.pattern: 'outputDir' is required and not set.`

`doctor --skill pattern` found no `outputDir` in `[suite.pattern]`, often because there is no binding file at all (`warn  bindings: no binding file found; built-in defaults are in use.`). Create `.agents/skill-bindings.toml` at the workspace root with at least:

```toml
bindingsVersion = "1.0"

[suite.pattern]
outputDir = "../patterns"
```

The [configuration reference](configuration.md#a-complete-binding-for-the-shipped-template) has a complete file for the shipped template.

### `error  suite.pattern: 'outputDir' points at <path>, which does not exist`

Paths are relative to the binding file, not to where you ran the command. From `.agents/skill-bindings.toml`, a `patterns/` folder at the root is `../patterns`. Create the folder, or fix the path. The same message names `template` or `ontologySchema` when those are wrong, and `the patterns root <path> does not exist` names `patternsRoot`.

### `'<key>' is not a binding this skill declares`

A warning: a key in `[suite.pattern]` the skill does not know, usually a typo. The keys are `outputDir`, `template`, `idSeries`, `deckTheme`, `ontologySchema`, `ontologySchemaSha256`, `patternsRoot` and `approvedStatuses`, in that camel case.

### `'<name>' is an absolute path. It will not survive a clone on another machine`

Make it relative to the binding file.

### `'ontologySchema' has digest <sha>... but the binding pins <sha>...; the vendored copy has drifted.`

`ontologySchemaSha256` pins a schema that has changed. If the schema is copied from elsewhere, review the change and update the pin. If your repository maintains the schema, remove `ontologySchemaSha256`.

### `<file> is not valid TOML: Unescaped '\' in a string`

Followed by `A regex belongs in a single-quoted TOML literal string`. Write `local_pattern = '[0-9]{1,3}'` or `'\d'`, not `"\d"`.

### `bindingsVersion 2.0 but this skill understands 1.x.`

The binding file was written for a newer `model`. Update `model`, or set `bindingsVersion = "1.0"` if the file really is 1.x.

### A document validates with no errors but reads no rows

With no binding file, `model` reads only `## Components` and `## Interfaces` with its default columns, so a pattern's Building Blocks table is ignored. Add the `[[markdown.tables]]` entries from the [configuration reference](configuration.md#a-complete-binding-for-the-shipped-template).

## The document and the diagram

### `'<text>' in Building Blocks matches no identifier rule, so the row was not read; a local id leads its cell, as in '01 Name'  [id_unmatched]`

A row whose first cell does not start with a catalogue id your `id_pattern` matches, or with a local id. Write `04 Audit log`, not `Audit log`; or add the series to `id_pattern`; or set `local_pattern` if you have none.

### `<id> is in the document but not on the diagram  [doc_not_in_diagram]`

A row was added and the diagram not synced. Run `model sync index.md components.drawio`. The reverse, `<id> is on the diagram but not in the document  [diagram_not_in_doc]`, means a row was removed or renamed: `sync` marks the orphan shape, and `sync --prune` deletes it.

### `<id> has no row in Catalogue Mapping; say what it realises, or that it is a gap  [mapping_missing]`

A local box without a Catalogue Mapping row. Add `| 04 | gap | gap |`, or `| 04 | COMP-017 | realises |` once you know what it is.

### `<iface>: source '<id>' is not an identified node  [edge_unknown_endpoint]`

Or `target '<id>'`. An interface's Provider or Consumer names a box the model does not know. There are two causes.

The Building Blocks row is missing. If you removed a box, also remove the interfaces and steps that name it.

Or the command read a different binding file from the one the document was written for. This happens when `publish.py` or `model scan` runs over a folder above the document's own binding file: the scan uses the binding nearest the folder it was given, not each document's. Run it on the folder that holds the binding, or move the binding up.

### `<id> has a mapping row but is not a node in this document  [mapping_unknown_local]`

A Catalogue Mapping row for a box that was removed or renumbered. Delete the row, or fix its id.

### Duplicate identifiers, dangling or mismatched arrows

`node_duplicate_id` is a shape copy-pasted in draw.io: the copy keeps the identifier and gets a new cell id. Delete the copy. `edge_dangling` is a connector with a free end, `edge_unknown_endpoint` one attached to an unidentified shape, and `step_endpoint_mismatch` an overlay arrow re-pointed by hand so it no longer matches the step. Reconnect it in draw.io, or run `sync`, which rebuilds the scenario layers from the steps tables.

### `step_not_contiguous`

Step numbers in a scenario have a gap or a duplicate. Number them 1, 2, 3 with none missing.

### `! components.drawio exists. Emitting would discard its layout.`

`emit` refuses to overwrite a diagram you may have arranged. Use `model sync index.md components.drawio`, or `emit --force` if you really want a fresh grid.

### `interface endpoints carry an identifier without a name`

A `publish.py` note, not a failure: a Provider, Consumer, Actor or Target cell holds a bare id such as `02`. Run `python <skills>/pattern/scripts/name-endpoints.py <file>` to fill in the names.

### `! <file>: <id> is an endpoint with no Building Blocks row`

From `name-endpoints.py`: it cannot name an id that has no Building Blocks row. Add the row, or fix the id.

## Views and publishing

### `components.svg is missing and draw.io desktop is not installed to render it. Export the 'Structure' layer(s) by hand, ...`

Also `... is older than its diagram ...`, or `... rendering is off (--render never)`. The view must be current before a deck can show it. Either install draw.io desktop and publish again, or export by hand: open `components.drawio` in draw.io desktop or https://app.diagrams.net, show only the layers named in the message, export as SVG to the named file beside the diagram, then run the `model stamp` command the message prints, for example:

```
python <skills>/model/bin/model.py stamp components.svg --diagram components.drawio --layer "Structure"
```

For a composite pattern the message names both `Structure` and `Participating patterns`; stamp with both `--layer` options.

### `animate failed: ! no current view of the 'Structure' layer: ...`

The walkthrough draws on the current structure view, so it fails for the same reason as above. Fix the view first.

### `skipped  <doc>` with `fails validation; fix it or pass --force`

`publish.py` does not publish a model that fails validation, because a deck built from a document and diagram that disagree shows one of them wrongly. The errors follow. Fix them; `--force` publishes anyway.

### `0 model(s)`

No document in the folder declares a diagram. Add `model: diagram: components.drawio` to the front matter, or add `--recursive` if the patterns are in subfolders.

### `no deck tags; deck skipped`

The document has no `deck:` tags. Add `<!-- deck:cover -->` after the H1 and `<!-- deck:slide label="..." -->` before the headings you want as slides.

### `! no such theme: <name>. Available: default`

`deckTheme` names a theme markdown-deck does not have. Use `default`, or a path to a `.css` file.

### The deck ignores a document's `deck_theme`

`publish.py` always passes the bound `deckTheme`, which wins over front matter. See [configuration](configuration.md#decktheme).

### `skipped <file>: a scenario image needs draw.io desktop`

With `--scenario-images` and no draw.io desktop, per-scenario images are skipped. The walkthrough does not need them.

## Composite patterns

### `Uses '<cell>': it is neither a pattern id and scenario key, such as PAT-905 S1, nor TBD and a name  [uses_invalid]`

Write `PAT-001 S1`. The id must match `[model] pattern_id` (by default two to five capitals, a hyphen, three digits). The same rule reports `the binding after the scenario key must be comma-separated id=id pairs`, and `an open participating pattern, TBD, cannot carry a binding: it has no boxes to bind yet`.

### `runs <id> <key> but has no Target; a participation step needs both, ...  [uses_step_endpoints]`

Fill in the Actor and Target: where the participating flow enters and leaves this pattern.

### `no document for the participating pattern <id> under <path>; ...  [participant_missing]`

Nothing under the patterns root is a folder named `<id>-<slug>` holding `index.md`, or a document whose H1 starts with the id. Check the id, check `doctor`'s `patterns root`, and bind `patternsRoot` if the patterns live elsewhere.

### `<id> has no scenario <key>; it has S1  [participant_scenario_missing]`

Use one of the keys listed.

### `the binding's <box> is not a box of <id>  [participant_binding]`

The left side of a binding names the participating pattern's boxes, the right side this pattern's. `the binding's <box> is not a box of this pattern` is the right side; `the binding names <box> more than once` is a repeat.

### `<id> <key> enters at its declared Start, <box> there, which cannot be matched to <box> here. ...  [participant_join]`

And `leaves at its declared Finish`. The step's Actor must correspond to the participating scenario's start, and its Target to its finish. Local ids never match across patterns on their own. Do what the message suggests: bind them, `PAT-001 S1 (01=01)`; or map the local box to a shared catalogue id in Catalogue Mapping; or use the same catalogue id in both.

### `open participating pattern TBD <name>: write it as its own pattern, then replace TBD with its id and scenario key  [participant_open]`

A reminder, not a failure, until the composite pattern is approved.

### `<id> is Approved but rests on the participating pattern <id>, which is Draft; ...  [participant_unapproved]`

The approval gate. Approve the participating pattern first, write any `TBD`, or set the composite pattern back to a status that is not approved.

### `Finish <box> is not the last step's actor or target, <a> or <b>  [scenario_start_finish]`

A declared Start must be the first step's Actor; a Finish the last step's Actor or Target. Fix the declaration or the steps.

### `step <n> uses '<cell>' in the document but '<cell>' on the diagram; run model sync  [step_uses_mismatch]`

Also `<id> has no region on the Participating patterns layer` and `the region for <id> is on the diagram but no step runs it`. The document changed after the diagram: run `model sync`.

### `composition_cycle`

A pattern reaches itself through Uses. Break the loop: a participating pattern cannot run the pattern that runs it.

### `participant_ambiguous`

Two documents claim one id, and the first found is used. Rename or remove one.

### A drill-in link from the walkthrough goes nowhere

The participating pattern's `scenarios.html` has not been built. Publish the patterns together: `publish.py <common folder> --recursive`.

## Links

### `link_unresolved`

A `[[links]]` rule matched an id, but its `locate` glob found nothing. Check the glob, which is relative to the binding file; `model doctor --doc index.md` shows what each box resolves to.

## Repository checks

### `skills-ref` fails to read `SKILL.md` on Windows

Set `PYTHONUTF8=1` first, so it reads the file as UTF-8 rather than in the system code page.

### `node scripts/validate-skills.mjs --help` says `No skills directory at <path>\--help`

It takes no flags; its one argument is the skills folder. Run `node scripts/validate-skills.mjs skills`.

### CI fails `SKILL.md within the specification's size guidance`

The body of a `SKILL.md` is over about 5,000 tokens (characters divided by four) or the file over 500 lines. Move detail into a file under the skill, such as `references/`, and link it.
