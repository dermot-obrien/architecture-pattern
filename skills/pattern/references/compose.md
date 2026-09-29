<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Compose patterns

Part of the `pattern` skill; [SKILL.md](../SKILL.md) summarises it.

A composite pattern is one whose scenario steps run other patterns' flows, its participating patterns. Compose in three ways:

- Top down. Sketch the composite pattern first, with each hard part an open participating pattern, `TBD`. Solve each as its own pattern, then replace the `TBD` with its id and scenario key.
- Bottom up. Compose approved patterns: each step that one of them already solves runs its scenario rather than repeating it.
- Both at once, as the work finds its level.

The notation borrows from two standards rather than inventing: a participation step is BPMN 2.0.2's call activity (UML's InteractionUse, a `ref` fragment, in a sequence diagram), a scenario's Start and Finish are its BPMN start and end events and its UML 2.5.1 ports, and a role binding, drawn as a dashed region round the boxes it binds, is UML 2.5.1's collaboration use.

Add a `Uses` column to the scenario's step table. On a participation step its value is the participating pattern's id and scenario key, `PAT-905 S1`, with anything after the key read as prose, or `TBD <name>` for an open participating pattern, not yet written. Leave it empty on every other step.

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 2 | 03 Order service | ABB-901 Payments hub | take payment | | PAT-905 S1 (01=03) |
| 3 | ABB-901 Payments hub | 01 Storefront | notify the customer | | TBD notification |

A participation step is one arrow in the composite pattern standing for the participating pattern's whole flow. Its Actor is where that flow enters and its Target where it leaves; both are required, and the Interface is optional.

Give each scenario a participating pattern will run a declared start and finish, on their own lines under its heading and before its steps table, each a box's id and name, as separate paragraphs:

```markdown
### S1 Payment capture

Start: 01 Order service

Finish: ABB-901 Payments hub
```

The Start must be the first step's actor and the Finish the last step's actor or target; `validate` holds them to it. A composite pattern then joins to them: the step's Actor must correspond to the Start and its Target to the Finish. Without them, the first step's actor and the last step's actor or target are used.

Boxes correspond through the step's role binding first: a parenthesised group of `id=id` pairs directly after the scenario key, participating pattern's box on the left, this pattern's on the right, as `PAT-905 S1 (01=03)` above. A binding is how a local box in one pattern is joined to a box in another; each box appears at most once on each side, and an open participating pattern cannot carry one. Otherwise boxes correspond when they share a catalogue id, or when a local box maps to it in Catalogue Mapping. A mismatch is a warning naming both boxes: bind them, or map the local box, rather than renaming it. List every participating pattern in Patterns Applied.

A participating pattern is the folder named `<ID>-<slug>` holding `index.md` under `patternsRoot`, else `outputDir`; with neither bound, the folders above the composite pattern are searched. Check the composition with:

```bash
python <model>/bin/model.py composition index.md    # the composition tree; --json for data
python <model>/bin/model.py validate index.md       # errors, warnings and a one-line summary
```

`validate` fails on a participating pattern or scenario that cannot be found, a binding that names a box that is not there, a declared Start or Finish the steps do not bear out, and a cycle, and warns on each open participating pattern and on a join it cannot establish. The approval gate: once the composite pattern's front matter `status` is one of `approvedStatuses`, every participating pattern at any depth must be approved too and no `TBD` may remain. Approve the participating patterns first.

In the diagram, a participation step's arrow is drawn dash-dotted and labelled `[+] 2: PAT-905 S1`, the plus being BPMN's call-activity marker. `emit` and `sync` keep a layer named `Participating patterns` holding one dashed region per participating pattern, labelled with its id and name, round the boxes bound to it; they are recomputed on every `sync`, so move the boxes, not the regions. Views of the structure include that layer; `publish.py --no-regions` leaves it out. In the walkthrough, a participation step carries a drill-in badge with a boxed plus that opens the participating pattern's `scenarios.html` at that scenario, with a link back to the composite pattern's step; an open participating pattern's marker is greyed and has no link. Publish the participating patterns with the composite pattern (`publish.py --recursive` over their common folder) so the links resolve.
