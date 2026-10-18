---
name: draft
description: Write a first draft of a placeholder architecture pattern, reference architecture, collaboration or use case from research, in the repository's proper template, citing every source. Gathers research in the repository (related patterns, candidate notes, passages that use the pattern's terms) and online, records each source, writes the template's sections with numbered citations, and marks the result as an AI-generated draft for review, with draft status, provenance and a review banner. Use when asked to draft, flesh out, research or fill in a placeholder pattern, or a pattern the portfolio skill created from a backlog.
license: CC-BY-4.0 AND Apache-2.0. Content under CC BY 4.0, code under Apache-2.0; see LICENSE and NOTICE.
compatibility: Python 3.11+. Standard library only. Requires the portfolio skill, installed beside it, to read and write front matter and find related documents. Online research uses the agent's own web search and fetch tools; without them, or with --recorded, it works from the repository and a recorded research file.
metadata:
  version: "0.1.0"
  homepage: https://github.com/dermot-obrien/architecture-pattern
  x-skill-requires: "pkg:generic/dermot-obrien/architecture-pattern/portfolio ^0.1.0"
---

# Draft

A placeholder is a promise with nothing behind it yet. This skill gives it a first draft that a person can review: researched, in the proper template, every claim tied to a source, and plainly marked as written by AI.

People start from the guide at https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/portfolio.md#drafting-a-placeholder.

## Step 0

Run `python <skills>/draft/scripts/check.py` from the workspace root. It confirms the portfolio skill is installed and lists the placeholders waiting for a draft. Stop if it fails.

Only a document with `portfolio.state: placeholder` (or `draft`, to redraft) is drafted. Never draft over a reviewed document: `write` refuses one.

## The flow

`<d>` is `python <skills>/draft/scripts/draft.py`, run from the workspace root.

1. Plan. `<d> plan <placeholder>` writes `research.json` beside the placeholder. It holds the template's sections, suggested queries, and the repository's sources, numbered `R1`, `R2`, and so on: related documents found by signature, the candidate's notes when it was promoted from one, and passages that use the pattern's terms. Read each one.
2. Research online. Search for the suggested queries and your own, read the pages, and record each source you will draw on: `<d> add-source research.json --url <url> --title "<title>" --excerpt "<the passage you rely on>" --publisher "<publisher>"`. It prints the source's number, `W1`, `W2`, and so on. Prefer primary sources: standards, specifications, the original description of a pattern, a vendor's own documentation for a reference architecture. Record only what you read.
3. Write the sections. In a scratch file, write a `## Heading` block for each template section you can support from the research, using the template's own headings and table columns. Cite with `[R1]` or `[W2]` after each claim drawn from a source. Leave a section out rather than invent it: its template guidance stays for the reviewer. The method, with what each section needs, is in [references/method.md](references/method.md).
4. Assemble. `<d> write <placeholder> --research research.json --sections <file> --set pattern_scope=<scope> --dry-run`, then without `--dry-run`. A draft is no longer a placeholder, so it needs what its type requires: `pattern_scope` (problem, domain, capability-area, platform, hosting-profile or epic), `implements` on a reference architecture, and `primary_actor`, `supports_outcome` and `success_criteria` on a use case. Pass each with `--set`, as in `--set implements=[AP-001]`; ask the user when the research does not settle it. It refuses a citation that names no recorded source, a heading the template does not have, a missing required field, and a draft that cites nothing. It keeps the template's deck tags and every section you did not write.
5. Check. `<d> check <placeholder> --research research.json`. Then run the pattern skill's own checks on the result, so the diagram generates from the tables.
6. Tell the user what you drafted, which sections you left for them, and which claims rest on a single source.

## What the draft carries

`write` sets these, and `check` confirms them:

| Marking | Value |
|---|---|
| `status` | `draft` |
| `portfolio.state` | `draft`, with the reason and the date |
| `provenance` | `origin: ai-generated`, `review_state: ai-raw`, `authored_by`, `authored_at`, and the backlog reference as `task_ref` |
| `banner` | a warning that it is an AI-generated draft for review |
| `references` | each web source as `doc`, each repository source as `source` |
| A notice under the title | the same warning, for a site that shows no banner |
| `## Sources` | every cited source with its title, publisher, URL and the date it was read, and a link definition so each `[W1]` is a link |

The reviewer clears `portfolio.state` and sets `review_state: human-reviewed` when they accept it. Never clear those markings yourself.

## Offline

`<d> plan <placeholder> --recorded <file>` takes the web sources from a recorded research file instead of searching online. Use it when there is no network, and in tests; the tests in `tests/` run the whole flow this way.

## Rules

- Every claim from research cites its source. Never cite a source you did not read, and never invent a URL.
- Write in the template's form: its headings, its table columns, its identifier conventions. A drafted architecture pattern names no products; a reference architecture does.
- Keep it generic where the pattern is generic, and never copy a source's text at length: summarise and cite.
