<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Composing patterns

A composite pattern is one whose scenario steps run other patterns' flows, its participating patterns. A checkout pattern does not redraw how an order is stored; one of its steps runs the order intake pattern's scenario, and the diagram, the walkthrough and validation all follow that link.

Step 9 of the [quick start](quick-start.md#9-compose-a-pattern-that-runs-another) builds one. The skill's own summary is [skills/pattern/references/compose.md](../skills/pattern/references/compose.md), and the model skill's [composition reference](https://github.com/dermot-obrien/diagram-model/blob/main/skills/model/references/composition.md) is the authority on the rules.

## Three ways to work

- Top down. Sketch the composite pattern first, with each hard part an open participating pattern, `TBD <name>`. Solve each as its own pattern, then replace the `TBD` with its id and scenario key.
- Bottom up. Compose approved patterns: each step that one of them already solves runs its scenario rather than repeating it.
- Both at once, as the work finds its level.

## The notation, and where it comes from

Nothing here is invented. A participation step is BPMN 2.0.2's call activity (in a UML sequence diagram, an InteractionUse, a `ref` fragment). A scenario's Start and Finish are its BPMN start and end events, and UML 2.5.1 ports on the pattern's boundary. A role binding, drawn as a dashed region round the boxes it binds, is UML 2.5.1's collaboration use.

## The Uses column

Add a `Uses` column to the scenario's steps table. The header is `[markdown.scenarios] columns.uses` in the binding, `Uses` by default; a binding's `columns` are merged over the defaults, so you set it only to use another header. Documents without the column behave as before.

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Checkout page | 02 Order records | place the order once | | PAT-001 S1 (01=01, 03=02) |
| 2 | 02 Order records | 03 Notifier | announce the order | IF-10 | |
| 3 | 03 Notifier | 01 Checkout page | confirm to the customer | | TBD customer notification |

A Uses cell holds one of:

| Form | Meaning |
|---|---|
| empty | An ordinary step |
| `PAT-001 S1` | This step is the whole of PAT-001's scenario S1. Text after the key is prose and ignored |
| `PAT-001 S1 (01=01, 03=02)` | The same, with a role binding directly after the key: comma-separated `id=id` pairs, the participating pattern's box on the left, this pattern's on the right |
| `TBD <name>` | An open participating pattern, not yet written. It cannot carry a binding |

A participation step is one arrow standing for the participating pattern's whole flow. Its Actor is where that flow enters this pattern and its Target where it leaves; both are required. Its Interface is optional. The participating pattern's id must match `[model] pattern_id`, by default two to five capitals, a hyphen and three digits.

## Start and Finish

A scenario another pattern may run should declare where its flow starts and finishes, each on its own line under the heading and before the steps table, as separate paragraphs:

```markdown
### S1 Place an order

Start: 01 Web shop

Finish: 03 Order store
```

The Start must be the first step's Actor, and the Finish the last step's Actor or Target; `validate` holds them to it (`scenario_start_finish`). Without them, a composite pattern joins to the first step's Actor and the last step's Actor or Target, which is usually right but is a guess. Declaring them makes the join explicit, and `composition` says `joined at its declared start and finish`.

## How boxes correspond across patterns

The participation step's Actor must correspond to the participating scenario's Start, and its Target to its Finish. Boxes correspond, in this order:

1. Through the step's role binding. This is the only way two local ids join across documents, since `01` in one pattern and `01` in another are unrelated.
2. When they share a catalogue id, `COMP-001` in both.
3. When a local box maps to that catalogue id in either document's Catalogue Mapping.

A join that cannot be established is a `participant_join` warning naming both boxes and suggesting the binding to add. Bind them, or map the local box, rather than renaming it.

Each box appears at most once on each side of a binding, and every box named must exist: a binding naming a box that is not there is a `participant_binding` error.

## Where participating patterns are found

A participating pattern is a folder named `<ID>-<slug>` holding `index.md`, or, when no folder is named for the id, a document whose first H1 starts with the id. It is searched for, to any depth, under the first of these that is set:

1. `[model] patterns_root`
2. `[suite.pattern] patternsRoot`
3. `[suite.pattern] outputDir`

With none set, each folder from the composite pattern upward is searched two levels deep, stopping at the repository root. `model doctor` prints the root in use and which binding supplied it. Two documents claiming one id is a `participant_ambiguous` warning, and the first found is used.

## Checking a composition

```
python <skills>/model/bin/model.py composition index.md          # the tree
python <skills>/model/bin/model.py composition index.md --json   # the same as data
python <skills>/model/bin/model.py validate index.md             # errors, warnings, summary
```

`composition` prints each participation step, the participating pattern's id, scenario and status, its binding, whether each end of the join used a declared Start or Finish, and open participating patterns, recursively, with cycles marked. `--json` gives `tree` and `summary`; each participation carries `binding` and `join`, as `declared` or `derived` per end. `publish.py` prints the same tree for every composite pattern it publishes.

`validate` reports these rules. Each severity can be changed in the binding's `[rules]`.

| Rule | Default | When |
|---|---|---|
| `uses_invalid` | error | The cell is neither `<ID> <KEY>` nor `TBD <name>`, a binding is not all `id=id` pairs, or a TBD carries a binding |
| `uses_step_endpoints` | error | A participation step without an Actor or a Target |
| `participant_missing` | error | No document for the id |
| `participant_scenario_missing` | error | The participating pattern has no scenario with that key |
| `participant_binding` | error | A binding names a box that is not in the pattern on its side, or one box twice on a side |
| `composition_cycle` | error | A pattern runs itself, directly or through others |
| `participant_unapproved` | error | The approval gate, below |
| `scenario_start_finish` | error | A declared Start or Finish the steps do not bear out, or one that is not a box of the pattern |
| `participant_join` | warn | The step's Actor does not correspond to the scenario's start, or its Target to its finish |
| `participant_open` | warn | An open participating pattern, listed until it is written |
| `participant_ambiguous` | warn | Two documents claim one id |
| `step_uses_mismatch` | warn | The diagram's overlay or regions disagree with the document's Uses; run `sync` |

[Troubleshooting](troubleshooting.md#composite-patterns) shows the exact message for each and the fix.

## The approval gate

Once a composite pattern's front matter `status` is one of the approved statuses (by default Final, Approved, Active, Published), every participating pattern at any depth must be approved too, and no `TBD` may remain. Otherwise `validate` fails with `participant_unapproved`, and `publish.py` skips the pattern. Approve participating patterns first; the composite pattern last. Set the statuses with `approvedStatuses` in `[suite.pattern]`, or `approved_statuses` in `[model]`, which wins.

## On the diagram

`emit` and `sync` draw a participation step's overlay arrow heavier and dash-dotted, labelled `[+] 1: PAT-001 S1`; the `[+]` is BPMN's call-activity marker, in ASCII because a boxed-plus glyph falls back to an empty box in draw.io's export. They also keep a layer named `Participating patterns` just above Structure, with one dashed, rounded region per participating pattern, labelled with its id and name (`Open: <name>` for a TBD), round the boxes bound to it and the Actor and Target of every step that runs it.

Regions are recomputed on every `sync` from where the boxes are, so move the boxes, not the regions. The structure view includes the regions by default; `publish.py --no-regions` or `model render --no-regions` leaves them out. A view exported by hand is stamped with both layers:

```
python <skills>/model/bin/model.py stamp components.svg --diagram components.drawio --layer Structure --layer "Participating patterns"
```

## In the walkthrough

A participation step is one step with a drill-in badge, a boxed plus. Clicking it, or the link beside the steps, or pressing D, opens the participating pattern's walkthrough at that scenario, with a link back to the step it came from; B goes back. An open participating pattern's badge is greyed and has no link. A `#S1` or `#S1-3` hash opens any walkthrough at that scenario or step.

The drill-in is a relative link to the participating pattern's own `scenarios.html`, so publish them together:

```
python <skills>/pattern/scripts/publish.py <folder holding both> --recursive
```

## Checklist for a composite pattern

1. Every participating pattern is listed in Patterns Applied, with its role.
2. Each participation step has an Actor and a Target, and a Uses cell of the right form.
3. Each participating scenario declares its Start and Finish.
4. Local boxes are joined by a role binding, or mapped to a shared catalogue id.
5. `model composition index.md` shows the tree you intend, and `model validate index.md` has no errors.
6. The participating patterns are approved before this one is.
7. The participating patterns are published with it, so the drill-in links resolve.

## Examples

- The quick start's PAT-002 Checkout runs PAT-001 Order Intake S1 through a two-pair binding and has one open participating pattern.
- [skills/pattern/examples/composite](../skills/pattern/examples/composite) runs the knowledge-retrieval example's S1 through a binding, `PAT-900 S1 (ABB-908=03)`, joining at that scenario's declared Start and Finish, and has one open participating pattern. CI checks its composition summary and its approval gate.
