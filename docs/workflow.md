<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Everyday workflow

The tasks you come back to after the [quick start](quick-start.md). `<skills>` is where the skills are installed, and `<model>` is `<skills>/model/bin/model.py`.

Most of this is what an agent does for you when you ask for it: the `pattern` skill's [SKILL.md](../skills/pattern/SKILL.md) is the procedure it follows. This page is for doing it by hand, and for knowing what to expect.

## Asking an agent

Ask in plain words: "create a pattern for order intake", "review PAT-004 against its diagram", "publish the patterns in architecture/patterns", "compose PAT-010 from PAT-004 S1 and a TBD for notifications". In agents that support slash commands you can also type `/pattern`. The agent runs `doctor` first and stops if a binding or a dependency is missing, then reports what it produced, the derived abstraction, any composition and anything that failed, with paths.

## Author a new pattern

1. Copy the template to `<outputDir>/<ID>-<slug>/index.md`: your repository's `template` binding if it has one, otherwise `<skills>/pattern/assets/template.md`. Take the next id in your `idSeries`.
2. Set `pattern_scope`. For `problem`, rename Context to Intent and delete the sections marked WIDER SCOPE.
3. Fill it in this order, which is not document order: Intent (or Context and Non-Goals); Patterns Applied; Building Blocks; Interfaces, which usually sends you back to revise Building Blocks; then the diagram; then Scenarios; then controls, decisions and risks, which are the residue of the rest.
4. Write every endpoint as id and name, `02 Order service`. `name-endpoints.py` fills in names you left out.
5. Declare the diagram in front matter, `model: diagram: components.drawio`, and generate it:

   ```
   python <model> emit index.md --to drawio --out components.drawio
   python <model> validate index.md
   ```

6. Tag the six to twelve sections an audience needs with `deck:` comments, keep the walkthrough's `deck:html` slide, and publish (below).

Delete each guidance comment in the template as you complete its section.

## Arrange the diagram, then keep it in step

`emit` lays boxes on a grid. Open `components.drawio` in draw.io desktop or https://app.diagrams.net, arrange the Structure layer, add a key, and save. If draw.io asks, keep the file uncompressed (Preferences, untick Compressed); a compressed file cannot be read.

From then on, after every change to the tables:

```
python <model> sync index.md components.drawio
python <model> validate index.md
```

`sync` adds shapes for new rows below the existing ones, marks shapes whose row has gone (`--prune` deletes them), rebuilds each scenario layer from its steps table, and recomputes a composite pattern's regions. It never moves what you placed. `--dry-run` shows what it would do.

Do not duplicate a draw.io page to make a scenario, and do not copy and paste a shape to make a new box: the copy keeps the identifier and validation reports a duplicate. Add a row and `sync` instead.

## Bring in an existing hand-drawn diagram

Write the document's tables to match what the diagram shows, then:

```
python <model> sync index.md components.drawio --adopt --dry-run
```

`--adopt` tags each unidentified shape whose label matches a row, instead of adding a new shape. Read what it would do, then run it without `--dry-run`, and `validate`.

## Promote a local box to a catalogue id

A box with no catalogue entry yet is a local id, `02 Order service`, with a Catalogue Mapping row. When the catalogue entry exists:

```
python <model> rename index.md 02 COMP-002 --dry-run
python <model> rename index.md 02 COMP-002
```

It renames the id in every table and on the diagram, and drops the mapping row, since the box is now catalogued. Never invent a catalogue id to get past validation.

## Render the view and animate the scenarios

`publish.py` does both. By hand, with draw.io desktop:

```
python <model> render components.drawio --out components.svg --layer Structure
python <model> animate index.md
```

For a composite pattern, `render` of the Structure layer includes the Participating patterns layer unless `--no-regions`.

Without draw.io desktop, export the view by hand: in draw.io, show only the Structure layer (and Participating patterns, for a composite pattern), export as SVG to `components.svg` beside the diagram, then record it:

```
python <model> stamp components.svg --diagram components.drawio --layer Structure
python <model> animate index.md
```

`animate` draws on the committed view and never needs draw.io. Commit the diagram, the view and its `.render.json` together. `python <model> stamp --check components.svg` says whether a view is still current.

## Publish

```
python <skills>/pattern/scripts/publish.py <folder> [--recursive]
```

It validates, renders what is stale, animates, and builds `dist/<name>/deck.html` and `deck.pdf` for every document in the folder that declares a diagram. Useful variations:

| Need | Run |
|---|---|
| See what would happen | `--dry-run` |
| HTML only, faster | `--no-pdf` |
| A build machine without draw.io | `--render never`, with views committed and stamped |
| Re-render every view | `--render always` |
| A site that builds its own decks | `--recursive --no-deck` first, then the site's deck build |
| Composite patterns and their participants | `--recursive` over their common folder, so the drill-in links resolve |
| A static image per scenario too | `--scenario-images` |
| Machine-readable results | `--json` |

A model that fails validation is skipped with its errors listed; fix them rather than reaching for `--force`.

## Review a pattern

`validate` catches what the eye does not: an interface wired one way in the table and another on the canvas, an overlay step whose endpoints disagree with its metadata, an identifier drawn twice. For the rest, read against the template's guidance: a key on the diagram, two to four straight-line scenarios, non-goals for a wide scope, interfaces with their error and retry behaviour, and risks stated honestly. A branching or failure flow belongs in a sequence diagram, noted in one line where the reader expects an overlay.

## In CI

A pull request that changes a pattern can be checked without draw.io:

```
python <skills>/model/bin/model.py scan <patterns folder> --recursive
python <skills>/pattern/scripts/publish.py <patterns folder> --recursive --render never --no-pdf
```

`scan` exits 1 on any validation error. `publish.py --render never` fails on any view that is missing or stale, naming the file to export and stamp. `markdown-deck` also fails a build on a stale diagram image when `CI` is set. Point both at a folder inside the workspace, at or below the folder that holds `.agents/`, so they read the workspace's bindings; a folder above it reads the built-in defaults.

## Compose

See [Composing patterns](composing.md).
