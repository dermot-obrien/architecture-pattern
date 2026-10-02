<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Examples

Every example uses invented identifiers and names, so none can be mistaken for a real catalogue.

| Example | What it shows | Where |
|---|---|---|
| Quick start PAT-001 Order Intake | The smallest useful problem-scope pattern: three local boxes, two interfaces, one scenario with a declared Start and Finish, deck tags, published with its view, walkthrough, deck and PDF | [quick-start.md, step 4](quick-start.md#4-write-a-small-pattern) |
| Quick start PAT-002 Checkout | A composite pattern: one step runs PAT-001 S1 through a two-pair role binding, one step is an open participating pattern, and the approval gate | [quick-start.md, step 9](quick-start.md#9-compose-a-pattern-that-runs-another) |
| PAT-900 Knowledge Retrieval | A full domain-scope pattern: eight catalogued building blocks, seven interfaces with protocols, error handling and NFRs, two scenarios, controls, variation points, decisions and risks, and its committed diagram, views and render records | [skills/pattern/examples/knowledge-retrieval](../skills/pattern/examples/knowledge-retrieval) |
| PAT-910 Staff Assistant | A composite pattern over PAT-900: a participation step bound `PAT-900 S1 (ABB-908=03)`, joining at PAT-900 S1's declared Start and Finish, and one open participating pattern. Tables only, no diagram | [skills/pattern/examples/composite](../skills/pattern/examples/composite) |
| The template | Every section, with the guidance for each in HTML comments | [skills/pattern/assets/template.md](../skills/pattern/assets/template.md) |
| UC-900 Map a business use case to an industry reference model | A use case from the `use-case` skill: six local participants, five interactions, a main flow and a set-up flow, with its diagram, view, render record and extracted model | [skills/use-case/examples/uc-900](../skills/use-case/examples/uc-900), and [use cases](use-cases.md#the-worked-example) |

## PAT-900 Knowledge Retrieval

Each example folder carries its own binding, `model.toml`, so it is self-contained; a repository would normally use one `.agents/skill-bindings.toml` at its root. Its binding reads `ABB-` and `SBB-` building blocks and `IF-` interfaces, where the quick start's reads the template's `COMP-`.

To check it agrees with its diagram, and that its views are current, from its folder:

```
python <skills>/model/bin/model.py validate index.md --against components.drawio
python <skills>/model/bin/model.py stamp --check components.svg
```

To regenerate every output with draw.io desktop, in bash, `./run.sh` (see [commands](commands.md#the-worked-examples-runsh)). The folder's [README](../skills/pattern/examples/knowledge-retrieval/README.md) explains each file and why the generated ones are committed.

The example predates the walkthrough: it embeds one image per scenario rather than linking `scenarios.html`, and it does not declare its diagram in front matter, so `publish.py` does not pick it up. It remains the reference for a complete, wide-scope document.

## PAT-910 Staff Assistant

From `skills/pattern/examples`:

```
python <skills>/model/bin/model.py composition composite/PAT-910-staff-assistant/index.md
python <skills>/model/bin/model.py validate composite/PAT-910-staff-assistant/index.md
```

`composition` shows step 2 running S1 of PAT-900, joined at its declared start and finish and bound `ABB-908=03`, and step 4 open. `validate` passes with one warning. Its binding sets `patterns_root = ".."`, and PAT-900 is found by its H1, since no folder is named for it. Set its `status` to `Approved` and `validate` fails on the approval gate. The folder's [README](../skills/pattern/examples/composite/README.md) walks through it.

CI runs both examples on every pull request; see [.github/workflows/ci.yml](../.github/workflows/ci.yml).
