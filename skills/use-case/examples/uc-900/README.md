<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Worked example: UC-900, a use case

A use case written from [the use case template](../../assets/template.md), published with the same tools as a pattern. The identifiers are invented for the example and the design is illustrative.

| File | What it is | Made by |
|---|---|---|
| `index.md` | The document, which is also the model (Participants, Interactions, Scenarios) and the deck | An author |
| `model.toml` | Binds the template's tables, with local participants coloured by Kind | An author |
| `components.drawio` | The diagram, arranged by hand after `model emit`, kept in step by `model sync` | `model emit`, then `model sync` |
| `components.svg`, `.render.json` | The view, and the record that it is current | `model render` |
| `scenarios.html` | The animated walkthrough of S1 and S2 | `model animate` |
| `model.json` | What the document extracts to | `model extract` |

Publish it from this folder with `python <skills>/pattern/scripts/publish.py .`, where `<skills>` is the folder the skills are installed in.
