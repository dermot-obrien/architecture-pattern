<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

Releases of the architecture-pattern plugin. Each skill keeps its own changelog with the detail, [pattern](skills/pattern/CHANGELOG.md), [use-case](skills/use-case/CHANGELOG.md) and [convert](skills/convert/CHANGELOG.md), and a release takes the version of the skill it releases.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [convert 0.1.0] - 2026-10-18

### Added

- A new skill, `convert`: a diagram in draw.io, SVG or PNG, with whatever Markdown goes with it, becomes an architecture pattern, a reference architecture, a use case or a collaboration. It gathers the sources into one conversion folder with a manifest and a report, archives originals tracked by git with `git mv`, reads boxes, links and sequences, chooses the type and says why, drafts from the type's template, and checks the draft against the source. See [converting](docs/converting.md).

## [pattern 0.13.0] - 2026-10-18

### Added

- A shipped template for a third type, `collaboration`: participants working together, with the four essential parts and the use case's Participants and Interactions tables.

## [use-case 0.3.2] - 2026-10-18

### Changed

- Requires pattern ^0.13.0.

## [pattern 0.12.0] - 2026-10-17

### Changed

- The default identifier series is `AP`, the architecture pattern's, where it was `PAT`; with the two types bound, `AP` names an architecture pattern and `RA` a reference architecture, so the kind is read from the identifier. The shipped template and the configuration guide say so. The `PAT` and `REF` series are retired; a repository that used them renumbers its documents into `AP` and `RA`.

## [use-case 0.3.1] - 2026-10-17

### Changed

- `realised_by` names architecture patterns (`AP-NNN`) and reference architectures (`RA-NNN`), the two series the pattern skill 0.12.0 mints; the retired `PAT-NNN` is gone from the template and the skill text.

## [cross-reference 0.3.1] - 2026-10-17

### Changed

- The example catalogue, the specification's example and the tests use the `AP` series, the architecture pattern's, in place of the retired `PAT`.

## [pattern 0.11.0] - 2026-10-15

### Added

- `pattern` 0.11.0: a register of minted identifiers and `register.py` to number, register and check them, for patterns kept in category folders; pattern types with their own id series, such as architecture patterns and reference architectures; an optional `outputDir`; `use-case` 0.3.0 numbers endorsed use cases from the same register; `cross-reference` 0.3.0 reads it as `localRegister` and can link bare identifiers. See each skill's changelog.

## [cross-reference 0.2.0] - 2026-10-03

### Added

- `cross-reference` 0.2.0: a file-aware local resolver for `remark-xref`, and docs routes passed to `id-routes`' `localMap`; see its changelog.

## [cross-reference 0.1.1] - 2026-10-03

### Fixed

- `cross-reference` 0.1.1: binding paths are relative to the bindings file, as for the other skills; see its changelog.

## [cross-reference 0.1.0] - 2026-10-03

### Added

- The `cross-reference` skill 0.1.0: references to another catalogue's identifiers as `code:ID`, a namespace register of short codes and an identifier register for single foreign identifiers, a CLI to validate, list, resolve and check references, and Docusaurus plugins for links, stable `id/<ID>/` addresses and the `id/index.json` manifest. It needs only Node and depends on no other skill. It has its own [changelog](skills/cross-reference/CHANGELOG.md), version and release tag, `cross-reference--v<version>`.
- `bundle.json` and `.claude-plugin/marketplace.json` list it, with its post-install check. CI runs its tests and its worked example, and binds it in the post-install check workspace.
- [docs/cross-references.md](docs/cross-references.md).

## [use-case 0.2.0] - 2026-10-02

### Added

- The `use-case` skill 0.2.0, beside `pattern`: a use case as one Markdown document that is also the model and the deck, published with `pattern`'s `publish.py`. It has its own [changelog](skills/use-case/CHANGELOG.md), version and release tag, `use-case--v<version>`.
- `bundle.json` and `.claude-plugin/marketplace.json` list it, with its post-install check and its requirements on `pattern` ^0.10.3, `model` ^0.8.2 and `markdown-deck` ^0.6.0.
- CI checks the UC-900 example as it checks the pattern examples, publishes it with `publish.py`, and runs both skills' post-install checks.
- [docs/use-cases.md](docs/use-cases.md), and a README section on updating and reinstalling the skills after this repository changes.

## [0.10.3] - 2026-09-30

### Fixed

- `pattern` 0.10.3: publish.py, and so the post-install check, runs on Python 3.11 again, as the requirements say; see its changelog.

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
