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
```

To run the worked example end to end, clone [diagram-model](https://github.com/dermot-obrien/diagram-model) and [markdown-deck](https://github.com/dermot-obrien/markdown-deck), list their `skills` directories in `AGENT_SKILLS_PATH`, then run `python skills/pattern/scripts/publish.py skills/pattern/examples --recursive --render never`. CI does exactly this.

Keep the skill generic. It is used by many organisations, so nothing in it may name or imply one: no organisation names, internal hosts, identifiers or brand palettes in code, templates, tests or examples. An organisation's own template, catalogue and theme belong in its own repository, bound through `[suite.pattern]` of its own `.agents/skill-bindings.toml`.

Record a user-visible change in `skills/pattern/CHANGELOG.md` and raise the version in `skills/pattern/SKILL.md` (`metadata.version`) and `.claude-plugin/plugin.json` and `marketplace.json` together.

## Releases

A release is a commit on `main` whose versions all agree, tagged twice: `architecture-pattern--v<version>`, which Claude Code resolves plugin dependency ranges against, and `v<version>`, which `gh skill install` and people read. `claude plugin tag` creates the first and checks that the manifests agree.

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
