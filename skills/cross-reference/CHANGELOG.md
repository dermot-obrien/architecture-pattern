<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.1.1] - 2026-10-03

### Fixed

- Paths in `[suite.cross-reference]` are relative to the bindings file, as every other skill's are, not to the workspace root. A workspace binding `namespaces = "registers/..."` must now say `"../registers/..."`. Command-line flags stay relative to the working directory.

## [0.1.0] - 2026-10-03

### Added

- The `cross-reference` skill: references to another catalogue's identifiers as `code:ID` compact URIs, with a bare identifier always meaning this catalogue.
- The namespace register (short codes of 2 to 6 characters, unique, never an identifier prefix) and the identifier register (one foreign identifier and its exact URL), both validated on load with a reason for every skipped row.
- `scripts/xref.cjs`: `validate`, `list`, `resolve` and `check`, which ignores fenced and inline code and checks other catalogues against their manifests.
- `scripts/check.cjs`, the post-install check, and `inputs.toml`, the `[suite.cross-reference]` bindings.
- Docusaurus plugins: `remark-xref.cjs`, which turns references into links with a tooltip, and `id-routes.cjs`, which publishes `id/<ID>/` redirects and the `id/index.json` manifest. Both take the catalogue's own identifier map as an option.
- `references/specification.md` and a worked example of three catalogues.
