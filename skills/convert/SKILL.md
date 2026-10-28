---
name: convert
description: Convert existing architecture material, a diagram in draw.io, SVG or PNG with whatever Markdown goes with it, into a document of the right pattern type, an architecture pattern, a reference architecture, a use case or a collaboration, that the pattern and use-case skills can then regenerate, check and publish. Gathers the sources into one conversion folder with a manifest, archives the originals with git mv when git tracks them, reads boxes, links and sequences from the diagram and the text, chooses the type and says why, drafts the document from the type's template, and checks the result against the source. Use when asked to convert, import, migrate or bring in old diagrams, slides exports or architecture notes as patterns, reference architectures, use cases or collaborations.
license: CC-BY-4.0 AND Apache-2.0. Content under CC BY 4.0, code under Apache-2.0; see LICENSE and NOTICE.
compatibility: Python 3.11+. Requires the `pattern` and `use-case` skills (this repository) and the `model` skill (diagram-model repository), installed wherever the agent reads skills; publishing the result also needs `markdown-deck`. draw.io desktop is optional. Archiving needs git.
metadata:
  version: "0.1.0"
  homepage: https://github.com/dermot-obrien/architecture-pattern
  x-skill-requires: "pkg:generic/dermot-obrien/architecture-pattern/pattern ^0.15.0, pkg:generic/dermot-obrien/architecture-pattern/use-case ^0.4.0, pkg:generic/dermot-obrien/diagram-model/model ^0.9.0"
---

# Convert

Existing material becomes a document the pattern skills own. Every pattern type has the same essence: a diagram, a description of its boxes, a description of the links between them, and one or more scenarios giving the sequence of what happens. Conversion finds those four parts in what someone already drew and wrote, and puts them where the type's template expects them.

Scripts do what can be done exactly: reading a draw.io file, decoding an SVG or PNG that carries one, pairing files, moving originals, writing tables, regenerating and comparing. You do the judgement: reading a picture, settling the type when the evidence is thin, and writing the prose sections from the source text.

People learning the skill, rather than agents running it, start from https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/converting.md.

## Step 0, before anything else

Run the pattern skill's resolver and use only the paths it prints:

```bash
python <skills>/model/bin/model.py doctor --skill pattern --json
```

`convert.py` finds `model`, `pattern` and `use-case` beside this skill, on `AGENT_SKILLS_PATH`, or in any agent skills directory, and exits 3 naming the one that is missing. If one is missing, stop and tell the user to install it; do not improvise a substitute.

## The four types

| Type | Boxes are | Chosen when | Template |
|---|---|---|---|
| `architecture-pattern` | ABBs and local roles | The boxes are capabilities, services or logical containers | The pattern skill's, for the type |
| `reference-architecture` | Mainly SBBs and products | The boxes name products and technologies, carry versions, or use technology icons | The pattern skill's, for the type |
| `use-case` | Participants, one with a goal | Actors and their goals: actor shapes, "as a ... I want ... so that" | The use-case skill's |
| `collaboration` | Participants working together | Otherwise: people, teams, boards, handovers, with no building-block rigour | The pattern skill's `collaboration` |

A collaboration is a pattern type with the lightest rules: its own template, the four essential parts, local ids and a free Kind. It reads with the same Participants and Interactions bindings as a use case. A repository that numbers it binds `[suite.pattern.types.collaboration]` with an `idSeries`, `CL` by default. [references/types.md](references/types.md) has the evidence each type scores and how a tie falls.

## Procedure

### 1. Plan

```bash
python <skills>/convert/scripts/convert.py run <file-or-folder>... --dry-run
```

Point it at a folder, at individual files, or both. It pairs each diagram with its text (a text that links to it, then one with the same stem, then the only diagram in the folder), groups exports of one diagram (`x.drawio`, `x.svg`, `x.png`) as one unit read from the most structured, and prints per unit what it read, the type it would choose and why, where the document would go, and what happens to each original. Show the user the plan. Ask before archiving when they have not said to: a run moves tracked originals.

### 2. Run

```bash
python <skills>/convert/scripts/convert.py run <paths>... [--type TYPE] [--out DIR] [--no-archive]
```

It makes one conversion folder per run, `<workDir>/<date>-<name>/`, holding `sources/` (copies), `manifest.json` (where each came from, its fingerprint, where it was archived), `units/<unit>/source.json` (what was read) and `unit.json` (what is drafted from), and `report.md`. Then, per unit:

