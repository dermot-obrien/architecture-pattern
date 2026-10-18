# Drafting method

How to turn research into a draft a reviewer can trust. The script checks the form; this is about the content.

## What to find

| Section | Look for | Good sources |
|---|---|---|
| Context (or Intent) | The recurring problem, the forces that pull against each other, and why the obvious answer fails | The original description of the pattern; the candidate's notes; the backlog row |
| Building Blocks, or Participants | The responsibilities the solution needs, each one box | Descriptions of the pattern's structure; related patterns in the repository, whose building blocks may be reused by identifier |
| Interfaces, or Interactions | What passes between the boxes, and in which direction | The same, plus protocol or interface specifications for a reference architecture |
| Scenarios | Two to four flows that show the pattern working, each five to ten steps | Worked examples; the use cases the pattern serves |
| Applicability, Not Applicable | When to use it, and when another pattern fits better | Comparisons and critiques; related patterns |
| Risks and Trade-offs, Decisions | What it costs, and the choices a team must make | Critiques, experience reports, the consequences recorded in decision records |

For a reference architecture, also find the products and services that realise each building block of the architecture pattern it implements, from their own documentation.

## How to cite

- Put the citation after the claim it supports, in the same sentence: `Replay grows with the stream, and a snapshot bounds it [W3].`
- Cite each claim from research. Do not cite your own connecting sentences.
- A table cell can carry a citation when the row comes from a source.
- One claim, several sources: `[W1] [W2]`.
- Prefer two independent sources for a claim the design depends on, and say in your summary to the user which claims rest on one.
- Use the repository's own documents (`R` sources) for what this organisation already decided; use web sources for what the pattern is in general.

## What to leave out

- A section the research does not support. Its guidance stays in the template for the reviewer, which is better than a plausible invention.
- Products and vendors in an architecture pattern: it is technology-agnostic.
- Long quotations. Summarise, and cite.
- Anything from a source you did not read.

## The sections file

A Markdown file of `## Heading` blocks, one per section you write, with the template's headings exactly (numbering is ignored). Tables keep the template's columns. Scenario headings are `### S1 Name`, as in the template.

```markdown
## Context

Several products keep balances that disagree [R1]. An event-sourced ledger stores every change as an immutable event and derives the state by replaying them [W1].

## Building Blocks

| ID | Name | Responsibility |
|---|---|---|
| 01 | Ledger | Appends events and never changes one |
```
