---
name: cross-reference
description: Refer to another catalogue's architecture identifiers, such as its building blocks, patterns or capabilities, without clashes. A bare ABB-024 means this catalogue; ops:ABB-024 means the ABB-024 of the catalogue whose short code is ops. Keeps the namespace register of short codes and the register of individual foreign identifiers, validates both, resolves a reference to a URL, checks every reference in a repository, and ships Docusaurus plugins that turn references into links and give every identifier a stable address and a manifest. Use when asked to reference, link or cite a building block, pattern or identifier from another repository, domain, team or site; to register a namespace code or a foreign identifier; to check cross-repository references; to give identifiers stable URLs; or when two catalogues' identifiers clash.
license: CC-BY-4.0 AND Apache-2.0. Content under CC BY 4.0, code under Apache-2.0; see LICENSE and NOTICE.
compatibility: Node 18+. No other skills and no npm packages. The Docusaurus plugins work with Docusaurus 3; the registers, CLI and check work with any static site generator or none.
metadata:
  version: "0.1.1"
  homepage: https://github.com/dermot-obrien/architecture-pattern
---

# Cross-reference

An identifier is unique only inside the catalogue that minted it. Once catalogues build on each other's blocks, a reference has to say whose block it means. This skill writes and checks those references, and turns them into links when a site is built.

## The convention

| Written as | Means |
|---|---|
| `ABB-024` | ABB-024 in this catalogue |
| `ops:ABB-024` | ABB-024 in the catalogue whose code is `ops` |

The code and the identifier are separated by a colon, with no spaces. This is a compact URI (CURIE, W3C CURIE Syntax 1.0). The code names the owning catalogue, never a host or a page, so a catalogue can move without breaking references. Write a reference as text, `ops:ABB-024`, or as the target of a Markdown link whose text is the block's name. Give the name with the identifier the first time it appears.

Never write a full URL to another catalogue's page in place of a reference, and never renumber an identifier to carry its catalogue (ABB-OPS-024).

## Step 0, before anything else

Run the post-install check from the workspace root, and stop on a problem:

```bash
node <skills>/cross-reference/scripts/check.cjs
```

It reads `[suite.cross-reference]` in `.agents/skill-bindings.toml`, the contract in `inputs.toml` beside this file. Paths there are relative to the bindings file, so a registers folder at the workspace root is `../registers`:

| Binding | Used for |
|---|---|
| `namespaces` | Required. The namespace register |
| `external` | The identifier register |
| `schemes` | A CSV with a `prefix` column: this catalogue's identifier prefixes, which a code may not equal |
| `localManifest` or `localMap` | This catalogue's identifiers and their pages, as JSON or as a module exporting a function |
| `scan`, `skip` | Where `check` looks for Markdown, and directory names it never enters |

## The rules

A namespace code is 2 to 6 lower case letters or digits, starting with a letter. It is unique, and it is never one of the identifier prefixes (`abb:ABB-024` would read as a type). It is never renamed or reused. The full specification, with both registers' columns, the resolution order, what a site publishes and the manifest format, is in [references/specification.md](references/specification.md). Read it before changing a register.

## Tasks

| Asked to | Do |
|---|---|
| Reference another catalogue's identifier | Find its code with `xref.cjs list`. Write `code:ID`. If it doesn't resolve (`xref.cjs resolve code:ID`), add a row to the identifier register, with the page's exact URL from the user, never a guess |
| Register a catalogue | Add one row to the namespace register with a code that follows the rules. Ask the user for the code if they haven't given one: codes are shared, so the catalogue's owner agrees it |
| Register one identifier | Add a row to the identifier register: namespace, id, name, repository, url |
| Check references | `xref.cjs check`. Report each error with the file it is in. `--offline` skips other catalogues' manifests |
| Give identifiers stable addresses | Add the `id-routes` plugin to the site (below). Every build then publishes `id/<ID>/` and `id/index.json` |

```bash
node <skills>/cross-reference/scripts/xref.cjs validate
node <skills>/cross-reference/scripts/xref.cjs list
node <skills>/cross-reference/scripts/xref.cjs resolve ops:ABB-024
node <skills>/cross-reference/scripts/xref.cjs check [--offline]
```

Exit 0 is clean, 1 is problems, 2 is a usage or configuration error.

## Docusaurus

Two plugins, wired in `docusaurus.config.js`. Both take this catalogue's own identifier map as an option, so the skill never needs to know how the catalogue finds its pages.

```js
const skill = '.agents/skills/cross-reference/scripts/docusaurus';
const {buildLinkMap, urlFor} = require('./src/my-identifier-map');   // the catalogue's own

remarkPlugins: [[require(`./${skill}/remark-xref.cjs`), {
  namespaces: 'registers/identifier-namespaces.csv',
  external: 'registers/external-identifiers.csv',
  schemes: 'registers/identifier-schemes.csv',
  localUrlFor: urlFor,
}]],
plugins: [[require.resolve(`./${skill}/id-routes.cjs`), {
  localMap: buildLinkMap,
  namespaces: 'registers/identifier-namespaces.csv',
}]],
```

Put `remark-xref` before any plugin that links bare identifiers. A reference that can't resolve stays plain text with a build warning, so it never breaks the build's link check.

## What never to do

- Don't invent a code or a URL. Codes are agreed with the catalogue's owner; URLs come from the owning site.
- Don't register this catalogue's own identifiers in the identifier register. They live in the catalogue's own registers.
- Don't edit an installed copy of this skill. Change it where it is mastered and reinstall.
