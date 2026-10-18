# Choosing the type

`convert.py` chooses each unit's type from its content and writes the reasoning into the conversion report. A type the caller gives with `--type`, or that the source declares in front matter `pattern_type` or `document_type`, or that `unit.json` sets, is taken as given.

## The evidence each type scores

| Type | Evidence | Points |
|---|---|---|
| Architecture pattern | Share of boxes with ABB identifiers | up to 4 |
| | Share of box names that are logical building blocks: service, store, gateway, broker, engine, registry, pipeline, cache, client, portal and the like, and not also technologies | up to 4 |
| | The text speaks of a pattern, logical design, building blocks, or being technology-agnostic | up to 2 |
| Reference architecture | Share of boxes with SBB identifiers | up to 4 |
| | Share of box names that are technologies (database, cluster, queue, bucket, server, runtime, ingress, load balancer...) or carry a version number | up to 4.5 |
| | Share of boxes drawn with an icon from a technology shape library rather than draw.io's generic ones | up to 3 |
| | The text speaks of a reference architecture, deployment, hosting, a platform, products or versions | up to 2 |
| Use case | Actor shapes, or boxes whose kind is actor | up to 3 |
| | Statements of a goal: "as a ... I want", "so that", "wants to", goal, use case | up to 4 |
| | Boxes named for a user: user, customer, claimant, applicant, patient... | up to 1.5 |
| Collaboration | Share of box names that are people, teams, boards, offices or roles | up to 4 |
| | Collaboration words in the text: handover, review, agree, escalate, sign off, stakeholder... | up to 2.4 |

A box named for a technology counts as physical whatever else its name says, so "Query API server" is a technology, not a logical API.

## How the choice falls

The highest score wins when it is at least 2 and at least 0.75 clear of the next. Otherwise the unit is a collaboration, the type with the lightest rules, and the report says no type was clearly ahead. The pages of one draw.io file are one body of material, so their type is chosen together.

When the report says no type was clearly ahead, look at the material and confirm the type with the user; then set `type` in `unit.json` and redraft with `--force`, or run again with `--type`.

## The collaboration type

A collaboration is participants working together: people, teams, boards, systems and outside parties, and what passes between them. It keeps the four essential parts of every pattern and drops the rest:

| Part | Section | Rule |
|---|---|---|
| Diagram | Diagram | Generated from the tables and checked against them, as in any pattern |
| Boxes | Participants | Local ids unless a catalogue entry exists; Kind is free (person, team, board, system, external) |
| Links | Interactions | Provider, Consumer and a short Purpose; no protocol, payload or retry columns |
| Sequences | Scenarios | At least one, five to ten steps, a straight line |

Purpose, Agreements, Open Questions and Catalogue Mapping are the only other sections, and only Purpose is required. The template is the pattern skill's `assets/templates/collaboration.md`, with `pattern_type: collaboration`. Its tables read with the same bindings as a use case's Participants and Interactions, so a repository that binds use cases already reads collaborations; one that numbers them binds:

```toml
[suite.pattern.types.collaboration]
label    = "Collaboration"
idSeries = "CO"
```

The architecture continuum's schema knows two kinds of pattern document, the architecture pattern and the reference architecture. Adding collaboration there is separate work in that repository.
