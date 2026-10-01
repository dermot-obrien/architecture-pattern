# Contributing to architecture-pattern

Thank you for your interest in contributing. Bug reports, fixes, examples and documentation improvements to the `pattern` skill are all welcome.

## Ways to contribute

- Report a bug, with the smallest document and diagram that show it.
- Suggest an improvement to the pattern template or method. Changes to how a diagram is generated or validated belong in [diagram-model](https://github.com/dermot-obrien/diagram-model).
- Fix a bug or add a feature, with tests.
- Improve the documentation or the worked example.

## Process

For a small change, fork the repository, make the change and open a pull request.

For a significant change, open an issue first describing what you want to do, so it can be discussed before you invest in it. Then fork, develop and open a pull request that references the issue.

## Before you open a pull request

Run, from the repository root:

```bash
node scripts/validate-skills.mjs skills
skills-ref validate skills/pattern
```

To check the worked examples as CI does, clone [diagram-model](https://github.com/dermot-obrien/diagram-model) and [markdown-deck](https://github.com/dermot-obrien/markdown-deck) beside this repository, run `npm install` in `markdown-deck/skills/markdown-deck`, list their `skills` directories in `AGENT_SKILLS_PATH`, then run the commands in [Running what CI runs, locally](docs/commands.md#running-what-ci-runs-locally).

Documentation for people lives in [docs/](docs/README.md), and what an agent reads in `skills/pattern/SKILL.md`. A change to behaviour updates both: `SKILL.md` briefly, linking rather than growing, and the docs in full. If you change the quick start, run it end to end in a fresh folder before opening the pull request.

Keep the skill generic. It is used by many organisations, so nothing in it may name or imply one: no organisation names, internal hosts, identifiers or brand palettes in code, templates, tests or examples. An organisation's own template, catalogue and theme belong in its own repository, bound through `[suite.pattern]` of its own `.agents/skill-bindings.toml`.

Record a user-visible change in `skills/pattern/CHANGELOG.md` and raise the version in `skills/pattern/SKILL.md` (`metadata.version`), the skill's entry in `bundle.json` (`version` and `purl`) and its entry in `.claude-plugin/marketplace.json` together. A change to `docs/` alone needs no version.

`skills-ref` is the Agent Skills reference validator; the README's [Agent Skills conformance](README.md#agent-skills-conformance) section says how to install it. CI runs both, and fails a `SKILL.md` over 500 lines or about 5,000 tokens: move detail into a file under the skill and link it.

## Releases

Each skill is versioned and released on its own, as DD-11 of AI-Assisted Work sets out. A release is a commit on `main` whose versions agree for that skill, tagged `<skill>--v<version>`, for example `pattern--v0.9.0`. Claude Code resolves a dependency range against those tags, and `gh skill install` reads them. Earlier releases were tagged after the repository, such as `architecture-pattern--v0.8.0`, and those tags stay where they are.

## Licensing of contributions

This repository is dual-licensed:

- Content (Markdown, skill instructions, templates, examples, diagrams): [CC BY 4.0](LICENSES/CC-BY-4.0.txt)
- Code (`scripts/`, shell scripts, `inputs.toml`, plugin manifests, CI workflows): [Apache-2.0](LICENSES/Apache-2.0.txt)

By submitting a contribution (pull request, patch, or issue containing code), you agree that it is licensed under the same terms as the file you are modifying. New code files must include an SPDX header:

```python
# SPDX-FileCopyrightText: <year> <your name or organisation>
# SPDX-License-Identifier: Apache-2.0
```

New content files are covered by the bulk rules in `REUSE.toml` and need no header. The project follows the [REUSE Specification 3.3](https://reuse.software/spec-3.3/).

## Open source, and giving improvements back

These skills are open source: documentation under CC BY 4.0 and code under Apache-2.0 (see `LICENSE`). You may use, copy and adapt them, inside an organisation or out, on the terms of those licences.

If you improve a skill and the improvement would be useful to others beyond you or your organisation, please give it back to the source repository, [architecture-pattern](https://github.com/dermot-obrien/architecture-pattern): open an [issue](https://github.com/dermot-obrien/architecture-pattern/issues) describing the improvement, or a pull request with the change. An issue is enough when the change is specific to your setup, or when you cannot share the code.

This repository's `NOTICE` records where its skills came from: it is derived from [AI-Assisted Architecture](https://github.com/dermot-obrien/ai-assisted-architecture), and names the source repository, path and commit of each skill. Each skill folder carries the same `NOTICE`, so a copied skill keeps its origin.

How you give back depends on how you took the skills.

### You copied the skills into another repository or skills library

A copy does not track this repository: it stays at the version you copied until you copy again.

1. Keep `NOTICE`, `LICENSE` and `LICENSES/` with every copy, including a single skill folder, and keep the copyright and licence headers in the files. Add your own attribution beside them rather than replacing them.
2. Record where the copy came from: this repository, and the tag or commit you took (for example `pattern--v0.10.1`). Release tags are named after the skill, `<skill>--v<version>`.
3. To update, copy a newer release over it, then re-apply any local changes you still need. Keep local changes small and separate, so they are easy to carry forward.
4. To give a change back, raise an issue here, or apply the change to a fork of this repository and open a pull request. A change made only in the copy is lost at the next update.

### You cloned or forked the repository and keep it in step

1. Keep this repository as a remote so you can take its releases: `git remote add upstream https://github.com/dermot-obrien/architecture-pattern.git`, then `git fetch upstream` and merge or rebase onto its `main` or a release tag.
2. Make your changes on a branch in your fork, and open a pull request against this repository's `main` for anything useful to others. Keep organisation-specific configuration out of the skills: it belongs in your workspace's bindings, which this repository never needs to see.
3. If you publish your fork, it is a derivative work: follow the section below.

## Derivative works

If you fork this repository or build on it:

1. Keep `LICENSE`, `LICENSES/`, `NOTICE` and `REUSE.toml` intact, and add your own attribution to `NOTICE` rather than replacing it.
2. Preserve the `SPDX-FileCopyrightText` and `SPDX-License-Identifier` headers in the files you carry over.
3. Mention "Based on architecture-pattern by Dermot O'Brien, derived from AI-Assisted Architecture" in your README, and link to this repository.
4. Indicate the changes you have made, as both CC BY 4.0 and Apache-2.0 require.

## Code of conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions

Open an [issue](https://github.com/dermot-obrien/architecture-pattern/issues).
