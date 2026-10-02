<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.2.0] - 2026-10-02

### Added

- Local and endorsed use cases. A use case starts local to its container, such as an epic, with an identifier scoped to it (`{container}-UC{n}` by default), and takes a registered identifier from `idSeries` only when endorsed. New optional bindings `register`, `localDir` and `localIdFormat`; `outputDir` now holds endorsed use cases. A procedure for endorsing a local use case, and `former_ids` in the template's front matter.
- `references/terms.md`: the definitions of use case, actor, subject, scenario, main success scenario, extension, formality, goal level, and use-case stories and slices, with their sources in UML 2.5.1, Jacobson, Booch and Rumbaugh, Kruchten, Cockburn and Use-Case 2.0.

### Changed

- The terms follow UML and the Unified Process: a use case has scenarios, S1 is the main success scenario and S2 onwards are alternative or extension scenarios. The template and the example call S1 the main success scenario.

## [0.1.0] - 2026-10-02, not released

### Added

- The `use-case` skill: a use case as one Markdown document that is also the model and the deck. Its Participants, Interactions and main flow (S1) generate the draw.io diagram and the animated walkthrough; its tagged sections build the deck. It is published with the `pattern` skill's `publish.py`, which it declares as a dependency with `model` and `markdown-deck`.
- `assets/template.md`: the one sentence, Participants, Interactions, Scenarios, what it returns, scope, data, systems, dependencies, measures, risks, open decisions, the next step and a catalogue mapping, each with guidance.
- `inputs.toml`: `[suite.use-case]` bindings `outputDir` (required), `template` and `idSeries` (default `UC`).
- `scripts/check.py`: the post-install check, which finds `pattern`, `model` and `markdown-deck` and runs `model doctor --skill use-case`.
- `examples/uc-900`: a worked example with its binding, diagram, view, walkthrough and model, checked by CI.
