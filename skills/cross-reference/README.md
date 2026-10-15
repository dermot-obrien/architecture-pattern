<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# cross-reference

An agent skill for referring to another catalogue's architecture identifiers without clashes. A bare `ABB-024` means this catalogue; `ops:ABB-024` means the ABB-024 of the catalogue whose short code is `ops`.

It keeps two registers, a namespace register of short codes and an identifier register for single foreign identifiers, validates them, resolves references to URLs, checks every reference in a repository, and ships two Docusaurus plugins: one turns references into links, the other gives every identifier a stable address (`id/<ID>/`) and publishes a manifest (`id/index.json`) other catalogues check against.

**Zero dependencies:** Node 18+ only, no other skills, no npm packages.

## Install

```bash
gh skill install dermot-obrien/architecture-pattern cross-reference
```

Or copy `skills/cross-reference/` into your agent's skills folder. See the [repository README](../../README.md#install) for all installation methods.

## Quick start

1. **Create the namespace register** (`registers/identifier-namespaces.csv`):
   ```csv
   code,name,site,manifest
   ops,Operations Architecture,https://arch.example.com/ops,https://arch.example.com/ops/id/index.json
   ```

2. **Create the identifier register** (`registers/external-identifiers.csv`):
   ```csv
   namespace,id,name,repository,url
   ops,ABB-024,Order Gateway,https://github.com/example/ops-arch,https://arch.example.com/ops/blocks/abb-024
   ```

3. **Bind in** `.agents/skill-bindings.toml`:
   ```toml
   [suite.cross-reference]
   namespaces = "../registers/identifier-namespaces.csv"
   external   = "../registers/external-identifiers.csv"
   ```

4. **Validate:**
   ```bash
   node .agents/skills/cross-reference/scripts/check.cjs
   node .agents/skills/cross-reference/scripts/xref.cjs validate
   ```

5. **Use in documents:**
   ```markdown
   This pattern uses ops:ABB-024 (Order Gateway) to receive orders.
   ```

6. **Check references:**
   ```bash
   node .agents/skills/cross-reference/scripts/xref.cjs check
   ```

See [SKILL.md](SKILL.md) for the complete workflow and [examples/catalogue](examples/catalogue/README.md) for a worked example.

## Documentation

| File | What it is |
|---|---|
| [SKILL.md](SKILL.md) | What an agent reads |
| [references/specification.md](references/specification.md) | The rules, the registers, resolution, the manifest |
| [inputs.toml](inputs.toml) | The bindings the skill needs from a workspace |
| `scripts/xref.cjs` | `validate`, `list`, `resolve` and `check` |
| `scripts/check.cjs` | The post-install check |
| `scripts/docusaurus/` | `remark-xref.cjs` and `id-routes.cjs` |
| [examples/catalogue](examples/catalogue/README.md) | Three catalogues, worked |

Tests: `node --test skills/cross-reference/tests/*.test.cjs` from the repository root (13 tests).

## Updating

To update after a new release:

1. **Delete the old installation:**
   ```bash
   rm -rf .agents/skills/cross-reference
   ```

2. **Reinstall:**
   ```bash
   gh skill install dermot-obrien/architecture-pattern cross-reference
   # Or copy from the repository again
   ```

3. **Verify:**
   ```bash
   node .agents/skills/cross-reference/scripts/check.cjs
   node --test .agents/skills/cross-reference/tests/*.test.cjs
   ```

4. **Check for new bindings:**
   ```bash
   cat .agents/skills/cross-reference/inputs.toml
   ```

**No dependencies to update** - this skill is standalone and has no npm packages or other skill dependencies.
