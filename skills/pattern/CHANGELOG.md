<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.10.3] - 2026-09-30

### Fixed

- publish.py runs on Python 3.11 again. Its summary line reused the f-string's own quote inside a replacement field, which only Python 3.12 accepts, so on 3.11 the post-install check stopped with `SyntaxError: unterminated string literal` before checking anything.

## [0.10.2] - 2026-09-30

### Fixed

- publish.py passes `--theme` only when `deckTheme` is bound and the document sets no `deck_theme`. It used to pass `deckTheme`, or `default` when unset, on every build, which overrode a document's `deck_theme` and `[suite.markdown-deck] theme`. `deckTheme` no longer has a default in inputs.toml.
- The knowledge-retrieval example declares its diagram, so publish.py publishes it, and it uses the animated walkthrough instead of one image per scenario. CI publishes the examples from above their binding files.

### Changed

- Requires model ^0.8.2, whose scan reads each document's own binding file.

## [0.10.1] - 2026-09-30

### Added

- Documentation for people, in the repository's `docs/`: a quick start from an empty folder to a published pattern and a composite pattern, run end to end on Windows in PowerShell and bash; concepts; everyday workflow; composing patterns; a configuration reference covering every `[suite.pattern]` key, the `model` keys a pattern relies on, front matter and environment variables, with a complete binding for the shipped template; a command reference; troubleshooting keyed to the tools' messages and rule ids; and the examples. `SKILL.md` and the skill's README link to it.
- `SKILL.md`'s binding table lists `idSeries`, which the agent uses to number a new pattern.
- `publish.py --help` describes `folder`, `--recursive` and `--json`, and its usage line lists `--json`; `name-endpoints.py --help` describes its paths.

### Fixed

- The template said "What is often called a pattern is a wide-scope pattern"; it is a reference architecture that is a wide-scope pattern.
- `name-endpoints.py`'s description repeated a word in its example, "ABB-901 Retrieval Retrieval Service".
- `check.py`'s description implied `SKILL_DIR` must be set; it defaults to the skill the script is in.
- The skill README's usage ran the model CLI by a path relative to the skill folder and did not mention the bindings or front matter a pattern needs.

## [0.10.0] - 2026-09-30

### Added

- Composing patterns, step 6 of `SKILL.md`: a composite pattern's scenario steps run other patterns' flows through an optional Uses column, `PAT-905 S1`, or mark an open participating pattern, `TBD <name>`. It covers sketching top down with open participating patterns, composing approved patterns, the join at the participation step's Actor and Target, the composition report and the approval gate, and listing every participating pattern in Patterns Applied.
- The template's scenario table shows the optional Uses column, with a comment on how to fill it; its Patterns Applied comment asks for every participating pattern.
- `inputs.toml` declares `patternsRoot`, where participating patterns are found (unset, `outputDir` is used), and `approvedStatuses`, default Final, Approved, Active, Published.
- `publish.py` prints the composition of every composite pattern, adds it to `--json` as `composition`, and lists every composition error in full when a pattern is skipped; the approval gate fails validation like any other error.
- `check.py` reports the patterns root and the approved statuses, and fails when the installed model predates composing.
- Declared start and finish, role binding, participating patterns' regions and the call-activity marker (UML 2.5.1 ports and collaboration use, BPMN 2.0.2 call activity and start and end events): step 6 of `SKILL.md` and the template's comments cover `Start:` and `Finish:` lines under a scenario heading, a binding after the scenario key, `PAT-005 S1 (02=ABB-011)`, the `Participating patterns` layer and the `[+]` marker.
- Links from each box to its page: `SKILL.md` documents the model bindings `[model] link_site` and `link_target` and the `[[links]]` rules (`match`, `locate`, `href` with `{id}`, `{site}`, `{located}`, `{rel}`, and `target`), which make declared ids clickable in the walkthrough and in draw.io; `inputs.toml` points to them, and the template's comment says declared ids link in the walkthrough.
- `references/compose.md` and `references/links.md` hold the detail of composing and of links; `SKILL.md` summarises both and links them, so it stays within the specification's size guidance that 0.9.2 checks.
- `publish.py` renders the structure with the `Participating patterns` layer by default; `--no-regions` leaves it out, and the hand-export note names the layers to stamp.
- `examples/composite`: PAT-910 runs S1 of the knowledge-retrieval example through a binding, joining at that scenario's declared Start and Finish, and has one open participating pattern. The knowledge-retrieval example's S1 declares its Start and Finish, and its `model.json` carries them.

### Changed

- Requires `model` `^0.8.0`, the first release that reads the Uses column.

## [0.9.2] - 2026-09-30

### Added

