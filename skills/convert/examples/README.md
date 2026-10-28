# Examples

Generic material of the kinds people already have, which the tests convert and publish. `tests/make_examples.py` writes `sources/`; the draw.io files are left as a person would leave them, with no identifiers.

| Source | Format | Text | Converts to | Shows |
|---|---|---|---|---|
| `sources/order-intake/` | draw.io drawn by hand | Rich: components table, numbered flow, constraints | Architecture pattern | Containers, a key left out, a title, numbered arrows merged with the written flow, unplaced text kept |
| `sources/edge-gateway/` | SVG exported from draw.io, with the diagram inside | Sparse: a title and a line | Reference architecture | Versions and technology names; a container; a technology icon |
| `sources/claims-portal/` | Plain SVG from another tool | Rich: a goal, actors, main flow | Use case | Shapes, lines and labels read best-effort, the layout kept |
| `sources/incident-handover/` | PNG picture | Sparse | Collaboration, read by the agent | `agent/incident-handover.unit.json` is what the agent writes |
| `sources/document-search/` | Plain SVG | None | Architecture pattern | No text; no sequence, so the agent writes S1 |
| `sources/event-pipeline/` | Compressed draw.io, two pages | None | Two reference architectures | One document per page, the type chosen for both together |
| `sources/supplier-onboarding/` | draw.io drawn by hand | Rich: participants table with kinds, a mermaid sequence | Collaboration | A sequence diagram becomes the scenario |
| `sources/appointment-booking/` | PNG exported from draw.io, with the diagram inside | Sparse: one goal | Use case | An actor shape; numbered arrows |
| `sources/release-approval/` | PNG picture | None | Collaboration, read by the agent | `agent/release-approval.unit.json` sets no type, so it is chosen |
| `sources/platform/` | A folder of three: two draw.io and a plain SVG | By stem, one with none | Three architecture patterns | A folder of several patterns |

Converting the lot, from this folder:

```bash
python ../scripts/convert.py run sources --out /tmp/converted --work /tmp/conversions --no-archive
```
