<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# architecture-pattern

Author an architecture pattern, at any scope from one recurring problem to a whole domain, platform or hosting profile, as one Markdown document that is also the model and also the deck. What is often called a reference architecture is a wide-scope pattern, authored the same way.

The document's tables generate the draw.io diagram and its numbered scenario overlays, and are validated against it, so a diagram that drifts is caught rather than believed. The document's tagged sections publish as HTML slides and a PDF.

This repository ships the `pattern` [Agent Skill](https://agentskills.io/specification), usable in VS Code with GitHub Copilot, Cursor, Claude Code, Codex, Gemini CLI and any other agent that reads the format. Nothing in it assumes a particular agent or IDE.

`pattern` is composition. It depends on two skills that are useful on their own and live in their own repositories:

| Skill | Repository | What it does for a pattern |
|---|---|---|
| `model` | [diagram-model](https://github.com/dermot-obrien/diagram-model) | Generates, syncs, validates and renders the diagram from the document's tables, and resolves the repository's bindings |
| `markdown-deck` | [markdown-deck](https://github.com/dermot-obrien/markdown-deck) | Turns the document's tagged sections into HTML slides and a PDF |

## Install

Install all three wherever your agent reads skills. They need not be in the same directory.

| Directory | Read by |
|---|---|
| `.agents/skills/` in the project | VS Code with GitHub Copilot, Cursor, Codex, Gemini CLI and most others |
| `.github/skills/` in the project | VS Code with GitHub Copilot, and the Copilot coding agent |
| `.cursor/skills/` in the project | Cursor |
| `.claude/skills/` in the project | Claude Code, and also VS Code with GitHub Copilot and Cursor |
| `~/.agents/skills/`, `~/.copilot/skills/`, `~/.cursor/skills/`, `~/.claude/skills/` | The same tools, for every project |

### With the GitHub CLI, for any agent

```bash
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
# --agent github-copilot|cursor|claude-code|codex|gemini-cli|... chooses the host
# --scope user installs for every project
```

`gh skill` needs GitHub CLI 2.90 or later.

### VS Code with GitHub Copilot, or Cursor

Use the commands above with `--agent github-copilot` or `--agent cursor`, or copy `skills/pattern/`, diagram-model's `skills/model/` and markdown-deck's `skills/markdown-deck/` into the project's `.agents/skills/`, which both read. Ask for a pattern or a reference architecture, or type `/pattern`.

### Claude Code, as a plugin

Each repository is also a Claude Code plugin marketplace. This plugin declares `diagram-model` and `markdown-deck` `^0.6.0` as dependencies, so installing it installs all three at versions it has been tested with:

```
/plugin marketplace add dermot-obrien/diagram-model
/plugin marketplace add dermot-obrien/markdown-deck
/plugin marketplace add dermot-obrien/architecture-pattern
/plugin install pattern@architecture-pattern
```

### Finding the dependencies

`pattern` looks for `model` and `markdown-deck` beside itself first, then in each directory on `AGENT_SKILLS_PATH` (separated as `PATH` is), then in every project and user directory in the table above, then among Claude Code plugins. Installing the three with different tools still works.

### Requirements

- Python 3.11 or newer, and Node 18 or newer.
- `npm install` run once in the folder where `markdown-deck` is installed. It installs its dependencies, including [Playwright](https://playwright.dev/) (markdown-deck 0.6.1 or later), which prints PDFs with Microsoft Edge or Google Chrome where installed, as on any Windows machine, so no browser download is needed. HTML decks, views and walkthroughs do not need Playwright.
- draw.io desktop, optionally. Without it, views are exported by hand from draw.io and stamped.

## Dependencies between skills

The Agent Skills specification has no dependency field yet, so `SKILL.md` declares what it needs in `metadata`, which every agent can read:

```yaml
metadata:
  version: "0.9.2"
  x-skill-requires: "pkg:generic/dermot-obrien/diagram-model/model ^0.7.0, pkg:generic/dermot-obrien/markdown-deck/markdown-deck ^0.6.0"
```

No agent installs a skill's dependencies from that field today, so in every agent `pattern` checks for them before it starts and stops with an instruction if one is missing. For Claude Code, its package entry in `.claude-plugin/marketplace.json` additionally repeats the requirement, resolved against the `model--v<version>` and `markdown-deck--v<version>` release tags, so there the dependencies are installed for you.

## Agent Skills conformance

`pattern` conforms to the [Agent Skills specification](https://agentskills.io/specification). Its `SKILL.md` carries only the fields the specification defines, its `name` is the name of the directory it is installed into (`skills/pattern` here, and `pattern` under whichever skills directory an installer uses), every `metadata` value is a string, and the file stays within the specification's guidance of 500 lines and 5,000 tokens, with detail in files it links by a relative path one level deep. The `x-` keys in `metadata` are this project's own, which the specification allows.

CI checks this on every pull request and every push to `main`, with `skills-ref`, the specification's reference validator, beside this repository's own `scripts/validate-skills.mjs`, which also checks that relative links resolve. To run the same checks locally, from the repository root:

```bash
python -m pip install "git+https://github.com/agentskills/agentskills@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
skills-ref validate skills/pattern
node scripts/validate-skills.mjs skills
```

On Windows, set `PYTHONUTF8=1` before running `skills-ref`, which otherwise reads `SKILL.md` in the system's code page.

## Configuring it for a repository

A repository binds the skills to its own layout in `.agents/skill-bindings.toml`: where new patterns go, its own template, its catalogue of building-block identifiers, its deck theme. `python <skills>/model/bin/model.py doctor --skill pattern` shows what is bound and what is missing. See `skills/pattern/SKILL.md`.

## Versions and identifiers

`pattern` is identified by the Package URL `pkg:generic/dermot-obrien/architecture-pattern/pattern`, which names no host, so a mirror or a move changes where it is fetched from but not what it is called. It has its own Semantic Version in `SKILL.md` (`metadata.version`), and each release is tagged `pattern--v<version>`. Its requirements name the skills it needs the same way, with a range. This follows DD-11 of [AI-Assisted Work](https://github.com/dermot-obrien/ai-assisted-work/blob/main/docs/about/design-decisions.md).

## Origin

`pattern` was developed as a skill of [AI-Assisted Architecture](https://github.com/dermot-obrien/ai-assisted-architecture), by the same author, and was extracted into this repository on 2026-09-29 at version 0.7.1 so it can be used without that framework. [NOTICE](./NOTICE) records the exact source commit; the history before extraction is the history of `skills/pattern` there.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: [SECURITY.md](SECURITY.md).

## Licence

Content (documentation, `SKILL.md`, templates, examples and diagrams) is licensed under [CC BY 4.0](LICENSES/CC-BY-4.0.txt), and code under [Apache-2.0](LICENSES/Apache-2.0.txt), the same terms as the framework it came from. See [LICENSE](./LICENSE) for which files are which, and keep [NOTICE](./NOTICE) with any copy or derivative.
