<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Cross-references

An identifier such as `ABB-024` is unique only inside the catalogue that minted it. When one platform's patterns use another platform's building blocks, a reference has to say whose block it means. The `cross-reference` skill gives every catalogue a short code and writes references as `code:ID`:

| Written as | Means |
|---|---|
| `ABB-024` | ABB-024 in this catalogue |
| `ops:ABB-024` | ABB-024 in the catalogue whose code is `ops` |

When a site is built, both forms of reference, in text or as a Markdown link target, become links into the owning catalogue. The full rules are in [the skill's specification](../skills/cross-reference/references/specification.md).

## What it needs

Node 18 or newer. No other skills, no npm packages, and no particular site generator: the registers, the CLI and the check work anywhere, and the two Docusaurus plugins are optional.

Install it like the other skills (see the [README](../README.md#install)), for example:

```bash
gh skill install dermot-obrien/architecture-pattern cross-reference
```

## Binding it

```toml
[suite.cross-reference]
namespaces    = "../registers/identifier-namespaces.csv"   # required
external      = "../registers/external-identifiers.csv"
schemes       = "../registers/identifier-schemes.csv"      # a CSV with a prefix column
localManifest = "../registers/local-ids.json"              # or localMap = "../src/id-map.js"
scan          = ["../docs"]                                 # default: the whole workspace
```

Paths are relative to the bindings file, as for the other skills.

`localManifest` or `localMap` tells the skill which identifiers your own catalogue publishes and where. A built site's `id/index.json` is a valid manifest. A module given as `localMap` exports a function returning a Map or an object of identifier to page.

Then run the post-install check from the workspace root:

```bash
node .agents/skills/cross-reference/scripts/check.cjs
```

## The two registers

The namespace register has one row per catalogue, with your own marked `self = yes`. A catalogue with a published site needs only its row: its identifiers resolve to `{base_url}id/{id}/`, or to its `url_template`.

The identifier register has one row per foreign identifier whose page can't be built from its code, such as a building block kept as a page in a wiki or a file in another repository. Its `url` wins over the namespace's template.

A code is 2 to 6 lower case letters or digits, starting with a letter, unique, and never one of your identifier prefixes. The register owner agrees each code, because every catalogue uses the same ones.

## Commands

```bash
node .agents/skills/cross-reference/scripts/xref.cjs validate
node .agents/skills/cross-reference/scripts/xref.cjs list
node .agents/skills/cross-reference/scripts/xref.cjs resolve ops:ABB-024
node .agents/skills/cross-reference/scripts/xref.cjs check --offline
```

`check` ignores fenced and inline code, so examples in documentation are never checked. Without `--offline`, it checks other catalogues' references against their manifests; an unreachable site is reported, not failed.

## Docusaurus

`remark-xref.cjs` turns references into links, with the block's name as a tooltip. `id-routes.cjs` writes `id/<ID>/` redirects for every identifier you publish, and the `id/index.json` manifest. Both take your catalogue's identifier map as an option; the wiring is in [SKILL.md](../skills/cross-reference/SKILL.md#docusaurus).

## Worked example

[skills/cross-reference/examples/catalogue](../skills/cross-reference/examples/catalogue/README.md) has three catalogues: one with its own site, one with a published site, and one with no site whose identifiers are registered one by one.
