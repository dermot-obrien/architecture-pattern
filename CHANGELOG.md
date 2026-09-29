<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

Releases of the architecture-pattern plugin. The `pattern` skill keeps its own [changelog](skills/pattern/CHANGELOG.md) with the detail, and a release takes its version.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.10.2] - 2026-09-30

### Fixed

- publish.py passes `--theme` only when `deckTheme` is bound and the document sets no `deck_theme`. It used to pass `deckTheme`, or `default` when unset, on every build, which overrode a document's `deck_theme` and `[suite.markdown-deck] theme`. `deckTheme` no longer has a default in inputs.toml.
- The knowledge-retrieval example declares its diagram, so publish.py publishes it, and it uses the animated walkthrough instead of one image per scenario. CI publishes the examples from above their binding files.

### Changed

- Requires model ^0.8.2, whose scan reads each document's own binding file.

## [0.10.1] - 2026-09-30

### Added

- Documentation in `docs/`: a quick start from an empty folder to a published pattern and a composite pattern, in PowerShell and bash, run end to end on Windows; concepts; everyday workflow; composing patterns; configuration, command and troubleshooting references; and the examples. The README gains a quick start, a documentation index, a git install route for any agent, and Codex and Gemini CLI install notes.
- `pattern` 0.10.1: small fixes to the template, the scripts' help and the skill README; see its changelog.

### Fixed

- The README's Claude Code section no longer gives the dependency range as `^0.6.0` for both skills; `model` is `^0.8.0`, as `SKILL.md` says.
- CONTRIBUTING said CI runs `publish.py` over the examples; it runs the model and deck commands in `.github/workflows/ci.yml`, which `docs/commands.md` now shows how to run locally.

## [0.10.0] - 2026-09-30

### Added

- `pattern` 0.10.0: composite patterns, whose scenario steps run participating patterns through a Uses column, the composition report in `publish.py`, the patterns root in `check.py`, `patternsRoot` and `approvedStatuses` bindings, declared Start and Finish, role binding, the `Participating patterns` regions (`publish.py --no-regions`), the `[+]` call-activity marker, links from declared ids to their pages (model's `[[links]]` bindings), and `examples/composite`.
- CI tests against diagram-model's branch of the same name when one exists, else its main, so a change made in both is tested together; it runs the composite example and checks the approval gate fails an approved composite pattern over an unapproved participating pattern.

### Changed

- Requires `model` `^0.8.0`, in `SKILL.md`, `bundle.json` and the marketplace entry.

## [0.9.2] - 2026-09-30

### Added

- `pattern` 0.9.2: CI validates it with `skills-ref`, the Agent Skills reference validator, and checks its size against the specification's guidance. The README says how to run both locally.

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
