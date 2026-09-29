<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Worked example: chaining patterns

[PAT-910 Staff Assistant](./PAT-910-staff-assistant/index.md) is a wider pattern whose scenario calls another. Its step 2 has `PAT-900 S1` in the Uses column, so that one step stands for the whole of S1 of the [knowledge-retrieval](../knowledge-retrieval/index.md) example. Its step 4 is `TBD confirmed action`, a child flow not yet written.

```sh
python <skills>/model/bin/model.py chain PAT-910-staff-assistant/index.md
python <skills>/model/bin/model.py validate PAT-910-staff-assistant/index.md
```

`chain` prints the tree: step 2 calls S1 of PAT-900, whose status is `Example`, and step 4 is open. `validate` warns on the open child flow and passes. `model.toml` binds `patterns_root` to the examples folder, and PAT-900 is found there by its H1, since no folder is named for it.

Set PAT-910's `status` to `Approved` and `validate` fails on the approval gate: an approved pattern cannot rest on PAT-900, whose status is not an approved one, nor on a `TBD`.

The example keeps only the tables chaining reads. A real pattern carries its diagram, and `publish.py` then builds a walkthrough whose step 2 drills into PAT-900's.
