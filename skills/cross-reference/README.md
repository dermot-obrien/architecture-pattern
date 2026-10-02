<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# cross-reference

An agent skill for referring to another catalogue's architecture identifiers without clashes. A bare `ABB-024` means this catalogue; `ops:ABB-024` means the ABB-024 of the catalogue whose short code is `ops`.

It keeps two registers, a namespace register of short codes and an identifier register for single foreign identifiers, validates them, resolves references to URLs, checks every reference in a repository, and ships two Docusaurus plugins: one turns references into links, the other gives every identifier a stable address (`id/<ID>/`) and publishes a manifest (`id/index.json`) other catalogues check against.

It needs Node 18 or newer and nothing else: no other skills and no npm packages.

| File | What it is |
|---|---|
| [SKILL.md](SKILL.md) | What an agent reads |
| [references/specification.md](references/specification.md) | The rules, the registers, resolution, the manifest |
| [inputs.toml](inputs.toml) | The bindings the skill needs from a workspace |
| `scripts/xref.cjs` | `validate`, `list`, `resolve` and `check` |
| `scripts/check.cjs` | The post-install check |
| `scripts/docusaurus/` | `remark-xref.cjs` and `id-routes.cjs` |
| [examples/catalogue](examples/catalogue/README.md) | Three catalogues, worked |

Tests: `node --test skills/cross-reference/tests/*.test.cjs` from the repository root.
