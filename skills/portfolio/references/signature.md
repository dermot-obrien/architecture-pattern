# The portfolio signature

This is the front matter the portfolio reads. It is part of the continuum's front matter standard (architecture-continuum, `standards/standard-frontmatter.md`, §2.9, §6.17 and §6.23), and the continuum's schemas validate it. The two are kept the same: a change here is a change there.

## What makes a document a pattern

Discovery reads the YAML front matter at the top of a Markdown file, and nothing else.

| `kind` | `pattern_type` | Series | What it is |
|---|---|---|---|
| `pattern` | `architecture-pattern` | `AP-NNN` | Technology-agnostic: its boxes are ABBs or local roles |
| `pattern` | `reference-architecture` | `RA-NNN` | Technology-specific: its boxes are mainly SBBs and products; `implements` names the architecture patterns it applies |
| `pattern` | `collaboration` | `CL-NNN` | Participants working together, with lighter rules: its boxes need not be catalogued building blocks, and it has no `implements` or `implemented_by` |
| `use-case` | | `UC-NNN` | What a solution does for someone, before anyone designs how |
| `candidate` | | none | A possible pattern, noted but not formally one yet |

A repository may bind other series under `[suite.pattern.types.<type>] idSeries`, and `[suite.use-case] idSeries`; the check holds each document to its type's bound series.

Every other `kind` of the continuum (an ABB, a capability, a decision record) is not a pattern, whatever its headings say. A page with no front matter, or front matter with no `kind`, is not discovered, whatever its file or folder is called.

### Legacy documents

A document written before the signature carried `kind` is still a deliberate signature, and is found and reported as legacy:

- `pattern_type` set to one of the three pattern types, and no `kind`
- `document_type: pattern` or `document_type: use-case`, and no `kind`; a pattern's type then follows from its identifier's series

Its identifier, when its front matter has none, is taken from the start of its first heading. `portfolio.py sign` writes `kind` (and `id`) into the front matter, after which it is an ordinary document.

## Candidates

A candidate is a light page of its own, so that only front matter counts. It is not formally a pattern, so it does not carry `kind: pattern`, mints no identifier, and the pattern schema's required fields do not apply to it.

```yaml
---
kind: candidate
title: Event-sourced ledger
candidate_type: architecture-pattern   # optional: architecture-pattern, reference-architecture, collaboration or use-case
description: "Keep a ledger as an append-only log of events, and derive balances from it."
created: 2026-07-07                    # optional
owner: Finance platform team           # optional
portfolio:                             # optional: priority, target_quarter, committed, backlog_ref
  priority: medium
  target_quarter: "2027-Q2"
---
```

An `id`, when a candidate has one, is a kebab-case slug, never a series identifier. A candidate carries no `portfolio.state` but one: `needs-conversion`, which the convert skill sets on a source it cannot convert yet, such as a picture awaiting the agent. It becomes a pattern by being converted, or by being promoted from the backlog when it is committed.

## The portfolio block

Optional on every pattern, use case and candidate. Absent, the document is live and nothing is pending.

```yaml
portfolio:
  state: placeholder                 # see below; absent means live
  priority: high                     # high, medium, low or none
  target_quarter: "2027-Q1"          # YYYY-Qn; quote it
  committed: true                    # true or false
  reason: "Why the state was set"
  since: 2026-10-18                  # when the state was set
  backlog_ref: "BL-12"               # the backlog row or ticket it came from
  archived_from: patterns/AP-004-old-gateway   # set by archive
```

| `state` | Set by | Means | Next |
|---|---|---|---|
| (absent) | | Live; nothing pending | |
| `placeholder` | `backlog` | Committed, with no content yet: the template, titled | The `draft` skill writes a draft |
| `draft` | the `draft` skill | An AI-generated draft from research, citing its sources, awaiting review | A person reviews it, then clears the state |
| `needs-conversion` | `tag` | Not in the form its type expects: a diagram, the boxes, the links and the scenarios | The convert skill; `tag` clears it once in form |
| `proposed-deprecation` | `tag`, or a person | Its status, `superseded_by`, `valid_until` or age says it may be retired | People agree, or clear the state |
| `archive` | a person | Deprecation agreed: move it out of the main tree | `archive` moves it |
| `archived` | `archive` | Moved to the archive folder, history kept | |

`tag` never overrides `placeholder`, `draft`, `proposed-deprecation`, `archive` or `archived`: those are set deliberately. Proposed deprecation wins over needs-conversion, since nothing is gained by converting what is being retired.

`portfolio.state` and the envelope's `status` are different things. `status` is the document's own review lifecycle (draft, proposed, accepted, active, deprecated, superseded, retired). `portfolio.state` is what the portfolio is doing about it.

## The four parts

Every type shares the same essence, and `tag` checks for it. Each part is an H2 heading, optionally numbered (`## 3. Building Blocks`); a table inside an HTML comment does not count.

| Part | Architecture pattern, reference architecture | Collaboration, use case | Holds |
|---|---|---|---|
| diagram | `## Diagram` | `## Diagram` | The diagram |
| boxes | `## Building Blocks` | `## Participants` | A table, with at least one row |
| links | `## Interfaces` | `## Interactions` | A table, with at least one row |
| scenarios | `## Scenarios` | `## Scenarios` | At least one `###` scenario or a table |

A repository whose template names them otherwise binds `[suite.portfolio.form.<type>]`, for example `boxes = ["Components", "Building Blocks"]`.

## Site fields

The continuum's standard also names the fields a site reads, which the portfolio sets or leaves alone:

| Field | Set by the portfolio | Means |
|---|---|---|
| `unlisted: true` | on archive | Built, but out of the sidebar, search and sitemap |
| `moved_to` | on an archive stub | The page now lives there; a stub carries no `kind`, so it is never discovered |
| `deck_publish`, `deck_id` | never | markdown-deck publishes the page as a deck, under that identifier |
| `banner` | never; the `draft` skill sets it on a draft | A notice shown at the top of the page: `{ tone: info, text: "..." }` |
