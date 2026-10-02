<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Worked example: three catalogues

`ex` is this catalogue. `ops` is another catalogue with a published site, so its identifiers need only its namespace row. `lab` has no site, so each of its identifiers that is referenced has a row in the identifier register.

From this folder:

```bash
node ../../scripts/check.cjs
node ../../scripts/xref.cjs list
node ../../scripts/xref.cjs resolve ex:BB-001 ops:BB-024 lab:BB-007 lab:BB-099
node ../../scripts/xref.cjs check --offline
```

`lab:BB-099` doesn't resolve, because the lab has no site and no row for it. In `docs/order-intake.md` it sits in inline code, so `check` ignores it.
