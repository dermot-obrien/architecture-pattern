<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.1.0] - 2026-10-18

### Added

- `portfolio.py discover`: every architecture pattern, reference architecture, collaboration, use case and candidate, found by the signature in its front matter and never by file or folder name. Legacy documents with `pattern_type` or `document_type: use-case` and no `kind` are found and reported.
- `portfolio.py inventory`: the summary page of every document with links and summaries, then the candidates, what needs attention and, with `--include-archived`, the archive. Markdown, standalone HTML or JSON, with no date, so regenerating an unchanged portfolio changes nothing. `linkBase` links identifiers to the cross-reference skill's stable addresses.
- `portfolio.py check`: signatures, series, duplicate identifiers and the `portfolio` block.
- `portfolio.py tag`: sets `needs-conversion` on a document missing one of its type's four parts and clears it once in form; sets `proposed-deprecation` from status, `superseded_by`, `valid_until` or age; sets or clears a state by hand. Never overrides a state a person set.
- `portfolio.py archive`: moves documents marked `archive` into `archiveDir` with `git mv`, keeping their place in the tree, marks them `archived` and `unlisted`, and reports the links the move breaks; `--rewrite-links` rewrites them and `--stub` leaves a page saying where it went. Idempotent, with `--dry-run`. Never deletes.
- `portfolio.py sign`: adds `kind` to legacy documents.
- `portfolio.py backlog`: matches a Markdown table, bullet list or CSV of pattern names against the portfolio, exactly, fuzzily or by identifier, reports what matched, what is new and what is ambiguous, makes committed new rows into placeholders from the type's template with the next identifier in its series, promotes a committed candidate, and with `--update` and `--candidates` carries priorities onto matched documents and notes uncommitted rows as candidates.
- A fallback collaboration template, used only when neither the repository nor the pattern skill provides one.