- CI runs `skills-ref validate` on the skill, the reference validator of the [Agent Skills specification](https://agentskills.io/specification), pinned to a commit, and fails a `SKILL.md` over the specification's guidance of 500 lines or about 5,000 body tokens.
- The README has an Agent Skills conformance section: what conforming means here, and how to run the same checks locally. CONTRIBUTING lists `skills-ref validate`.

### Changed

- The README's `metadata` example shows the current version.

Nothing in the skill's behaviour changed. It already conformed: `skills-ref` reported it valid before this release, and its `SKILL.md` is 184 lines and about 3,100 body tokens.

## [0.9.1] - 2026-09-29

### Added

- `scripts/check.py`, the skill's post-install check, as DD-11 of AI-Assisted Work defines it. Run from the workspace root, it confirms `model` and `markdown-deck` are installed where an agent finds them, then runs `model doctor --skill pattern` against the workspace's `[suite.pattern]` bindings. A missing draw.io desktop is a warning. Exit 0 when all is well, 1 with one line per problem, 2 for a usage or environment error. A patch release: before 1.0.0 a minor would fall outside a dependent's `^0.9.0`, and nothing here breaks one.

## [0.9.0] - 2026-09-29

### Changed

- Follows DD-11 of AI-Assisted Work. `x-skill-requires` names its dependencies by Package URL and range: `pkg:generic/dermot-obrien/diagram-model/model ^0.7.0, pkg:generic/dermot-obrien/markdown-deck/markdown-deck ^0.6.0`. `model` 0.7.0 is the first release whose sibling discovery reads that form, so the requirement moves to `^0.7.0`.
- The skill's identifier is `pkg:generic/dermot-obrien/architecture-pattern/pattern`, and releases are tagged `pattern--v<version>`, named after the skill rather than the repository.
- The marketplace defines one package per skill: install it as `pattern@architecture-pattern`, not `architecture-pattern@architecture-pattern`. It depends on `model@diagram-model` `^0.7.0` and `markdown-deck@markdown-deck` `^0.6.0`.

## [0.8.2] - 2026-09-29

### Changed

- `ontologySchema` is described as the repository's own schema, which the skill reads as guidance, rather than a copy vendored from elsewhere. `ontologySchemaSha256` is recommended only for a schema copied from elsewhere and never edited here; for a schema the repository maintains, a pin breaks `doctor` on every edit until someone updates it, and stops the skill at step 0.

## [0.8.1] - 2026-09-29

### Changed

- The template's comments on `realises` and its references no longer name a particular capability model's rungs. They say what each reference shows, as `SKILL.md` already did, so the template carries nothing specific to the framework it came from.

## [0.8.0] - 2026-09-29

Extracted from AI-Assisted Architecture, where it was `skills/pattern`, into its own repository, https://github.com/dermot-obrien/architecture-pattern, so it can be installed and used without either framework. NOTICE records the source commits, and the history before this entry is the history of that path in AI-Assisted Architecture.

### Changed

- Depends on `model@^0.6.0`, from https://github.com/dermot-obrien/diagram-model, and `markdown-deck@^0.6.0`, from https://github.com/dermot-obrien/markdown-deck, rather than on skills that shipped with AI-Assisted Work. Nothing in either skill assumes a particular agent or IDE. For Claude Code, the architecture-pattern plugin also declares the diagram-model and markdown-deck plugins as dependencies, so installing it installs all three.
- `scripts/publish.py` finds `model` and `markdown-deck` wherever an agent installed them: any project or user skills directory of VS Code with GitHub Copilot, Cursor, Claude Code, Codex or Gemini CLI, a Claude Code plugin, or `AGENT_SKILLS_PATH`, not only beside this skill. The worked example's `run.sh` takes `MODEL` and `MARKDOWN_DECK` for the same reason.
- "Tying a pattern to capabilities" no longer names a particular capability model. `realises`, `flows` and the `cost-model` and `evidence` references are unchanged; the skill records them and a capability model that reads them decides what they are worth.
- Licensed as AI-Assisted Architecture licenses its skills: content under CC BY 4.0 and code under Apache-2.0, declared per file in `REUSE.toml`. The skill directory carries `LICENSE`, both licence texts and `NOTICE`.
- `metadata.homepage` names this repository, and `metadata.x-derived-from` names the source commit in AI-Assisted Architecture.

### Fixed

- The worked example is regenerated. Its `model.json` and the scenario layers of `components.drawio` still carried the `role_in_this_reference_architecture` column from before the rename to `pattern`, and its views had no render records. It now extracts, syncs and stamps clean, and CI checks that it stays so. Its building blocks, interfaces and patterns use invented identifiers and names, in the 900 range, so they cannot be mistaken for any real catalogue.

### Removed

- `scripts/pack-repo.py`. It assembled a standalone repository from the framework's copy; this repository is now the master.

## [0.7.1] - 2026-09-26

### Changed

- Scenario steps name their building blocks too. Actor and Target in each steps table under Scenarios are written as identifier and name, in the template, the example and the method, and `scripts/name-endpoints.py` fills them in the same way as Interfaces. The model reads only the leading identifier, so overlays, the walkthrough and validation are unchanged.

## [0.7.0] - 2026-09-26

### Added

- Interface endpoints carry names. Provider and Consumer in the Interfaces table are written as the identifier followed by the name, as Building Blocks has it, in the template, the example and the method, so the table and its deck slide read without a lookup. `scripts/name-endpoints.py <file-or-folder>` rewrites bare identifiers from the document's own Building Blocks table and reports an endpoint with no row; `--check` changes nothing and exits 1 when something would change. `publish.py` adds a note for a document that still has bare endpoints, and does not fail on it. The model reads only the leading identifier, so diagrams and validation are unchanged.

## [0.6.0] - 2026-09-26

### Added

- Optional `realises: [CAP-NNN]` front matter, with optional `flows` and `references` of type `cost-model` and `evidence`, in the template and in the skill's method. A pattern is tied to the capabilities it realises, so their rung on the definition ladder can count it: a logical pattern toward R3, a physical one with a cost model toward R4, and evidence linked from it toward R5. `aaa-rung` reads these fields. A pattern without them is unaffected.

## [0.5.0] - 2026-09-26

### Added

- draw.io desktop is optional. `publish.py --render auto|always|never`: auto (the default) renders a view only when it is missing or older than its diagram and draw.io is installed, and otherwise requires the committed view to be current; never never calls draw.io and names each view to export and stamp; always re-renders every view. A view is current when its render record matches the diagram, as `model render` or `model stamp` writes it. The walkthrough is drawn on the committed view. Requires `model` 0.5.0.
- The procedure describes exporting the Structure layer by hand from draw.io desktop or online, and stamping it.

## [0.4.1] - 2026-09-26

### Added

- `publish.py --no-deck` renders each model's views and builds its walkthrough without building a deck, so a site that builds its decks another way can regenerate every view first rather than depend on whatever was last rendered. Requires `model` 0.4.1, whose walkthrough is identical from run to run.

## [0.4.0] - 2026-09-26

### Changed

- Renamed from `reference-architecture` to `pattern`. Every architecture model is a pattern, typed by scope (`problem`, `domain`, `capability-area`, `platform`, `hosting-profile`, `epic`, as front matter `pattern_scope`) and by the abstraction `model validate` derives. A reference architecture is a wide-scope pattern and is authored the same way. The binding section is now `[suite.pattern]`, `model doctor --skill pattern` checks it, and the default identifier series is `PAT`. Breaking for a repository still binding `[suite.reference-architecture]`.

## [0.3.0] - 2026-09-26

### Changed

- A reference architecture and a pattern are described as two classes of one construct, told apart by intent and scope rather than by whether their boxes are logical building blocks or products. Any mix of boxes is allowed, and the derived abstraction that `model validate` reports is what says whether a model can be built from. Requires `model` 0.4.0.
- Scenarios are presented by the animated walkthrough. `publish.py` renders only the structure view, runs `model animate` before building the deck so an embedded walkthrough slide is current, and renders per-scenario images only with `--scenario-images`. `--no-animate` skips the walkthrough.

## [0.2.0] - 2026-09-25

### Added

- `scripts/publish.py <folder>`, which publishes every declared model in a folder: views rendered beside each document as `<stem>.svg` and `<stem>-sN.svg`, then a deck and PDF per document under `dist/<name>/`. Models that fail validation are skipped unless `--force`. `--thumbnails` passes through to `markdown-deck`.
- Guidance on local identifiers and the mapping table, on `model rename` for promotion, and on `model sync --adopt` for bringing a hand-drawn diagram into a model.

### Changed

- The procedure declares the diagram in the document's front matter, so validation and publishing find it without being told. Requires `model` 0.2.0.

## [0.1.0] - 2026-09-25

First release.

### Added

- `assets/template.md`, the reference architecture template, with each section's grounding recorded in SKILL.md rather than asserted.
- The authoring order, which is not document order: context and non-goals, then patterns, then building blocks, then interfaces, then the diagram, then scenarios. Interfaces is where the thinking happens and it usually sends you back to revise the building blocks.
- A worked example, `examples/knowledge-retrieval`, with committed inputs and outputs and a `run.sh` that regenerates every artefact.
- `inputs.toml`, declaring what this skill needs from the repository and nothing about where it lives. The repository answers in `[suite.reference-architecture]`, and `model doctor --skill reference-architecture` checks one against the other.
- A generic template. The identifier series, the deliverable code, the diagram palette and the ontology conformance statement are a house profile and now live in the consuming repository's own template, bound as `template`. A published skill should not ship one organisation's vocabulary.
- Declared dependencies on `model` and `markdown-deck`, with an explicit stop if either is absent, since no tool resolves skill-to-skill dependencies outside the Claude Code plugin route.
