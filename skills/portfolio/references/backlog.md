# Backlog forms and matching

`portfolio.py backlog <file>` reads a backlog of pattern names in any of three forms, matches each row against the portfolio, and reports. It writes only with no `--dry-run`, and only for unambiguous rows.

## A Markdown table

The first row names the columns, in any order and any case. Only a name column is required.

| Column | Also accepted | Values |
|---|---|---|
| Name | Pattern, Title, Pattern name | The pattern's name; an identifier such as `AP-003` matches that document |
| Type | Kind, Pattern type | `architecture pattern` or `AP`, `reference architecture` or `RA`, `collaboration` or `CL`, `use case` or `UC` |
| Committed | Commit, Commitment | yes, true, y, x or committed; anything else is not committed |
| Priority | Prio | high, medium, low or none; P1 to P4 are read as high to none |
| Quarter | Target quarter, Target | `2027-Q1`, also written `Q1 2027` |
| Owner | | The placeholder's owner |
| Ref | Reference, Ticket, Key, Issue | Kept as `portfolio.backlog_ref` |

```markdown
| Name | Type | Committed | Priority | Quarter | Ref |
|---|---|---|---|---|---|
| Zero-trust ingress | RA | yes | medium | 2027-Q2 | BL-6 |
```

A file may hold several tables; each is read.

## A bullet list

One item per pattern. A type may follow the name in brackets; other fields follow semicolons, as `key: value` or a bare word. A checked task box means committed.

```markdown
- Zero-trust ingress (reference architecture); committed; quarter: 2027-Q2
- [x] Event-driven ingestion
- Data mesh; P3
```

Brackets that do not name a type stay part of the name: `- Payments (cards and wallets)`.

## A CSV

A file ending `.csv`, with a header row using the table's column names.

## Matching

Names are compared after lower-casing, dropping a leading identifier, punctuation and the words `the`, `a`, `an`, `of`, `for`, `and`, `pattern`, `architecture`, `reference`, `with`, `to`, `in` and `on`. The score is half the characters' similarity and half the words', where two words differing only a little (ingest, ingestion) count as the same. A row whose type differs from a document's loses 0.15.

| Result | When | Action |
|---|---|---|
| exact | The names are equal, or the row names the document's identifier | none, or `--update`; promotes a candidate when committed |
| fuzzy | One document scores 0.85 or more, and no other is within 0.05 of it | as exact |
| ambiguous | Several names are equal or close, or the best scores between 0.65 and 0.85 | none: resolve by hand |
| new | Nothing scores 0.65 | a placeholder when committed; a candidate with `--candidates` |
| duplicate | The row repeats an earlier one | none |

Archived documents, and those marked for archive, are not matched. Their identifiers are still never reused.

Run the backlog again after editing it: rows already turned into placeholders now match them exactly, so nothing is made twice.
