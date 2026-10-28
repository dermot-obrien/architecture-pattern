<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog

## [0.1.0] - 2026-10-18

### Added

- `draft.py plan`: reads a placeholder, lists the template's sections, suggests queries for online research, and gathers the repository's sources: related documents found by signature, the candidate's notes, and passages that use the pattern's terms. `--recorded` takes web sources from a recorded research file, the offline mode.
- `draft.py add-source`: records a web source the agent read, numbered W1, W2 and so on.
- `draft.py write`: puts the agent's cited sections into the placeholder's template, keeping its deck tags and every section not written, adds a Sources section with a link definition per source, and marks the result: status draft, `portfolio.state: draft`, provenance ai-generated and ai-raw, a review banner and a notice under the title. Refuses unresolved citations, headings the template does not have, an uncited draft and a document that is neither a placeholder nor a draft.
- `draft.py check`: confirms a draft carries every marking and every citation resolves.
