<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

Releases of the architecture-pattern plugin. The `pattern` skill keeps its own [changelog](skills/pattern/CHANGELOG.md) with the detail, and a release takes its version.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.10.0] - 2026-09-30

### Added

- `pattern` 0.10.0: chaining patterns through a scenario step's Uses column, the chain report in `publish.py`, the patterns root in `check.py`, `patternsRoot` and `approvedStatuses` bindings, and `examples/chaining`.
- CI tests against diagram-model's branch of the same name when one exists, else its main, so a change made in both is tested together; it runs the chaining example and checks the approval gate fails an approved pattern over an unapproved child.

### Changed

- Requires `model` `^0.8.0`, in `SKILL.md`, `bundle.json` and the marketplace entry.

## [0.9.1] - 2026-09-29

### Added

- `pattern` 0.9.1: `scripts/check.py`, the post-install check.
- `bundle.json`, the bundle manifest DD-11 of AI-Assisted Work defines: the `pattern` skill, its purl, its requirements (`model ^0.7.0`, `markdown-deck ^0.6.0`, as `x-skill-requires` states them) and its check. The marketplace is its `claude-plugin` adapter.
- CI validates `bundle.json` with `scripts/validate-bundle.mjs`, and runs the check unbound (it must fail) and bound (it must pass). The validator and the schema are copies from AI-Assisted Work, in `scripts/` and `scripts/vendor/`, so CI needs no network.

## [0.9.0] - 2026-09-29

### Changed

- `pattern` 0.9.0: DD-11 identifiers, purl requirements, the tag `pattern--v0.9.0`, and one package per skill, `pattern@architecture-pattern`.

## [0.8.2] - 2026-09-29

### Changed

- `pattern` 0.8.2: `ontologySchema` is the repository's own schema; pin it with `ontologySchemaSha256` only if it is a copy maintained elsewhere.

## [0.8.1] - 2026-09-29

### Changed

- `pattern` 0.8.1: the template's comments no longer name a particular capability model's rungs.

## [0.8.0] - 2026-09-29

First release as its own repository.

### Added

- `pattern` 0.8.0, extracted from AI-Assisted Architecture. NOTICE records the source commit.
- The Claude Code plugin `architecture-pattern`, in a one-plugin marketplace of the same name, depending on `diagram-model@diagram-model` and `markdown-deck@markdown-deck`, both `^0.6.0`.
- `scripts/validate-skills.mjs`, CI running it and the worked example against diagram-model and markdown-deck, a REUSE compliance check, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`.
