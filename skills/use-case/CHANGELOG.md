<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.1.0] - 2026-10-02

### Added

- The `use-case` skill: a use case as one Markdown document that is also the model and the deck. Its Participants, Interactions and main flow (S1) generate the draw.io diagram and the animated walkthrough; its tagged sections build the deck. It is published with the `pattern` skill's `publish.py`, which it declares as a dependency with `model` and `markdown-deck`.
- `assets/template.md`: the one sentence, Participants, Interactions, Scenarios, what it returns, scope, data, systems, dependencies, measures, risks, open decisions, the next step and a catalogue mapping, each with guidance.
- `inputs.toml`: `[suite.use-case]` bindings `outputDir` (required), `template` and `idSeries` (default `UC`).
- `scripts/check.py`: the post-install check, which finds `pattern`, `model` and `markdown-deck` and runs `model doctor --skill use-case`.
- `examples/uc-900`: a worked example with its binding, diagram, view, walkthrough and model, checked by CI.
