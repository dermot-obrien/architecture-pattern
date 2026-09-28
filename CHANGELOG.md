<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

Releases of the architecture-pattern plugin. The `pattern` skill keeps its own [changelog](skills/pattern/CHANGELOG.md) with the detail, and a release takes its version.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.8.0] - 2026-09-29

First release as its own repository.

### Added

- `pattern` 0.8.0, extracted from AI-Assisted Architecture. NOTICE records the source commit.
- The Claude Code plugin `architecture-pattern`, in a one-plugin marketplace of the same name, depending on `diagram-model@diagram-model` and `markdown-deck@markdown-deck`, both `^0.6.0`.
- `scripts/validate-skills.mjs`, CI running it and the worked example against diagram-model and markdown-deck, a REUSE compliance check, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`.
