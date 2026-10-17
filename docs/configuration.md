<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Configuration reference

Everything you can set, where, and what wins. The `pattern` skill's own contract is [skills/pattern/inputs.toml](../skills/pattern/inputs.toml); the `model` and `markdown-deck` keys it relies on are summarised here and documented in full in their repositories.

## The binding file

One file binds the whole skill suite to a repository: `.agents/skill-bindings.toml`. Every command finds it by searching upward from the document (or, for `doctor`, from the working directory or `--near`), trying at each folder, in order:

1. `.agents/skill-bindings.toml`
2. `skill-bindings.toml`
3. `model.toml`
4. `.model.toml`

The first found wins; `--config <file>` on a `model` command overrides the search. With none found, `model` uses built-in defaults that read `## Components` and `## Interfaces` tables, which do not match the pattern template, so `doctor --skill pattern` warns.

Rules that apply to the whole file:

- Relative paths are relative to the folder holding the binding file, never to where a command is run. `.agents/skill-bindings.toml` therefore writes `outputDir = "../patterns"` for a `patterns/` folder at the root.
- `bindingsVersion = "1.0"`. A major version the installed `model` does not understand is refused rather than guessed at.
- Write every regular expression in a single-quoted TOML literal string, `'COMP-[0-9]{3}'`. A double-quoted string processes escapes, so `"\d"` is a TOML error.
- An absolute path is a warning, since it will not survive a clone on another machine.
- A key a skill does not declare is a warning, `'<key>' is not a binding this skill declares`, so a typo is not silently ignored.

`python <skills>/model/bin/model.py doctor --skill pattern` checks `[suite.pattern]` against the contract and prints every resolved path. `python <skills>/pattern/scripts/check.py` runs the same check after confirming the other two skills are installed.

## `[suite.pattern]`

The keys the `pattern` skill declares in `inputs.toml`.

| Key | Type | Required | Default | Read by |
|---|---|---|---|---|
| `outputDir` | directory | no | `patterns/` at the repository root | The agent, for new patterns; `register.py`; `model` for compositions |
| `template` | file | no | the skill's `assets/template.md` | The agent |
| `idSeries` | string | no | `PAT` | The agent, `register.py` |
| `register` | file | no | none | `register.py`; `model`, for compositions |
| `types` | tables | no | none | `register.py`; `model validate`; the agent |
| `deckTheme` | string | no | unset: markdown-deck chooses | `publish.py` |
| `ontologySchema` | file | no | none | The agent, as guidance |
| `ontologySchemaSha256` | string | no | none | `doctor` |
| `patternsRoot` | directory | no | `outputDir` | `model`, for compositions |
| `approvedStatuses` | list of strings | no | `["Final", "Approved", "Active", "Published"]` | `model`, for the approval gate |

### outputDir

The folder new pattern folders are created in by default, as `<outputDir>/<ID>-<slug>/index.md`; the user can always name another. If set, it must exist; `doctor` fails otherwise. It is also the last fallback for where participating patterns are found.

