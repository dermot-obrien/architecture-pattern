<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# model

An agent skill that treats a diagram and a document as two views of one model of boxes and lines. Extract a model from Markdown tables, draw.io, JSON or YAML; emit it to any of those; validate one against another; and render draw.io layers to SVG, PNG or PDF.

Nothing in it knows what the boxes mean, so it serves an architecture pattern, a network topology, a process flow, a data lineage or any model of boxes and lines. Your workspace's binding file holds the vocabulary.

**Pure Python standard library** - no installation needed beyond Python 3.9+ (3.11+ for config files).

## Install

```bash
gh skill install dermot-obrien/diagram-model model
```

Or copy `skills/model/` into your agent's skills folder. See the [repository README](../../README.md#install) for all installation methods.

## Quick start

With a document `shop.md` containing `## Components` and `## Interfaces` tables:

```bash
# 1. Check installation
python .agents/skills/model/bin/model.py doctor

# 2. Generate diagram from tables
python .agents/skills/model/bin/model.py emit shop.md --to drawio --out components.drawio

# 3. Open in draw.io and arrange the shapes

# 4. Validate they agree
python .agents/skills/model/bin/model.py validate shop.md --against components.drawio

# 5. Keep them synchronized after edits
python .agents/skills/model/bin/model.py sync shop.md components.drawio

# 6. Render a view
python .agents/skills/model/bin/model.py render components.drawio --out components.svg --layer Structure

# 7. Animate scenarios
python .agents/skills/model/bin/model.py animate shop.md
```

The [quick start guide](../../docs/quick-start.md) goes step by step with a complete example.

## Commands

| Command | What it does |
|---|---|
| `doctor` | Resolves and validates bindings; checks a workspace is ready |
| `emit` | Generates a representation from another (e.g., diagram from tables) |
| `extract` | Extracts a model to JSON, YAML or CSV |
| `validate` | Checks a diagram and document agree |
| `sync` | Updates a diagram from changed tables, preserving layout |
| `composition` | Prints the tree of participating patterns |
| `rename` | Renames an identifier across document, diagram and references |
| `render` | Renders draw.io layers to SVG, PNG or PDF |
| `layers` | Lists layers in a diagram |
| `animate` | Builds an HTML walkthrough of scenarios |
| `stamp` | Records what a manually-exported view shows |
| `drawio` | Reports whether draw.io desktop is installed |
| `contract` | Checks a document/template has the structure the binding reads |
| `scan` | Validates every document in a folder that declares a diagram |

See [docs/commands.md](../../docs/commands.md) for every flag and option.

## Documentation

| Page | Content |
|---|---|
| [Quick start](../../docs/quick-start.md) | From nothing to a validated diagram and walkthrough |
| [Concepts](../../docs/concepts.md) | The model, representations, conventions, findings, composition |
| [Configuration](../../docs/configuration.md) | Every binding, front matter key and environment variable |
| [Commands](../../docs/commands.md) | Every command, flag, output and exit code |
| [Troubleshooting](../../docs/troubleshooting.md) | Every message and rule with its fix |
| [Examples](../../docs/examples.md) | The worked example |
| [SKILL.md](SKILL.md) | What the agent reads |

## Updating

To update after a new release:

1. **Delete the old installation first** (important):
   ```bash
   rm -rf .agents/skills/model
   ```

2. **Reinstall:**
   ```bash
   gh skill install dermot-obrien/diagram-model model
   # Or: git clone --depth 1 --branch model--v0.9.0 https://github.com/dermot-obrien/diagram-model.git
   #      cp -r diagram-model/skills/model .agents/skills/
   ```

3. **Verify:**
   ```bash
   python .agents/skills/model/bin/model.py doctor
   ```

4. **Check for new bindings or rules:**
   ```bash
   python .agents/skills/model/bin/model.py doctor --json
   cat .agents/skills/model/inputs.toml
   ```

5. **Re-validate existing models:**
   ```bash
   python .agents/skills/model/bin/model.py scan patterns --recursive
   ```

**No npm dependencies** - Python only. If you update skills that depend on `model` (like `pattern`), update them all together to ensure version compatibility.

## Requirements

- Python 3.9+ (3.11+ for reading `.toml` config files)
- draw.io desktop (optional - for rendering; views can be exported manually)
- PyYAML (optional - only needed for YAML input/output)

Check requirements:
```bash
python --version
python .agents/skills/model/bin/model.py drawio
```

## Testing

245 tests covering extraction, emission, validation, composition, pattern types, register lookup, contract validation and more.

```bash
python -m unittest discover -s .agents/skills/model/tests
```

## Licence

Content under [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt), code under [Apache-2.0](../../LICENSES/Apache-2.0.txt). See [LICENSE](LICENSE) and [NOTICE](NOTICE).
