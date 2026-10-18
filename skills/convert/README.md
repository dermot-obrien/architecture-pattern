<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# convert

An agent skill that turns existing architecture material, a diagram in draw.io, SVG or PNG with whatever Markdown goes with it, into a document of the right pattern type: an architecture pattern, a reference architecture, a use case or a collaboration. The result is an ordinary document of the [pattern](../pattern) or [use-case](../use-case) skill, which regenerates its diagram from its tables, checks it and publishes it.

Every type has the same essence: a diagram, a description of its boxes, a description of the links between them, and one or more scenarios giving the sequence of what happens. Conversion finds those four parts in the source and drafts the rest of the template for the agent to complete.

## Requires

| Skill | Does | Comes from |
|---|---|---|
| [pattern](../pattern) | Its templates, `register.py` numbering and `publish.py` | This repository |
| [use-case](../use-case) | The use case template | This repository |
| [model](https://github.com/dermot-obrien/diagram-model) | Reads identified draw.io exactly, adopts identifiers onto a drawing, validates, stamps views | Its own repository |

Python 3.11 or newer, and git for archiving. draw.io desktop is optional.

## Use

```bash
python <skills>/convert/scripts/convert.py run <file-or-folder>... --dry-run
python <skills>/convert/scripts/convert.py run <file-or-folder>...
```

The first prints the plan, the second carries it out and writes `report.md` in the conversion folder. [SKILL.md](SKILL.md) is the procedure an agent follows; [docs/converting.md](https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/converting.md) is the guide for people. The [examples](examples) are generic sources in every format, which the tests convert.

## Licence

Content under CC BY 4.0 and code under Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