Unset, new patterns go in `patterns/` at the repository root (the folder holding `.agents/`, or the binding file's own), created when first needed. `register.py outdir` prints the folder in use, with a note when it is the default; the agent tells you once where it put the pattern, and `check.py` prints the same note. If `register` and `patternsRoot` are unset too, nothing says where the patterns are, so `register.py next` scans every folder in the repository (skipping hidden folders, `node_modules`, `dist` and `build`) for the highest number, and warns that it did. `check.py` warns about this configuration. It is correct, only slower in a large repository; bind `register` or `patternsRoot` to avoid it.

```toml
[suite.pattern]
outputDir = "../architecture/patterns"
```

### Patterns in category folders

Patterns need not sit in one flat folder. Point `patternsRoot` at the folder above your categories and `outputDir` at a folder new patterns land in, then move each into its category when you are ready:

```toml
[suite.pattern]
outputDir    = "../architecture/patterns/_inbox"   # new patterns are created here
patternsRoot = "../architecture/patterns"          # found here, at any depth
register     = "../registers/catalogue.csv"        # optional, see register below
```

```
architecture/patterns/
  _inbox/PAT-012-new-idea/
  integration/PAT-001-order-intake/
  platform/PAT-002-event-backbone/
```

A pattern folder carries its diagram and views with it, so a move breaks nothing inside it, and composition finds a participating pattern anywhere under `patternsRoot`. `register.py next` numbers a new pattern from the whole tree, never from `outputDir` alone. Keep a `.gitkeep` in `_inbox` so the folder survives being emptied, since `doctor` fails on a bound folder that does not exist. A hand-written relative link to a moved pattern does break; a `PAT-001` linked through `cross-reference` does not.

### template

Your repository's own pattern template, used instead of the generic one the skill ships, and instead of the one shipped for a type that names no template of its own. A house template carries what belongs to the repository rather than to a published skill: its identifier series, its deliverable code, its diagram palette, any conformance statement. It must exist if set.

```toml
template = "../templates/pattern-template.md"
```

#### Which template, and replacing one

The skill ships a template for each kind of pattern it knows, and any of them can be replaced. A new pattern of a type is written from the first of:

| Order | Template | Bound as |
|---|---|---|
| 1 | The repository's own for that type | `[suite.pattern.types.<type>] template`, a path relative to the binding file, or `builtin:<name>` for a shipped one |
| 2 | The repository's own for every pattern | `[suite.pattern] template` |
| 3 | Shipped for that type | `assets/templates/architecture-pattern.md`, `assets/templates/reference-architecture.md` |
| 4 | Shipped for any pattern | `assets/template.md` |

`python <skills>/pattern/scripts/template.py which --type <type>` prints the one in use and where it came from.

A replacement may say anything, in any order, with any extra sections and columns, so long as it keeps the construct the binding reads: every `[[markdown.tables]]` section with a table carrying every bound column, a Scenarios section with a scenario heading such as `### S1 <name>` and a steps table with Step, Actor and Action (and Target and Interface, or steps cannot name them), and the bound Catalogue Mapping columns if it has that section. A table needs only its header row. `template.py check`, which `check.py` runs, checks every template in use with `model contract`, and a repository's own template for a type is also held to that type's series in its H1. Copy a shipped template as the starting point; never edit the installed copy, which the next update overwrites.

```toml
[suite.pattern.types.reference-architecture]
idSeries = "RA"
physical = "most"
template = "../templates/reference-architecture.md"   # ours, checked against the binding
```

### idSeries

The identifier prefix for new patterns when no types are bound: `AP` gives `AP-001`, an architecture pattern. No script reads it; the agent uses it to name the next pattern. With the two types bound, each has its own: `AP` for an architecture pattern, `RA` for a reference architecture. For a Uses cell to recognise the series, it must also match `[model] pattern_id` (default `[A-Z]{2,5}-[0-9]{3}`), so a four-digit series needs `pattern_id` set too.

```toml
idSeries = "AP"
```

### deckTheme

The theme `publish.py` passes to markdown-deck as `--theme`: a built-in name (`default` is the one built in; `markdown-deck themes` lists them) or a path to a `.css` file. A relative `.css` path is resolved against the binding file.

```toml
deckTheme = "themes/house.css"      # .agents/themes/house.css
```

Precedence: a document's `deck_theme` always wins. Otherwise `publish.py` passes `deckTheme` as `--theme` when it is set, and when it is unset passes nothing, so markdown-deck chooses: `[suite.markdown-deck] theme`, then its own default. A deck built directly with `markdown-deck build` follows the same order, with its command-line option first.

### ontologySchema

Your repository's own ontology schema, which the section structure is expected to follow. The repository owns and edits it; the skill only reads it, as guidance for section order. Nothing validates a pattern against it. It must exist if set.

```toml
ontologySchema = "../metamodel/ontology-schema.json"
```

### ontologySchemaSha256

The SHA-256 of `ontologySchema`. Set it only for a schema copied from elsewhere and never edited here: `doctor` then fails when the copy drifts, with `'ontologySchema' has digest ... but the binding pins ...`. Leave it unset for a schema your repository maintains, or every edit to the schema breaks `doctor`, and so stops the skill at step 0, until the pin is updated.

```toml
ontologySchemaSha256 = "3f2a...e9"
```

### patternsRoot

Where a Uses cell's participating pattern is looked for, to any depth. Unset, `outputDir` is used. `doctor` prints the root in use and the binding it came from as `patterns root`.

A row in `register` with a `path` that exists is used before any of these. Then precedence, first set wins: `[model] patterns_root`, then `[suite.pattern] patternsRoot`, then `[suite.pattern] outputDir`, then a search of each folder from the composite pattern upward, two levels deep, stopping at the repository root.

```toml
patternsRoot = "../architecture"     # patterns spread over several folders below it
```

### types

The repository's kinds of pattern, one table each. See [pattern types](concepts.md#pattern-types) for why.

```toml
[suite.pattern.types.architecture-pattern]
label    = "Architecture pattern"
idSeries = "AP"
physical = "none"

[suite.pattern.types.reference-architecture]
label    = "Reference architecture"
idSeries = "RA"
physical = "most"
```

| Key | Meaning |
|---|---|
| `label` | What readers call it |
| `idSeries` | The prefix of its identifiers. `register.py next --type <name>` numbers in it |
| `physical` | `none`, `some` (at least one), `most` (more than half the boxes with a level) or `all` of its boxes SBBs or products, from a `[[catalogues]]` entry whose `level` is `physical`. Unset allows any mix |
| `template` | The repository's own template for the type, or `builtin:<name>`. Unset, the shipped one for the type if there is one; see [which template](#which-template-and-replacing-one) |

With types bound, `register.py next` needs `--type`, so no pattern is numbered in the wrong series, and the register's `type` column holds the type's name. `idSeries` itself is then unused by patterns.

### register

A CSV of every identifier the repository has minted, and where each lives. A new pattern takes its number from it and is given a row, composition finds a participating pattern through it before searching any folder, and `cross-reference` turns `PAT-001` in any document into a link from the same file. `use-case` may bind the same file, and so may your own building-block series: its `type` column says which is which.

```csv
id,type,name,status,path,url,summary
PAT-001,pattern,Order intake,Approved,../architecture/patterns/integration/PAT-001-order-intake,,Accepts orders from every channel
PAT-002,pattern,Event backbone,Draft,../architecture/patterns/platform/PAT-002-event-backbone,,Shared event streaming
UC-004,use-case,Track an order,Draft,../use-cases/UC-004-track-an-order,,
```

| Column | Required | Meaning |
|---|---|---|
| `id` | yes | The identifier. A register with no `id` column uses its first column |
| `type` | no | `pattern`, `use-case`, or any series of your own |
| `name`, `status` | no | Kept in step with the document's H1 and front matter by `register.py check --fix` |
| `path` | no | The folder or document, relative to the register file |
| `url` | no | Its published page, when that cannot be found from its file. Wins over `path` for links |
| `summary` | no | One line, for people reading the register |

Other columns are kept and filled with `--set`. `register.py` never adds a column.

Rows are appended, never inserted. Two branches that each take the next number both change the last line, so git stops with a conflict on the register, and resolving it is where the clash is noticed and one pattern renumbered. Do not give the register `merge=union` in `.gitattributes`, which would keep both rows silently. If both rows are kept anyway, `register.py check`, which `check.py` runs, fails on the duplicate.

```toml
register = "../registers/catalogue.csv"
```

### approvedStatuses

Front matter `status` values the approval gate counts as approved. A composite pattern whose status is one of these cannot rest on a participating pattern whose status is not, or on a `TBD`. A comma-separated string is also accepted.

Precedence: `[model] approved_statuses` wins over `[suite.pattern] approvedStatuses`, which wins over the default.

```toml
approvedStatuses = ["Approved", "Published"]
```

## `model` keys the pattern relies on

The table contract lives in the `model` skill's part of the same file. These are the keys a pattern binding uses; diagram-model's [SKILL.md](https://github.com/dermot-obrien/diagram-model/blob/main/skills/model/SKILL.md) and its example [model.toml](https://github.com/dermot-obrien/diagram-model/blob/main/skills/model/examples/model.toml) are the full reference.

### `[model]`

| Key | Type | Default | What it does |
|---|---|---|---|
| `node_id_attrs` | list | `["id"]` | draw.io attributes that carry a box's identifier. The first whose stem names an id's prefix is used (`sbb_id` for `SBB-001`), else the first |
| `edge_id_attr` | string | `edge_id` | draw.io attribute that carries an interface's identifier |
| `group_attr` | string | `group` | draw.io attribute for the table's group column |
| `kind_attr` | string | `kind` | draw.io attribute for the table's kind column |
| `local_pattern` | regex | none | What a local id looks like, such as `'[0-9]{1,3}'` for `01 Gateway` |
| `local_prefix` | string | none | Alternatively, a reserved prefix, such as `"LOC-"`, followed by two or three digits |
| `local_attr` | string | `local_id` | draw.io attribute for a local id |
| `patterns_root` | directory | none | Where participating patterns are found; wins over `[suite.pattern]` |
| `pattern_id` | regex | `[A-Z]{2,5}-[0-9]{3}` | What a participating pattern's id looks like in a Uses cell |
| `approved_statuses` | list | Final, Approved, Active, Published | Wins over `[suite.pattern] approvedStatuses` |
| `link_site` | string | none | Substituted for `{site}` in link rules |
| `link_target` | `new` or `same` | `new` | Whether a box's link opens in a new tab |

### `[[markdown.tables]]`

One entry per table that is part of the model. With none, the built-in defaults apply, and they do not read the template's Building Blocks section.

| Key | What it does |
|---|---|
| `section` | The heading the table sits under, such as `Building Blocks` |
| `entity` | `node` for boxes, `edge` for lines |
| `id_pattern` | Regex a catalogue identifier matches. For an edge table, include the node series too, since Provider and Consumer hold node ids |
| `columns` | Header names for `id`, `label`, `group`, `kind` (nodes) and `id`, `source`, `target`, `label` (edges) |

### `[markdown.scenarios]`

| Key | Default | What it does |
|---|---|---|
| `section` | `Scenarios` | The heading scenarios sit under |
| `heading_pattern` | `'^(S\d+)\b[\s:.-]*(.*)$'` | How a scenario heading gives its key and name |
| `columns` | step `Step`, actor `Actor`, action `Action`, edge `Interface`, target `Target`, uses `Uses` | Header names, merged over the defaults |

### `[markdown.mapping]`

The Catalogue Mapping table for local ids: `section` (default `Catalogue Mapping`) and `columns` for `id` (`Local ID`), `maps_to` (`Maps To`) and `relationship` (`Relationship`, one of `realises`, `partial`, `gap`).

### `[[catalogues]]`

Files identifiers are checked against: `path` (relative to the binding file), `column` (the id column), and an optional `level` of `conceptual`, `logical` or `physical`, which feeds the derived abstraction. A declared catalogue that cannot be read is an error, not an absence.

```toml
[[catalogues]]
path   = "../catalogue/components.csv"
column = "id"
level  = "logical"
```

### `[rules]`

A severity per validation rule: `error`, `warn` or `off`. [Troubleshooting](troubleshooting.md) lists the rules a pattern meets.

```toml
[rules]
mapping_missing = "off"
```

### `[style]`

draw.io style strings for what `emit` and `sync` draw: `node`, `edge`, `badge`, `flow`, `flow_uses` (a participation step's arrow) and `region` (a participating pattern's region). This is where a repository's palette goes.

### Links from boxes to pages

`[model] link_site` and `link_target`, and `[[links]]` rules, make each declared identifier a link to its page in the walkthrough and in draw.io. See [skills/pattern/references/links.md](../skills/pattern/references/links.md).

```toml
[model]
link_site   = "https://architecture.example.org"
link_target = "new"

[[links]]
match  = 'COMP-[0-9]{3}'                         # full match on the id; rules tried in order
locate = "../catalogue/components/{id}-*"        # optional glob, relative to the binding file
href   = "{site}/catalogue/components/{located}/"
target = "same"                                  # optional; wins over link_target
```

`href` may use `{id}`, `{site}`, `{located}` (the glob's first match relative to its fixed folders, with a matched `index.md` dropped) and `{rel}` (the path from the generated page to the match). Add a rule for your pattern series too, so a participation step links to its participating pattern's page. Local ids never link. A rule that matches but locates nothing is a `link_unresolved` warning; `model doctor --doc index.md` shows what each box resolves to.

## `[suite.markdown-deck]`

markdown-deck's repository defaults, documented in its [README](https://github.com/dermot-obrien/markdown-deck#repository-defaults): `theme`, `palette`, `comments`, `thumbnails`, `pdf`, `tableRows`, `feedbackTo`, `feedbackSubject`, `mermaid` and `registry`. Under `publish.py`, `theme` and `pdf` are overridden (see [deckTheme](#decktheme), and `publish.py` always passes `--pdf` or `--no-pdf`); the others apply as usual.

## A complete binding for the shipped template

This binds the generic template: `COMP-NNN` building blocks, `IF-NN` interfaces, plain-number local ids, `PAT-NNN` patterns, with patterns in `architecture/patterns/`.

```toml
bindingsVersion = "1.0"

[model]
node_id_attrs = ["component_id"]
edge_id_attr  = "iface_id"
group_attr    = "group"
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

[suite.pattern]
outputDir        = "../architecture/patterns"
idSeries         = "PAT"
# deckTheme      = "default"      # unset: markdown-deck chooses
approvedStatuses = ["Final", "Approved", "Active", "Published"]

[suite.markdown-deck]
theme = "default"
```

## Front matter

Keys in a pattern document's YAML front matter.

| Key | Type | Required | Read by | What it does |
|---|---|---|---|---|
| `title` | string | recommended | markdown-deck, sites | Deck and page title; the deck falls back to `sidebar_label`, then the file name |
| `sidebar_label` | string | no | sites, markdown-deck | Short label; markdown-deck's eyebrow falls back to it |
| `description` | string | no | sites | One-line summary |
| `document_type` | string | no | your site or catalogue | `pattern` |
| `pattern_type` | string | no | `model validate`, the register | One of the bound [types](#types); unset, the type whose `idSeries` the identifier carries |
| `implements` | list | no | `model validate` | The patterns this one makes concrete, `[AP-004]`; each must have a document |
| `pattern_scope` | enum | yes | the agent, readers | `problem`, `domain`, `capability-area`, `platform`, `hosting-profile` or `epic` |
| `status` | string | recommended | `model` | Checked against the approved statuses by the approval gate |
| `version`, `last_modified`, `author` | string | no | readers | Housekeeping |
| `model.diagram` | path | yes, to publish | `model`, `publish.py` | The diagram, relative to the document. `publish.py` and `model scan` publish only documents that declare one |
| `realises` | list | no | a capability model | Capability ids this pattern realises |
| `flows` | list | no | a capability model | Only these flows of them; omit for every flow |
| `references` | list of `{type, path}` | no | a capability model | `type: cost-model` or `type: evidence` |
| `provenance` | map | no | your review process | `origin` and `review_state` |
| `deck_*` | various | no | markdown-deck | `deck_theme`, `deck_palette`, `deck_eyebrow`, `deck_comments`, `deck_thumbnails`, `deck_pdf`, `deck_table_rows`, `deck_feedback_to`, `deck_feedback_subject`, `deck_id`, `deck_publish`; see markdown-deck |

```yaml
---
title: "PAT-012 Order Intake"
pattern_scope: problem
status: Draft
realises: [CAP-012]
flows: [take-order]
references:
  - { type: cost-model, path: "../cost/order-intake.xlsx" }
model:
  diagram: components.drawio
---
```

## Conventions inside the document

| Where | Convention |
|---|---|
| Under a scenario heading, before its table | `Start: <id> <name>` and `Finish: <id> <name>`, each its own paragraph |
| A steps table | A `Uses` column: `PAT-001 S1`, `PAT-001 S1 (a=b, c=d)`, or `TBD <name>` |
| `## Catalogue Mapping` | One row per local id: Local ID, Maps To, Relationship (`realises`, `partial`, `gap`) |
| HTML comments | `deck:cover`, `deck:slide`, `deck:html`, `deck:skip`, `deck:note` and the rest of markdown-deck's tags |

## Environment variables

| Variable | Read by | What it does |
|---|---|---|
| `AGENT_SKILLS_PATH` | `publish.py`, `check.py`, `model` | Extra folders to find skills in, separated as `PATH` is (`;` on Windows, `:` elsewhere). Searched after the folder beside `pattern` |
| `SKILL_DIR` | `check.py` | The installed `pattern` folder; defaults to the one the script is in. An installer sets it |
| `CLAUDE_CONFIG_DIR` | `publish.py`, `model` | Where Claude Code keeps plugins, when it is not `~/.claude` |
| `MODEL`, `MARKDOWN_DECK` | the worked example's `run.sh` | Paths to the two CLIs when they are not beside the skill |
| `MARKDOWN_DECK_CHANNEL`, `MARKDOWN_DECK_BROWSER` | markdown-deck | The browser the PDF export uses |
| `CI` | markdown-deck | When set, a stale diagram image fails the deck build rather than warning |
| `PYTHONUTF8` | `skills-ref` | Set to `1` on Windows so `SKILL.md` is read as UTF-8 |
