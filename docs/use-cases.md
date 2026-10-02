<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Use cases

A use case says what a solution does for someone and what it needs, before anyone designs how it is built. A pattern says how it is built. The `use-case` skill writes the first the way `pattern` writes the second: one Markdown document that is also the model and also the deck.

Write the use case first when the question is whether to build something. Write the pattern first when the question is how.

## Use cases and scenarios

The skill follows UML and the Unified Process. A use case is a set of behaviours that gives an actor an observable result of value. A scenario is one path through it: S1 is the main success scenario, and S2 onwards are alternative or extension scenarios. A use case has scenarios, never the other way round. How much of the template is filled in is formality, in Cockburn's sense of brief, casual or fully dressed, and is separate from whether the use case is endorsed.

Every term, with its definition and source (the UML specification, Jacobson, Booch and Rumbaugh, Kruchten, Cockburn, and Use-Case 2.0), is in [the skill's terms reference](../skills/use-case/references/terms.md).

## Local and endorsed use cases

A use case starts local to the container that needs it, such as an epic or a project: a folder whose name begins with the container's identifier. It lives in the container's `use-cases` folder and takes an identifier scoped to the container, `EP-12-UC1` by default. Nobody outside the container relies on it.

When the organisation endorses it, it takes the next identifier from the registered series, `UC-007` say, moves to `outputDir`, records its local identifier in `former_ids`, and the container links to it. Ask your agent to endorse it, and it does each step; [SKILL.md](../skills/use-case/SKILL.md) lists them.

| Binding | Default | What it sets |
|---|---|---|
| `outputDir` | Required | Where endorsed use cases live |
| `idSeries` | `UC` | The registered series |
| `register` | None | A CSV of endorsed use cases, read for the next number and given a row on endorsement. A `slug` column, if it has one, names the endorsed folder |
| `localDir` | `use-cases` | The folder inside a container for its local use cases |
| `localIdFormat` | `{container}-UC{n}` | How a local identifier is formed |

## What the skill needs

| Skill | Why | Repository |
|---|---|---|
| `pattern` 0.10.3 or later | Its `publish.py` renders the view, animates the flows and builds the deck | This one |
| `model` 0.8.2 or later | Generates, syncs and validates the diagram from the document's tables, and resolves the bindings | [diagram-model](https://github.com/dermot-obrien/diagram-model) |
| `markdown-deck` 0.6.0 or later | Turns tagged sections into HTML slides and a PDF | [markdown-deck](https://github.com/dermot-obrien/markdown-deck) |

Install all four wherever your agent reads skills, as the [README](../README.md#install) describes for `pattern`, adding `use-case` from this repository.

## Bind the workspace

Add a `[suite.use-case]` section to `.agents/skill-bindings.toml`:

```toml
[suite.use-case]
outputDir = "../use-cases"     # where endorsed use cases go, relative to this file
idSeries  = "UC"               # optional; UC is the default
# template = "templates/use-case.md"   # optional; your own template instead of the skill's
```

The binding file must also map the template's Participants and Interactions tables. `skills/use-case/SKILL.md` has the snippet; a `model.toml` beside a use case does the same for that folder alone, as every example here does.

Then run the post-install check from the workspace root. It must end `use-case: ok`:

```bash
python .agents/skills/use-case/scripts/check.py
```

## Write one

Ask your agent for a use case, or by hand:

1. Copy `skills/use-case/assets/template.md` into the container, as `<container>/use-cases/<container id>-UC1-<slug>/index.md`, and replace `<ID>` with the identifier.
2. Fill in the one sentence, Participants, Interactions and S1, the main success scenario, first. The template's comments say what goes in each section, and in what order.
3. Generate the diagram once, arrange it in draw.io, and from then on keep it in step with `sync`:

   ```bash
   python .agents/skills/model/bin/model.py emit index.md --to drawio --out components.drawio
   python .agents/skills/model/bin/model.py sync index.md components.drawio
   python .agents/skills/model/bin/model.py validate index.md
   ```

4. Publish the view, the walkthrough and the deck:

   ```bash
   python .agents/skills/pattern/scripts/publish.py <use case folder>
   ```

   Every `publish.py` flag in [commands](commands.md) applies, including `--render never` without draw.io and `--recursive` over a folder of use cases.

## Adapting the template

The template's Dependencies table records what a use case needs, from whom, and whether to use it as is, change it or build new. A repository that reads needs against its own product register or maturity levels copies the template, changes that table, and points `template` under `[suite.use-case]` at the copy. Keep organisation-specific content in that copy and in your bindings, never in the installed skill, so the next update does not overwrite it.

## The worked example

[UC-900](../skills/use-case/examples/uc-900) maps a business use case to an industry reference model. It carries its own `model.toml`, its diagram, its stamped view and its extracted `model.json`. CI checks that it agrees with itself without draw.io, and that `publish.py` publishes it. Its identifiers are invented and its design is illustrative.
