---
name: portfolio
description: Keep a repository's architecture patterns current as a managed portfolio. Finds every architecture pattern, reference architecture, collaboration, use case and candidate by the signature in its front matter (never by file or folder name), writes an inventory page of all of them with links and summaries, tags the ones that need conversion or are proposed for deprecation, archives the ones marked for archive with git mv so history is kept, and matches a backlog of pattern names against the portfolio, turning committed rows with no match into placeholders. Use when asked to list, inventory, audit, clean out, tag, deprecate or archive patterns, to generate a pattern catalogue or portfolio page, or to turn a backlog or roadmap of patterns into placeholder documents.
license: CC-BY-4.0 AND Apache-2.0. Content under CC BY 4.0, code under Apache-2.0; see LICENSE and NOTICE.
compatibility: Python 3.11+ and git. Standard library only. Placeholders are written from the pattern skill's and the use-case skill's templates, so install those beside it, or bind templates of the repository's own.
metadata:
  version: "0.1.0"
  homepage: https://github.com/dermot-obrien/architecture-pattern
  x-skill-requires: "pkg:generic/dermot-obrien/architecture-pattern/pattern ^0.15.0, pkg:generic/dermot-obrien/architecture-pattern/use-case ^0.4.0"
---

# Portfolio

A repository collects patterns faster than anyone retires them. This skill keeps the collection current: it knows what is there, says what needs work, and moves out what is no longer wanted, without losing history.

People learning the skill start from the guide at https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/portfolio.md.

## Step 0, before anything else

From the workspace root, run the post-install check and stop on an error:

```bash
python <skills>/portfolio/scripts/check.py
```

It prints the binding file, the folders scanned, the archive folder and where the inventory goes, and validates every signed document. Every path comes from `[suite.portfolio]` of `.agents/skill-bindings.toml`, the contract in `inputs.toml` beside this file. With nothing bound, the whole repository is scanned, the archive is `archive/` and the inventory is printed.

## The signature

A document is in the portfolio only when its front matter says so. Never decide from a file name, a folder name, a heading or a tag: names collide, and the signature is deliberate.

| Front matter | Is |
|---|---|
| `kind: pattern`, `pattern_type: architecture-pattern` | An architecture pattern, `AP-NNN` |
| `kind: pattern`, `pattern_type: reference-architecture` | A reference architecture, `RA-NNN` |
| `kind: pattern`, `pattern_type: collaboration` | A collaboration, `CL-NNN` |
| `kind: use-case` | A use case, `UC-NNN` |
| `kind: candidate` | A possible pattern, not formally one yet, with no identifier |

The portfolio's own fields sit in one optional `portfolio:` block: `state`, `priority`, `target_quarter`, `committed`, `reason`, `since`, `backlog_ref` and `archived_from`. The full specification, with every value and what sets it, is in [references/signature.md](references/signature.md). It is the continuum's front matter standard, so the same documents pass the continuum's check.

A document with `pattern_type` and no `kind`, or with `document_type: pattern` or `use-case`, predates the signature. It is found and reported as legacy; `portfolio.py sign` adds the `kind`.

## Commands

Run from the workspace root. `<p>` is `python <skills>/portfolio/scripts/portfolio.py`.

| Asked to | Run |
|---|---|
| List what is there | `<p> discover` |
| Write the inventory page | `<p> inventory` (to the bound page), or `--out portfolio.html` |
| Validate signatures and portfolio blocks | `<p> check` |
| Tag what needs conversion or deprecation | `<p> tag --dry-run`, then `<p> tag` |
| Mark one document by hand | `<p> tag <path> --state archive --reason "Agreed at review"` |
| Archive what is marked for archive | `<p> archive --dry-run`, then `<p> archive --rewrite-links` |
| Add `kind` to legacy documents | `<p> sign` |
| Match a backlog and make placeholders | `<p> backlog <file> --dry-run`, then `<p> backlog <file>` |

Every command that writes has `--dry-run`, which prints exactly what a real run does. Show the user the dry run before the real one, unless they asked for it to just happen.

## The lifecycle

1. `tag` sets `needs-conversion` on a document that lacks one of the four parts its type expects (a diagram, the boxes table, the links table, scenarios), and clears it once the document is in form. Send such documents to the convert skill. It sets `proposed-deprecation` when the status is deprecated, superseded or retired, `superseded_by` is set, `valid_until` has passed, or the document is older than `staleAfterDays`. It never overrides a state a person set.
2. A proposal to deprecate is agreed by people, not by this skill. When it is, a person sets `portfolio.state: archive`, by hand or with `tag <path> --state archive`.
3. `archive` moves each such document, with its folder when the folder holds nothing else signed, to the same place under `archiveDir`, with `git mv` where git tracks it, and marks it `archived` and `unlisted`. Nothing is deleted. A second run does nothing.
4. Links the move would break are always reported. Pass `--rewrite-links` to rewrite them, inbound and outbound, or `--stub` to leave a page saying where it went. Never leave a broken link unreported.
5. `inventory` again, so the page shows the result. On a site built by the continuum's workspace skill, `regenerate` does this before every build.

## The backlog

The backlog is a Markdown table, a bullet list or a CSV of pattern names, each optionally with a type, committed, priority, quarter, owner and reference. The forms are in [references/backlog.md](references/backlog.md).

The report says, for each row, whether it matched exactly (by name or identifier), matched fuzzily (one close name and no rival), is ambiguous (several close names, or one only somewhat close) or is new. Act only on what is unambiguous:

- A committed new row becomes a placeholder: the type's template, under the type's `outputDir`, with the next identifier in its series and `portfolio.state: placeholder`.
- A committed row that matches a candidate promotes it: the candidate moves with `git mv` to where the placeholder goes, and its notes are kept at the end.
- An ambiguous row is never acted on. Show the user the options and ask which is meant, or whether it is new.
- `--update` copies a matched row's priority, quarter and commitment onto its document; `--candidates` makes uncommitted new rows into candidate pages.

A placeholder is filled by the `draft` skill, which writes a cited draft from research.

## Rules

- Never discover, match or mint by file or folder name. Identifiers come from front matter, and the next one is the highest in the series among signed documents, archived ones included, and the register, plus one.
- Never delete a document. Archive it.
- Never act on an ambiguous backlog row.
- Keep everything generic: no organisation names, hosts or brands in what you write.
