<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Links to each box's page

Part of the `pattern` skill; [SKILL.md](../SKILL.md) summarises it.

The model skill's own section of the same file says how a declared identifier links to its page, so every walkthrough, and the diagram in draw.io, can open a building block, product, pattern or capability from its box. These are `model` bindings, not `[suite.pattern]` ones:

```toml
[model]
link_site   = "http://localhost:3000/docs"            # {site}; optional
link_target = "new"                                   # "new" (default) or "same"

[[links]]
match  = 'ABB-[0-9]{3}'                               # full match on the id; rules tried in order
locate = "../building-blocks/abbs/*/{id}-*"           # optional glob, relative to the binding file
href   = "{site}/building-blocks/abbs/{located}/"     # {id}, {site}, {located}, {rel}
target = "same"                                       # optional; wins over link_target
```

`{located}` is the glob's first match relative to its fixed folders, with a matched `index.md` dropped; `{rel}` is the path from the generated page to the match. Add one rule per identifier series the site has pages for, patterns included, so a participation step's participating pattern links to its page beside the drill-in. Local ids never link. A rule that matches but finds nothing is a `link_unresolved` warning. `model doctor --doc index.md` shows what each box resolves to.
