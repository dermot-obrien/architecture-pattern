<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# markdown-deck

An agent skill that turns tagged sections of one Markdown document into HTML slides and a PDF. The tags are HTML comments, so the document still reads as a document wherever Markdown renders.

**Zero skill dependencies** - works standalone with any document. Optionally integrates with the `model` skill for diagram staleness checks.

## Install

```bash
gh skill install dermot-obrien/markdown-deck markdown-deck
npm install --prefix .agents/skills/markdown-deck
```

Or copy `skills/markdown-deck/` and run `npm install` in it. See the [repository README](../../README.md#install) for all methods.

## Quick start

1. **Tag a document** (`talk.md`):
   ```markdown
   # Shipping Smaller
   
   <!-- deck:cover subtitle="Why small releases win" -->
   
   <!-- deck:slide -->
   ## The problem
   
   Large releases hide risk until they ship.
   
   ## Appendix
   
   No tag here - stays document-only.
   ```

2. **Build:**
   ```bash
   node .agents/skills/markdown-deck/bin/markdown-deck.mjs build talk.md --out dist --pdf
   ```

3. **Open** `dist/deck.html` - navigates with arrow keys, `F` for fullscreen, `I` for index

4. **PDF** at `dist/deck.pdf` - one 16:9 page per slide

See the [quick start guide](../../docs/quick-start.md) for themes, colour schemes and background images.

## Tags

| Tag | Creates |
|---|---|
| `<!-- deck:cover -->` | Cover slide |
| `<!-- deck:slide -->` | Content slide from the next heading's section |
| `<!-- deck:divider -->` | Section divider |
| `<!-- deck:image src="./slide.png" -->` | Slide from a 16:9 image |
| `<!-- deck:html src="./slide.html" -->` | Slide from custom HTML |
| `<!-- deck:include src="../other.md" section="..." -->` | Section from another document |
| `<!-- deck:skip -->` ... `<!-- /deck:skip -->` | Keeps in document, drops from deck |
| `<!-- deck:note -->` ... `<!-- /deck:note -->` | Presenter notes |

See [docs/tags.md](../../docs/tags.md) for all attributes and behaviors.

## Commands

```bash
# Build deck
node .agents/skills/markdown-deck/bin/markdown-deck.mjs build <file> --out <dir> --theme default

# Also export PDF
node .agents/skills/markdown-deck/bin/markdown-deck.mjs build <file> --out <dir> --pdf

# Publish all decks in a workspace
node .agents/skills/markdown-deck/bin/markdown-deck.mjs publish <root> --out <site>/decks

# List available themes
node .agents/skills/markdown-deck/bin/markdown-deck.mjs themes

# Check installation
node .agents/skills/markdown-deck/bin/check.mjs
```

See [docs/commands.md](../../docs/commands.md) for all options.

## Documentation

| Page | Content |
|---|---|
| [Quick start](../../docs/quick-start.md) | From nothing to HTML and PDF in 10 minutes |
| [Tags](../../docs/tags.md) | Every tag with attributes and examples |
| [Concepts](../../docs/concepts.md) | Themes, palettes, backgrounds, publishing |
| [Configuration](../../docs/configuration.md) | Repository and per-deck settings |
| [Commands](../../docs/commands.md) | All commands and options |
| [Troubleshooting](../../docs/troubleshooting.md) | Error messages and fixes |

## Updating

To update after a new release:

1. **Delete old installation:**
   ```bash
   rm -rf .agents/skills/markdown-deck
   ```

2. **Reinstall:**
   ```bash
   gh skill install dermot-obrien/markdown-deck markdown-deck
   npm install --prefix .agents/skills/markdown-deck
   ```
   
   Or copy from repository:
   ```bash
   git clone --depth 1 --branch markdown-deck--v0.6.8 https://github.com/dermot-obrien/markdown-deck.git
   cp -r markdown-deck/skills/markdown-deck .agents/skills/
   npm install --prefix .agents/skills/markdown-deck
   ```

3. **Verify:**
   ```bash
   node .agents/skills/markdown-deck/bin/check.mjs
   node .agents/skills/markdown-deck/bin/markdown-deck.mjs --version
   ```

4. **Rebuild existing decks** to pick up theme/rendering changes:
   ```bash
   node .agents/skills/markdown-deck/bin/markdown-deck.mjs build <file> --out <dir>
   ```

**Always run `npm install`** after reinstalling - the skill has npm dependencies (gray-matter, marked, playwright).

## Requirements

- Node.js 18+
- `npm install` run once in the skill directory
- Playwright (installed by npm) for PDF export - uses Edge/Chrome/Chromium
- No other skills required (works standalone)

Check:
```bash
node --version
ls .agents/skills/markdown-deck/node_modules/
```

## Testing

14 test suites covering parsing, rendering, building, browser export:

```bash
cd .agents/skills/markdown-deck
npm test
```

## Licence

Content under [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt), code under [Apache-2.0](../../LICENSES/Apache-2.0.txt). See [LICENSE](LICENSE) and [NOTICE](NOTICE).
