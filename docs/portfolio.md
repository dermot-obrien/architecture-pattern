<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# The portfolio

Two skills keep a repository's patterns current. `portfolio` knows what is there: it lists every pattern on one page, tags what needs conversion or is proposed for deprecation, archives what is agreed, and turns a backlog into placeholders. `draft` gives a placeholder its first draft, written from research and citing its sources, for a person to review.

This page is the guide. The agent's instructions are in [skills/portfolio/SKILL.md](../skills/portfolio/SKILL.md) and [skills/draft/SKILL.md](../skills/draft/SKILL.md), and the exact front matter is in [the signature reference](../skills/portfolio/references/signature.md).

## Contents

- [The signature](#the-signature)
- [Install and bind](#install-and-bind)
- [Cleaning out a repository](#cleaning-out-a-repository)
- [The inventory page](#the-inventory-page)
- [From a backlog to placeholders](#from-a-backlog-to-placeholders)
- [Drafting a placeholder](#drafting-a-placeholder)
- [Commands](#commands)
- [Why it works this way](#why-it-works-this-way)

## The signature

A document is a pattern because its front matter says so, and for no other reason. File names, folder names, headings and tags are never read to decide: a folder called `AP-012-something` with no front matter is not a pattern, and a page called `pattern.md` is not one either.

| Front matter | Is |
|---|---|
| `kind: pattern` and `pattern_type: architecture-pattern` | An architecture pattern, `AP-NNN` |
| `kind: pattern` and `pattern_type: reference-architecture` | A reference architecture, `RA-NNN` |
| `kind: pattern` and `pattern_type: collaboration` | A collaboration, `CL-NNN` |
| `kind: use-case` | A use case, `UC-NNN` |
| `kind: candidate` | A possible pattern, not formally one yet |

This is the continuum's front matter standard, so the same pages pass the continuum's check. The pattern and use-case templates carry `kind` from pattern 0.14.0 and use-case 0.4.0, so everything new is signed from the start.

The portfolio's own fields sit in one optional block:

```yaml
portfolio:
  state: proposed-deprecation    # placeholder, draft, needs-conversion, proposed-deprecation, archive or archived
  priority: high                 # high, medium, low or none
  target_quarter: "2027-Q1"
  committed: true
  reason: "Superseded by AP-002"
  since: 2026-10-18
```

With no `state`, a document is live and nothing is pending. [The signature reference](../skills/portfolio/references/signature.md) lists every field and value, and what sets each state.

## Install and bind

Install `portfolio` and `draft` beside `pattern` and `use-case`, wherever your agent reads skills, as in the [README's install section](../README.md#install). Both need only Python 3.11 and git.

Nothing has to be bound: with no bindings the whole repository is scanned, the archive is `archive/` at the root, and the inventory is printed. To choose, add to `.agents/skill-bindings.toml`, with paths relative to that file:

```toml
[suite.portfolio]
roots = ["../patterns", "../use-cases", "../candidates"]   # where to look; default, the whole repository
archiveDir = "../archive"                                  # where archived pages go
inventory = "../docs/portfolio.md"                         # the page inventory writes; .md, .html or .json
candidatesDir = "../candidates"
linkBase = "/architecture/"                                # on a site: link identifiers to their stable address
```

Placeholders go where a new pattern would: `[suite.pattern] outputDir`, or `[suite.use-case] outputDir`, numbered in the type's series. Bind the collaboration type beside the other two:

```toml
[suite.pattern.types.collaboration]
label = "Collaboration"
idSeries = "CL"
```

Then check:

```bash
python .agents/skills/portfolio/scripts/check.py
```

## Cleaning out a repository

The order that works on a repository that has grown for years. Every step that changes a file has `--dry-run`; look at it first, and commit after each step so each change is reviewable on its own. `P` below is `python .agents/skills/portfolio/scripts/portfolio.py`, run from the repository root.

1. See what is signed.

   ```bash
   P discover
   ```

   Patterns written before the signature appear as legacy if they carry `pattern_type`, `document_type: pattern` or `document_type: use-case`. Anything else, such as a folder of old diagrams and notes, does not appear at all: that is material for the convert skill, which turns it into a signed document, or for a hand-written `kind` line once you have decided it is a pattern.

2. Sign the legacy pages, and check.

   ```bash
   P sign --dry-run
   P sign
   P check
   ```

   `check` reports identifiers outside their type's series, duplicates and malformed portfolio blocks. Fix those before going on.

3. Tag.

   ```bash
   P tag --dry-run
   P tag
   ```

   A page missing one of its type's four parts (a diagram, the boxes table, the links table, scenarios) is tagged `needs-conversion`, with the parts it lacks in `reason`. Send those to the convert skill; `tag` clears the state once the page is in form. A page whose status is deprecated, superseded or retired, or that has `superseded_by` or a past `valid_until`, is tagged `proposed-deprecation`. Bind `staleAfterDays` to propose old pages too. `tag` never overrides a state a person set.

4. Agree. Take the inventory's "Needs attention" table to whoever decides. For each deprecation agreed, mark the page:

   ```bash
   P tag patterns/AP-003-nightly-batch-export --state archive --reason "Agreed at the architecture review, 2026-10-20"
   ```

   For one not agreed, clear the tag with `--clear`.

5. Archive.

   ```bash
   P archive --dry-run
   P archive --rewrite-links
   ```

   Each page marked `archive` moves, with its folder when nothing else signed shares it, to the same place under the archive folder, with `git mv` so `git log --follow` keeps its history. It is marked `archived` and `unlisted`. Nothing is deleted, and a second run does nothing. The dry run lists every link the move would break, into the page and out of it; `--rewrite-links` rewrites them. Without it they are reported and left, and `--stub` leaves a short page at the old place saying where it went, for addresses outside the repository.

6. Regenerate the inventory and commit.

   ```bash
   P inventory
   ```

## The inventory page

`P inventory` writes one page: every document by type, with its identifier, a link, status, portfolio state, priority, quarter, whether it is committed and a summary (its `description`, else its first paragraph); then the candidates; then what needs attention; then, with `--include-archived`, the archive; and last, any signature problems. The format follows the file's extension, or `--format md|html|json`; `--out -` prints it.

The page carries no date, so regenerating an unchanged portfolio changes nothing and a build never commits noise.

On a Docusaurus site, bind `linkBase`, and each identifier links to `{linkBase}id/{ID}/`, the stable address the [cross-reference](cross-references.md) skill's plugin publishes. Those addresses survive a page moving to the archive.

To keep the page current on a site built by the continuum's workspace skill, its `regenerate` step writes the inventory before every build when the portfolio skill is installed and `[suite.portfolio] inventory` is bound. Until your workspace skill has that step, add it to the site's prebuild yourself:

```json
"prebuild": "node scripts/architecture.mjs regenerate && python .agents/skills/portfolio/scripts/portfolio.py inventory"
```

## From a backlog to placeholders

Write the backlog as a Markdown table, a bullet list or a CSV. Only a name is required:

```markdown
| Name | Type | Committed | Priority | Quarter | Ref |
|---|---|---|---|---|---|
| Event-driven ingestion | AP | yes | high | 2027-Q1 | BL-2 |
| Zero-trust ingress | RA | yes | medium | 2027-Q2 | BL-6 |
| Data mesh | | no | low | | BL-8 |
```

```markdown
- Zero-trust ingress (reference architecture); committed; quarter: 2027-Q2
- [x] Event-driven ingestion
- Data mesh; P3
```

Then:

```bash
P backlog backlog.md --dry-run
P backlog backlog.md --report backlog-report.md
```

The report sorts every row into matched (exactly, by name or identifier, or fuzzily, when one document is close and no other is near it), ambiguous, new or duplicate. Only unambiguous rows are acted on:

| Row | Action |
|---|---|
| New and committed | A placeholder: the type's template under the type's `outputDir`, with the next identifier in its series, `status: draft` and `portfolio.state: placeholder` |
| Matches a candidate, and committed | The candidate is promoted: moved with `git mv` to the placeholder's place, its notes kept at the end |
| Matches a document | Nothing, unless `--update`, which copies the row's priority, quarter and commitment onto it |
| New and not committed | Nothing, unless `--candidates`, which writes a candidate page |
| Ambiguous | Nothing: the report lists the close documents, and you decide |

Run it again after editing the backlog: rows already turned into placeholders now match them, so nothing is made twice. [The backlog reference](../skills/portfolio/references/backlog.md) has every column name it accepts and the matching thresholds.

## Drafting a placeholder

Ask your agent to draft a placeholder, or run the steps yourself. `D` is `python .agents/skills/draft/scripts/draft.py`.

```bash
D plan patterns/AP-007-event-sourced-ledger/index.md
```

`plan` writes `research.json` beside the placeholder: the template's sections, queries to search for, and the repository's own sources, numbered R1, R2 and so on (related patterns, the candidate's notes, passages that use the pattern's terms). The agent then searches online, reads, and records each source it will rely on with `D add-source`, which numbers them W1, W2 and so on. It writes the sections it can support, citing `[R1]` or `[W2]` after each claim, and assembles them:

```bash
D write patterns/AP-007-event-sourced-ledger/index.md --research patterns/AP-007-event-sourced-ledger/research.json --sections sections.md --set pattern_scope=problem
D check patterns/AP-007-event-sourced-ledger/index.md
```

`write` refuses a citation of a source that was not recorded, a heading the template does not have, and a draft that cites nothing. A draft is no longer a placeholder, so the continuum's schema asks for what its type requires: `pattern_scope`, `implements` on a reference architecture, and the actor, outcome and success criteria of a use case. `write` refuses a draft without them, and `--set` supplies each. It keeps the template's deck tags and every section the agent left out, so their guidance is there for the reviewer. The result is marked as an AI draft in five places: `status: draft`, `portfolio.state: draft`, `provenance` (`ai-generated`, `ai-raw`), a `banner`, and a notice under the title. It ends with a Sources section listing each source with its URL and the date it was read.

Reviewing it is yours: check each claim against its source, correct it, then clear `portfolio.state` and set `provenance.review_state: human-reviewed`. The inventory counts drafts awaiting review, so none is forgotten.

Without a network, `D plan <placeholder> --recorded research.json` takes the web sources from a recorded file; the tests run the whole flow this way.

## Commands

| Command | Does |
|---|---|
| `portfolio.py discover [--json]` | Lists the signed documents |
| `portfolio.py inventory [--out FILE] [--format md\|html\|json] [--include-archived]` | Writes the inventory page |
| `portfolio.py check [--json]` | Validates signatures, series, duplicates and portfolio blocks; exit 1 on an error |
| `portfolio.py tag [--dry-run]` | Tags what needs conversion or is proposed for deprecation |
| `portfolio.py tag PATH... --state STATE [--reason TEXT]`, or `--clear` | Sets or clears a state by hand |
| `portfolio.py sign [--dry-run]` | Adds `kind` to legacy documents |
| `portfolio.py archive [--dry-run] [--rewrite-links] [--stub]` | Archives what is marked `archive` |
| `portfolio.py backlog FILE [--dry-run] [--update] [--candidates] [--default-type TYPE] [--report FILE] [--json]` | Matches a backlog and makes placeholders |
| `draft.py plan PLACEHOLDER [--recorded FILE]` | Gathers the repository's research and writes `research.json` |
| `draft.py add-source research.json --url --title --excerpt [--publisher] [--accessed]` | Records a web source |
| `draft.py write PLACEHOLDER --research FILE --sections FILE [--set KEY=VALUE ...] [--dry-run]` | Assembles the cited, marked draft |
| `draft.py check DRAFT [--research FILE]` | Confirms the markings and the citations |

Every binding is in [the portfolio's inputs.toml](../skills/portfolio/inputs.toml).

## Why it works this way

- Only front matter counts, because names collide and a signature is a decision someone made. The cost is a one-off `sign` for legacy pages and a `kind` line in every template.
- A candidate is a page with `kind: candidate`, not a row in a register, so the rule that only front matter counts has no exception. It mints no identifier until it is committed.
- The archive is a binding, and pages keep their place in the tree below it, so the archive of a large repository stays navigable and two pages with the same folder name in different places never collide.
- Archiving moves and never deletes, and reports every link it breaks. Rewriting them is one flag, because some repositories prefer to fix links by hand in the same review.
- The backlog acts only on what is unambiguous. A wrong placeholder costs more to find and remove than an ambiguous row costs to resolve by hand.
- The draft skill's script does the parts that must be exact (numbering sources, resolving citations, the markings, the template) and the agent does the reading and the writing.
