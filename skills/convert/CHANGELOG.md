<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.1.0] - 2026-10-18

### Added

- `scripts/convert.py`, with `run`, `draft`, `read`, `verify` and `archive`: converts a diagram in draw.io, SVG or PNG, with any Markdown beside it, into a document of one of four types, architecture pattern, reference architecture, use case or collaboration.
- Sources from a folder, searched to any depth, or from individual files. Each diagram is a unit with the texts that link to it, share its stem, or share its folder; exports of one diagram side by side are one unit, read from the most structured.
- One conversion folder per run, holding copies of the sources, `manifest.json` (origin, fingerprint, archive path), each unit's `source.json` and `unit.json`, and `report.md`. `--dry-run` prints the plan.
- Archiving with `git mv` into `archiveDir`, keeping history; a source outside git, or untracked, is copied and left in place. Nothing is deleted. `--no-archive` and `archive` for later.
- Readers: identified draw.io through `model extract`; hand-drawn draw.io from its shapes, containers, numbered connectors and scenario layers; the draw.io inside an SVG's `content` attribute or a PNG's `mxfile` chunk; plain SVG from its shapes, lines and text, best-effort; a picture left to the agent, who writes the unit model. Markdown gives descriptions, link labels, and scenarios from mermaid sequence diagrams, steps tables and numbered lists.
- The type chosen from the content, with the reasons in the report; `--type`, front matter, or `unit.json` override it. [references/types.md](references/types.md).
- Drafting from the type's template as the repository binds it, numbering from the pattern skill's register series, a register row when one is bound, local ids, Catalogue Mapping gap rows, and conversion notes listing every uncertain reading.
- The diagram adopted from the source drawing with `model sync --adopt`, keeping its layout, or redrawn at a plain SVG's positions, else generated; a stamped preview view when draw.io desktop is not installed, so `publish.py` and the walkthrough work at once.
- The front matter signature on every document, written in one place: `kind`, `id`, `title`, and for a pattern `pattern_type` and `pattern_scope`, then `status` and `provenance`. A source waiting for the agent gets a `kind: candidate` placeholder with `portfolio.state: needs-conversion`, removed by `draft` once the document exists. `archiveDir` falls back to `[suite.portfolio] archiveDir`.
- Verification: `model validate`, then the diagram regenerated from the document's tables compared with the source, box by box and line by line.
- Examples in every format, rich, sparse and no text, and all four types, with unit and end-to-end tests.
