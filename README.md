<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# architecture-pattern

Author an architecture pattern, at any scope from one recurring problem to a whole domain, platform or hosting profile, as one Markdown document that is also the model and also the deck. What is often called a reference architecture is a wide-scope pattern, authored the same way.

The document's tables generate the draw.io diagram and its numbered scenario overlays, and are validated against it, so a diagram that drifts is caught rather than believed. The document's tagged sections publish as HTML slides and a PDF.

This repository ships three [Agent Skills](https://agentskills.io/specification), usable in VS Code with GitHub Copilot, Cursor, Claude Code, Codex, Gemini CLI and any other agent that reads the format. Nothing in them assumes a particular agent, IDE or organisation.

| Skill | What it writes |
|---|---|
| `pattern` | An architecture pattern: how a solution is built |
| `use-case` | A use case: what a solution does for someone and what it needs, before anyone designs how it is built. It publishes with `pattern`'s tools; see [use cases](docs/use-cases.md) |
| `cross-reference` | References to another catalogue's building blocks and patterns, `ops:ABB-024`, without clashes, and stable addresses for your own. It needs only Node; see [cross-references](docs/cross-references.md) |

`pattern` is composition. It depends on two skills that are useful on their own and live in their own repositories:

| Skill | Repository | What it does for a pattern |
|---|---|---|
| `model` | [diagram-model](https://github.com/dermot-obrien/diagram-model) | Generates, syncs, validates and renders the diagram from the document's tables, and resolves the repository's bindings |
| `markdown-deck` | [markdown-deck](https://github.com/dermot-obrien/markdown-deck) | Turns the document's tagged sections into HTML slides and a PDF |

## Quick start

Install the three skills into a workspace (below), bind it in `.agents/skill-bindings.toml`, write a pattern, then:

```
python .agents/skills/pattern/scripts/check.py
python .agents/skills/model/bin/model.py emit patterns/PAT-001-order-intake/index.md --to drawio --out patterns/PAT-001-order-intake/components.drawio
python .agents/skills/model/bin/model.py validate patterns/PAT-001-order-intake/index.md
python .agents/skills/pattern/scripts/publish.py patterns --recursive
```

Or ask your agent for a pattern and it does the same. The [quick start](docs/quick-start.md) goes from an empty folder to a published pattern and a composite pattern in about ten minutes, in PowerShell and bash, with a small example to copy and the output you should see at each step.

## Documentation

| Page | For |
|---|---|
| [Quick start](docs/quick-start.md) | From nothing to a published pattern, its view, walkthrough, deck and PDF, and a composite pattern |
| [Concepts](docs/concepts.md) | What a pattern is, and the ideas behind the tables, the diagram, the walkthrough and the deck |
| [Everyday workflow](docs/workflow.md) | Authoring, syncing, adopting a hand-drawn diagram, promoting local ids, working without draw.io, publishing, CI |
| [Composing patterns](docs/composing.md) | Composite patterns: the Uses column, Start and Finish, role bindings, the approval gate |
| [Configuration](docs/configuration.md) | Every binding key, front matter key and environment variable |
| [Commands](docs/commands.md) | Every script and flag, and the `model` and `markdown-deck` commands a pattern uses |
| [Troubleshooting](docs/troubleshooting.md) | Each error and warning message, and its fix |
| [Examples](docs/examples.md) | The worked examples and what each shows |
| [Use cases](docs/use-cases.md) | The `use-case` skill: binding it, writing a use case, adapting the template |
| [Cross-references](docs/cross-references.md) | The `cross-reference` skill: namespace codes, the two registers, checking references, the Docusaurus plugins |

## Install

Install all three skills wherever your agent reads skills, and `use-case` beside them if you write use cases. They need not be in the same directory.

| Directory | Read by |
|---|---|
| `.agents/skills/` in the project | VS Code with GitHub Copilot, Cursor, Codex, Gemini CLI and most others |
| `.github/skills/` in the project | VS Code with GitHub Copilot, and the Copilot coding agent |
| `.cursor/skills/` in the project | Cursor |
| `.claude/skills/` in the project | Claude Code, and also VS Code with GitHub Copilot and Cursor |
| `~/.agents/skills/`, `~/.copilot/skills/`, `~/.cursor/skills/`, `~/.claude/skills/` | The same tools, for every project |

A directory in the project installs the skills for that workspace; one under your home folder installs them for every project. This repository has no installer of its own. Whichever route you use, run the post-install check from the workspace root afterwards: `python <skills>/pattern/scripts/check.py`, and `python <skills>/use-case/scripts/check.py` for `use-case`.

### With the GitHub CLI, for any agent

```bash
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/architecture-pattern use-case   # optional
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
# --agent github-copilot|cursor|claude-code|codex|gemini-cli|... chooses the host
# --scope user installs for every project
```

`gh skill` needs GitHub CLI 2.90 or later.

### With git, for any agent

Clone each repository at a release tag and copy its skill folder. This works with any agent; the [quick start](docs/quick-start.md#2-make-a-workspace-and-install-the-three-skills) has the same commands for PowerShell.

```bash
git clone --depth 1 --branch use-case--v0.2.0 https://github.com/dermot-obrien/architecture-pattern.git _src/architecture-pattern
git clone --depth 1 --branch model--v0.8.2 https://github.com/dermot-obrien/diagram-model.git _src/diagram-model
git clone --depth 1 --branch markdown-deck--v0.6.8 https://github.com/dermot-obrien/markdown-deck.git _src/markdown-deck
mkdir -p .agents/skills
cp -r _src/architecture-pattern/skills/pattern _src/architecture-pattern/skills/use-case _src/diagram-model/skills/model _src/markdown-deck/skills/markdown-deck .agents/skills/
rm -rf _src
```

Copy into `.claude/skills`, `.cursor/skills`, `.github/skills` or a home directory from the table instead of `.agents/skills` to suit your agent. Release tags are named `<skill>--v<version>`; the `use-case--v0.2.0` tag also carries `pattern` 0.10.3, and the three above were tested together. Leave out `use-case` if you do not write use cases. For a user-level install, copy into `~/.agents/skills` (or your agent's own) and run the check from any workspace.

### VS Code with GitHub Copilot, or Cursor

Use the commands above with `--agent github-copilot` or `--agent cursor`, or copy `skills/pattern/`, diagram-model's `skills/model/` and markdown-deck's `skills/markdown-deck/` into the project's `.agents/skills/`, which both read. Ask for a pattern or a reference architecture, or type `/pattern`.

### Codex and Gemini CLI

Both read `.agents/skills/` in the project. Use `gh skill install` with `--agent codex` or `--agent gemini-cli`, or the git route above.

### Claude Code, as a plugin

Each repository is also a Claude Code plugin marketplace. This plugin declares `diagram-model` and `markdown-deck` as dependencies, so installing it installs all three at versions it has been tested with:

```
/plugin marketplace add dermot-obrien/diagram-model
/plugin marketplace add dermot-obrien/markdown-deck
/plugin marketplace add dermot-obrien/architecture-pattern
/plugin install pattern@architecture-pattern
/plugin install use-case@architecture-pattern   # optional; declares pattern as a dependency
```

Claude Code also reads skills copied into `.claude/skills/` or `~/.claude/skills/` by the git route.

### Finding the dependencies

`pattern` looks for `model` and `markdown-deck` beside itself first, then in each directory on `AGENT_SKILLS_PATH` (separated as `PATH` is), then in every project and user directory in the table above, then among Claude Code plugins. Installing the three with different tools still works.

### Requirements

- Python 3.11 or newer, and Node 18 or newer.
- `npm install` run once in the folder where `markdown-deck` is installed, for example `npm install --prefix .agents/skills/markdown-deck`. It installs its dependencies, including [Playwright](https://playwright.dev/) (markdown-deck 0.6.1 or later), which prints PDFs with Microsoft Edge or Google Chrome where installed, as on any Windows machine, so no browser download is needed. HTML decks, views and walkthroughs do not need Playwright.
- draw.io desktop, optionally. Without it, views are exported by hand from draw.io and stamped.

## Updating, and reinstalling after the source changes

An installed skill is a copy. Pulling this repository, or a newer release appearing, changes nothing in a workspace until the skills are installed again. Reinstall all of them together, because `use-case` needs the `pattern` from the same release, and `pattern` needs `model` and `markdown-deck` at the versions its `SKILL.md` names.

| How you installed | To update |
|---|---|
| GitHub CLI | Run the same `gh skill install` commands again |
| git | Fetch the newer tags (or `git pull` a clone you keep), delete each installed skill folder, copy it again from the clone, as in [With git](#with-git-for-any-agent). Deleting first matters: copying over the top leaves files a release removed |
| Claude Code plugin | `/plugin marketplace update architecture-pattern`, and the same for `diagram-model` and `markdown-deck`, then reinstall the plugins |
| A workspace installer that pins each source to a commit | Move the pin to the new commit, run the installer, and commit the pin with whatever the update changes |

Then, every time:

1. `npm install` again in the installed `markdown-deck` folder if `markdown-deck` changed.
2. Run each post-install check from the workspace root, `python <skills>/pattern/scripts/check.py` and `python <skills>/use-case/scripts/check.py`. Both must end `ok`. A new release can add a required binding, which the check names.
3. Republish a pattern or use case you rely on, `publish.py <folder>`, to see that it still builds.

Never edit an installed copy: the next install overwrites it. Keep your own configuration in `.agents/skill-bindings.toml`, your own template and your own theme, which an update never touches, and give changes to the skills back here (see [CONTRIBUTING](CONTRIBUTING.md#open-source-and-giving-improvements-back)).

## Dependencies between skills

The Agent Skills specification has no dependency field yet, so `SKILL.md` declares what it needs in `metadata`, which every agent can read:

```yaml
metadata:
  version: "0.10.3"
  x-skill-requires: "pkg:generic/dermot-obrien/diagram-model/model ^0.8.0, pkg:generic/dermot-obrien/markdown-deck/markdown-deck ^0.6.0"
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

A repository binds the skills to its own layout in `.agents/skill-bindings.toml`: where new patterns go and where a composite pattern's participating patterns are found, its own template, its tables and identifier series, its catalogue of building-block identifiers, its deck theme. `python <skills>/model/bin/model.py doctor --skill pattern` shows what is bound and what is missing. The [configuration reference](docs/configuration.md) covers every key, with a complete binding for the shipped template.

## Versions and identifiers

`pattern` is identified by the Package URL `pkg:generic/dermot-obrien/architecture-pattern/pattern`, which names no host, so a mirror or a move changes where it is fetched from but not what it is called. It has its own Semantic Version in `SKILL.md` (`metadata.version`), and each release is tagged `pattern--v<version>`. Its requirements name the skills it needs the same way, with a range. `use-case` is `pkg:generic/dermot-obrien/architecture-pattern/use-case`, versioned and tagged the same way (`use-case--v<version>`), and requires `pattern` by range like any other skill. This follows DD-11 of [AI-Assisted Work](https://github.com/dermot-obrien/ai-assisted-work/blob/main/docs/about/design-decisions.md).

## Origin

`pattern` was developed as a skill of [AI-Assisted Architecture](https://github.com/dermot-obrien/ai-assisted-architecture), by the same author, and was extracted into this repository on 2026-09-29 at version 0.7.1 so it can be used without that framework. [NOTICE](./NOTICE) records the exact source commit; the history before extraction is the history of `skills/pattern` there. `use-case` was written in this repository, split from `pattern` before either released it, and first released as 0.2.0 on 2026-10-02; its own NOTICE says so.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: [SECURITY.md](SECURITY.md).

## Licence

Content (documentation, `SKILL.md`, templates, examples and diagrams) is licensed under [CC BY 4.0](LICENSES/CC-BY-4.0.txt), and code under [Apache-2.0](LICENSES/Apache-2.0.txt), the same terms as the framework it came from. See [LICENSE](./LICENSE) for which files are which, and keep [NOTICE](./NOTICE) with any copy or derivative.
