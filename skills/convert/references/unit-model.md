# The unit model

A unit is one diagram and the text that goes with it. Every reader writes the same model, as JSON, to `units/<unit>/source.json` (what was read) and `units/<unit>/unit.json` (what is drafted from). `convert.py draft` reads `unit.json`, so correcting a reading, or writing one from a picture, is editing that file.

## Shape

```json
{
  "name": "Incident handover",
  "summary": "The handover between the night and day operations teams.",
  "type": "collaboration",
  "status": "ready",
  "extraction": "agent",
  "boxes": [
    {"key": "b1", "label": "Night Operations", "description": "Runs the service overnight",
     "kind": "team", "geom": [40, 120, 200, 70]},
    {"key": "b2", "label": "Day Operations", "kind": "team", "geom": [600, 120, 200, 70]},
    {"key": "b3", "label": "Shift Log", "kind": "system", "geom": [320, 300, 200, 70],
     "uncertain": "the label is faint in the image"}
  ],
  "links": [
    {"source": "Night Operations", "target": "Shift Log", "label": "record open incidents"},
    {"source": "b1", "target": "b2", "label": "brief at handover"}
  ],
  "scenarios": [
    {"name": "Morning handover", "steps": [
      {"actor": "Night Operations", "target": "Shift Log", "action": "records the open incidents"},
      {"actor": "Night Operations", "target": "Day Operations", "action": "briefs the day team",
       "uncertain": "the picture gives no order; the text implies it"}
    ]}
  ]
}
```

## Fields

| Field | Meaning |
|---|---|
| `name` | The document's name, without an identifier |
| `summary` | The source's opening text; drafted under the type's opening section |
| `type` | `architecture-pattern`, `reference-architecture`, `use-case` or `collaboration` (or `AP`, `RA`, `UC`, `CO`). Empty: chosen from the content |
| `status` | `needs-agent` until someone has read a picture; `ready` to draft |
| `extraction` | `exact`, `heuristic` or `agent`: how the diagram was read. `agent` skips the comparison with the source, which has no structure |
| `id` | Set after drafting: the document's identifier. Kept on a redraft |

A box:

| Field | Meaning |
|---|---|
| `key` | Its handle within the unit. Optional when writing by hand; links and steps may name a box by `label` or `id` instead |
| `label` | Its name as drawn |
| `id` | The identifier it was drawn with, such as `ABB-012` or `03`. Empty: it takes the next local id |
| `description` | What it does here; `TBD` in the document when empty |
| `kind` | For a use case or collaboration, the Kind column: actor, solution, product, external, team, board, system |
| `container` | The group or swimlane it sat in; the Source column of a pattern |
| `geom` | `[x, y, width, height]` in the source's own units, such as the image's pixels. With every box placed, the document's diagram is drawn where the source drew them |
| `uncertain` | Why the reading is not sure. Listed in the document's conversion notes and the report |

A link: `source` and `target` (a box's key, label or id), `label` (what flows, the arrow's label), `description`, `directed` (false for a line with no arrowhead or one at each end), `uncertain`. Provider is `source` and Consumer `target`, in the arrow's direction.

A scenario: `name`, and `steps`, each with `actor` and `target` (key, label or id), `action`, optional `link` (a link's key or `IF-` id; found from the two boxes when omitted) and `uncertain`. Steps are numbered in order. A step with no actor cannot be drawn and is left out, with a note.

## What the readers look for

| Source | Boxes | Links | Scenarios |
|---|---|---|---|
| draw.io with identifiers | `model extract`: every identified shape | Every identified connector | Every scenario layer |
| draw.io drawn by hand | Labelled shapes; an icon takes the text beside it; containers become groups; a shape or group labelled Key or Legend is left out | Connectors between two boxes, a free end joined to the nearest box, direction from the arrowheads | Connectors numbered `1.`, `(2)` or `3:`; a later layer holding only connectors, or named S1, Scenario, Flow or Steps |
| SVG from draw.io | The draw.io inside, as above | | |
| Plain SVG | A closed shape holding text, its first line the name and the rest the description; a shape enclosing others is a group, one covering the picture its background | Lines and paths whose ends lie on two boxes, direction from their markers, labelled by the text nearest their middle | Labels that start with a number |
| PNG from draw.io | The draw.io in its `mxfile` text chunk, as above | | |
| Picture | Read by the agent | | |
| Markdown | Descriptions from a table whose first column names a box, a bullet `Name: what it does`, or a heading that is a box's name | Labels from a From and To table, or `A -> B: what flows` | A mermaid `sequenceDiagram`, a table with a Step column, a numbered list under a heading such as Scenario, Flow, Sequence, Steps or Process, or any numbered list whose items each name two boxes |

A numbered step in prose names its actor first and its target second, by the boxes' names; a step naming one box, or three, is marked uncertain.
