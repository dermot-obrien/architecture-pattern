<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Documentation

Documentation for the `pattern` skill, and the `use-case` skill that publishes with it. Start with the quick start; the rest is reference.

| Page | For |
|---|---|
| [Quick start](quick-start.md) | Install the three skills and go from an empty folder to a published pattern and a composite pattern, in about ten minutes |
| [Concepts](concepts.md) | What a pattern is, and the ideas behind the tables, the diagram, the walkthrough and the deck |
| [Everyday workflow](workflow.md) | Authoring, arranging and syncing diagrams, adopting a hand-drawn diagram, promoting local ids, working without draw.io, publishing, CI |
| [Composing patterns](composing.md) | The Uses column, Start and Finish, role bindings, where participating patterns are found, the approval gate, the diagram's regions and the walkthrough's drill-in |
| [Configuration](configuration.md) | Every binding key, front matter key and environment variable, with type, default, precedence and an example |
| [Commands](commands.md) | Every script and flag in this repository, and the `model` and `markdown-deck` commands a pattern uses |
| [Troubleshooting](troubleshooting.md) | Each error and warning message, and its fix |
| [Examples](examples.md) | The worked examples and what each shows |
| [Use cases](use-cases.md) | The `use-case` skill: what it needs, binding it, writing a use case, adapting the template, its worked example |
| [Cross-references](cross-references.md) | The `cross-reference` skill: referring to another catalogue's identifiers, the registers, checks, and the Docusaurus plugins |

The skill itself, what an agent reads, is [skills/pattern/SKILL.md](../skills/pattern/SKILL.md), with detail in [references/compose.md](../skills/pattern/references/compose.md) and [references/links.md](../skills/pattern/references/links.md).

The two skills `pattern` depends on have their own documentation: [diagram-model](https://github.com/dermot-obrien/diagram-model) for the `model` skill, and [markdown-deck](https://github.com/dermot-obrien/markdown-deck).
