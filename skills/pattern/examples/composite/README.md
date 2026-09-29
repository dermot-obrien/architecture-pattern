<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Worked example: a composite pattern

[PAT-910 Staff Assistant](./PAT-910-staff-assistant/index.md) is a composite pattern: its scenario steps run other patterns' flows. Its step 2 has `PAT-900 S1` in the Uses column, so that one participation step stands for the whole of S1 of the [knowledge-retrieval](../knowledge-retrieval/index.md) example, its participating pattern. Its step 4 is `TBD confirmed action`, an open participating pattern, not yet written.

PAT-900's S1 declares where its flow starts and finishes, as two paragraphs under its heading:

```markdown
Start: ABB-908 Model Gateway

Finish: ABB-901 Retrieval Service
```

PAT-910 has no Model Gateway of its own; its local `03 Assistant gateway` plays that role, which step 2 says with a role binding after the scenario key, `PAT-900 S1 (ABB-908=03)`. The step's Actor, 03, then corresponds to PAT-900's declared Start, and its Target, ABB-901, to the declared Finish.

```sh
python <skills>/model/bin/model.py composition PAT-910-staff-assistant/index.md
python <skills>/model/bin/model.py validate PAT-910-staff-assistant/index.md
```

`composition` prints the composition tree: step 2 runs S1 of PAT-900, whose status is `Example`, joined at its declared start and finish and bound `ABB-908=03`, and step 4 is open. `validate` warns on the open participating pattern and passes. `model.toml` binds `patterns_root` to the examples folder, and PAT-900 is found there by its H1, since no folder is named for it.

Set PAT-910's `status` to `Approved` and `validate` fails on the approval gate: an approved composite pattern cannot rest on PAT-900, whose status is not an approved one, nor on a `TBD`.

The example keeps only the tables composing reads. A real pattern carries its diagram: `model emit` or `sync` then draws a `Participating patterns` layer with a dashed region for PAT-900 round 03 and ABB-901 and one for the open participating pattern, labels step 2's arrow `[+] 2: PAT-900 S1`, and `publish.py` builds a walkthrough whose step 2 drills into PAT-900's.