1. Reads the diagram. A draw.io whose shapes carry identifiers is read by `model extract`, exactly. Any other draw.io is read from its shapes, a draw.io-exported SVG or PNG from the diagram inside it, and a plain SVG from its shapes and text, best-effort. A picture with no diagram inside it is left to you (step 3).
2. Reads the text: a title, a summary, box descriptions, link labels, and scenarios from a mermaid `sequenceDiagram`, a steps table, or a numbered list. A flow both numbered on the diagram and written in the text is one scenario.
3. Chooses the type, unless `--type` or the source's own `pattern_type` or `document_type` says.
4. Numbers it with the pattern skill's `register.py` series, adds the register row when one is bound, and drafts `<ID>-<slug>/index.md` from the type's template in the type's `outputDir`, or in `--out`. Boxes take local ids (`01 Order API`) unless drawn with a catalogue id the binding reads, links `IF-01` onwards, scenarios `S1` onwards. Every local box gets a `gap` row in Catalogue Mapping.
5. Writes `components.drawio`: the source drawing itself with the document's identifiers adopted onto its shapes (`model sync --adopt`), so the layout is kept; for a plain SVG, a redrawing at the source's positions, adopted the same way; otherwise one generated from the tables. Then a view of its structure layer, rendered by draw.io desktop when installed, else a plain preview, stamped with `model stamp`.
6. Checks the draft: `model validate`, then the diagram regenerated from the document's tables, compared with the source box by box and line by line. Differences are reported, never hidden.

Every document carries the front matter signature the portfolio discovers it by, never its file or folder name: `kind` (`pattern` or `use-case`), `id`, `title`, and for a pattern `pattern_type` and `pattern_scope`, then `status: draft` and `provenance`. A unit that needs you (step 3) gets a placeholder instead, `kind: candidate` with `portfolio.state: needs-conversion`, which `draft` removes once the real document is written.

Finally it archives, then writes `report.md`. Read the report in full before step 4.

Archiving moves each source git tracks, with `git mv`, to the same path under `archiveDir` (default `archive/` at that repository's root), so its history follows it. A source outside git, or untracked, is copied and left where it is. Nothing is ever deleted. `archiveDir` falls back to `[suite.portfolio] archiveDir`, so a repository has one archive. `--no-archive` copies only; `convert.py archive <conversion folder>` archives later.

### 3. Read a picture

A unit whose status is `needs-agent` is an image with nothing to parse. Open the image, then write into its `units/<unit>/unit.json` the boxes, links and scenarios you see, in the unit model of [references/unit-model.md](references/unit-model.md): each box's label as drawn and, where you can judge it, `geom` (its pixel box in the image, which keeps the layout); each link's ends by box label; each numbered flow as a scenario. Put the reason in `uncertain` on anything you could not read for certain, such as a faint label, an arrowhead you cannot see, or an order the picture does not give. Set `type` if you know it, and `status` to `ready`, then:

```bash
python <skills>/convert/scripts/convert.py draft <conversion folder> [--unit <unit>]
```

`draft` also redrafts a unit after you correct its `unit.json`, for a wrong type, a missed box or a reversed link; pass `--force` to overwrite a document already drafted, but only before anyone has edited it.

### 4. Complete the document

The draft holds what the source shows; the rest of the template is yours to write from the source text and the user's answers, by the pattern or use-case skill's own rules. In order:

1. Work through the `CONVERSION NOTES` comment under the H1: every uncertain reading, every note, and the reminder that Provider and Consumer follow each arrow's direction. Fix each in the tables, then delete the comment.
2. Set `pattern_scope` if the notes say it was inferred from the number of boxes.
3. Fold the `## Notes from the source` section into the sections its text belongs in, then delete it.
4. Replace each `TBD` (a box with no description, a link with no label) from the source, or ask.
5. If the source showed no sequence, write S1 from what the text says happens, or ask the user for it. A scenario is a straight line of five to ten steps.
6. Write the opening section (Context or Intent, the solution in one sentence, Purpose) and the remaining sections from the template's guidance, then remove guidance comments and example rows you have completed.

Then `model sync index.md components.drawio` after any table change, never `emit`, and check and publish with the owning skill: `python <skills>/pattern/scripts/publish.py <folder>` for every type. After arranging the diagram in draw.io, render or export its structure layer again and stamp it.

## Rules that are easy to get wrong

Never invent what the source does not show. A missing description is `TBD`, a missing sequence is a question for the user, and a guess is marked `uncertain`.

The comparison in the report is the evidence that nothing was lost. A box or line only in the source is a reading to fix in `unit.json` and redraft, or a decision the user makes; say which.

A use case drafted from material that no one has endorsed is local: rename it as the use-case skill describes before it is relied on outside its container.

Collaboration is the fallback, not a dustbin. When the report says no type was clearly ahead, look at the material and confirm the type with the user.

## Reporting back

Say where the conversion folder and its report are, and for each unit: its source, how it was read, the type and the reason, the identifier and the document's path, what `validate` and the comparison found, what is still uncertain, and which originals were archived or left in place. Never report a unit as converted while its status is `needs-agent` or `failed`.
