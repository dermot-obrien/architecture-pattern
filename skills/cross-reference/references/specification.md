<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Cross-catalogue identifiers: specification

Version 0.1. How one architecture catalogue refers to another's identifiers, and how a site makes its own identifiers reachable.

## Terms

| Term | Meaning |
|---|---|
| Catalogue | A set of identifiers minted by one owner, such as the building blocks and patterns of one platform or domain. Usually one repository and one site |
| Identifier | A catalogue's name for one thing, `ABB-024`: a prefix in capitals, a hyphen, then letters, digits, dots or hyphens |
| Namespace code | A catalogue's short code, `ops` |
| Reference | A namespace code, a colon and an identifier: `ops:ABB-024` |

## 1. References

A bare identifier always means the catalogue the page belongs to. A reference to another catalogue's identifier is written `code:ID`, a compact URI under W3C CURIE Syntax 1.0, as text or as a Markdown link target. A reference in the catalogue's own code is allowed and means the same as the bare identifier, but it is checked.

## 2. Namespace codes

A code:

1. is 2 to 6 characters, lower case letters or digits, starting with a letter: `^[a-z][a-z0-9]{1,5}$`
2. is unique across every catalogue that shares the register
3. is not equal to any identifier prefix, lower-cased, so `abb:ABB-024` can't be misread as a type
4. is never renamed and never reused; a retired catalogue's code stays reserved

## 3. The namespace register

One row per catalogue. Every catalogue holds a copy, with `self = yes` on its own row.

| Column | Holds |
|---|---|
| `namespace` | The code |
| `name` | The catalogue's full name. Never written in a reference |
| `self` | `yes` for the catalogue holding this copy |
| `base_url` | The root of the catalogue's published site, with a trailing slash. Empty if it has none |
| `url_template` | Optional. A page URL built from `{base_url}` and `{id}`. Empty means `{base_url}id/{id}/` |
| `manifest` | Optional. Path of the catalogue's identifier manifest under `base_url`, normally `id/index.json` |
| `owner` | Who answers for the catalogue's identifiers |
| `notes` | Anything else |

## 4. The identifier register

One row per individual identifier in another catalogue whose page can't be built from its code: a catalogue with no site, or a page whose address doesn't follow from the identifier.

| Column | Holds |
|---|---|
| `namespace` | The owning catalogue's code. It must be in the namespace register and must not be `self` |
| `id` | The identifier as the owning catalogue mints it |
| `name` | Its name there, shown as the link's tooltip |
| `repository` | The repository or space that holds it |
| `url` | The absolute (http or https) URL of its page |
| `notes` | Anything else |

## 5. Resolution

1. A bare identifier resolves inside the catalogue.
2. A reference in the catalogue's own code resolves to its page inside the catalogue, and fails if the catalogue doesn't publish it.
3. A reference with a row in the identifier register resolves to that row's `url`.
4. Otherwise it resolves to the namespace's `url_template`, or `{base_url}id/{id}/`.
5. Otherwise it doesn't resolve: a build leaves it as plain text and warns, and a check reports it.

A code that isn't in the namespace register is not a reference, so ordinary text with a colon is never touched. Nothing is fetched to resolve a reference.

## 6. What a site publishes

A site that wants other catalogues to need only its namespace row publishes:

| Address | Content |
|---|---|
| `{base_url}id/{ID}/` | A redirect to the identifier's page. The lower-cased identifier redirects too |
| `{base_url}id/index.json` | The identifier manifest |

The manifest:

```json
{
  "namespace": "ops",
  "name": "Operations Platform",
  "base_url": "https://ops.example.org/architecture/",
  "url_template": "{base_url}id/{id}/",
  "count": 2,
  "ids": {
    "ABB-024": "blocks/abb-024-identity-provider/",
    "PAT-003": "patterns/pat-003-zero-trust-ingress/#scenarios"
  }
}
```

Each path in `ids` is relative to `base_url`. A catalogue keeps an identifier's address working after it is withdrawn, with a page saying so.

## 7. Checks

- Loading a register skips every row that breaks sections 2 to 4 and says why.
- A check of a repository finds every reference outside fenced and inline code. Own-code references must be published by the catalogue. Others must be in the identifier register, or published in the owning site's manifest. A reference that can't resolve is an error. An unreachable manifest is reported, not an error.

## 8. Moving and retiring

Moving a site changes its `base_url` in every copy of the namespace register; no reference changes. When an identifier changes owner, it stays with the namespace that minted it, and its old page points to the new owner's identifier. A retired catalogue keeps its row with an empty `base_url`, so its code stays reserved.
