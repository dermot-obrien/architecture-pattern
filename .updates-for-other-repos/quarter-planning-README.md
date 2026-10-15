<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# quarter-planning

An agent skill for planning a quarter or programme increment in two stages: derive a budget of points from the calendar and resourcing, allocate it to epics, then elaborate deliverables and roll their sizes up. Checks the integrity chain, frames epics against a definition ladder, generates epic cards, tracks feature requests, and links plan documents to published pages.

**Zero skill dependencies** - reads your planning model and registers at configured paths.

## Install

```bash
gh skill install dermot-obrien/delivery-planning quarter-planning
```

Or copy `skills/quarter-planning/` into your agent's skills folder. See the [repository README](../../README.md#install) for all methods.

## Quick start

1. **Set up your planning model** - 6 required bindings in `.agents/skill-bindings.toml`:
   ```toml
   [suite.quarter-planning]
   sources.work_item = "../planning/work_item.yaml"
   sources.activity = "../planning/activity.yaml"
   register = "../planning/deliverable-register.csv"
   basis = "../planning/quarters/2027-q1/basis.yaml"
   calendar = "../planning/calendar.csv"
   resourcing = "../planning/resourcing.csv"
   ```

2. **Verify installation:**
   ```bash
   python .agents/skills/quarter-planning/bin/check.py
   python .agents/skills/quarter-planning/bin/quarter.py --quarter 2027-q1 --where
   ```

3. **Check quarter status:**
   ```bash
   python .agents/skills/quarter-planning/bin/quarter.py --quarter 2027-q1
   ```

4. **View the budget ladder:**
   ```bash
   python .agents/skills/quarter-planning/bin/quarter.py --quarter 2027-q1 --budget
   ```

5. **Frame an epic:**
   ```bash
   python .agents/skills/quarter-planning/bin/quarter.py --quarter 2027-q1 --frame EP-123
   ```

See the [quick start guide](../../docs/quick-start.md) for a complete worked example with sample data.

## Commands

| Command | What it does |
|---|---|
| `<quarter>` | Budget vs planned per epic, load vs capacity per person, what fails |
| `--budget` | Top-level budget and the ladder from calendar to points |
| `--validate` | Full validation: all 10 sections of integrity and subscription checks |
| `--frame <epic>` | Frame one epic against capability lane and definition ladder |
| `--size <epic>` | Name/revise products on one epic, set budget |
| `--cards` | Regenerate epic cards and stage grid |
| `--links` | Update epic/story links in plan documents to published pages |
| `--close` | Record actuals (rung reached, actual points) at quarter end |
| `--approve <record> <stage>` | Move to approval stage (draft/sized/validated/approved) |
| `--check` | Run checks and interpret output |
| `--reconcile` | Regenerate views, align plan documents to them |
| `--where` | Show resolved input paths without reading them |

See [docs/commands.md](../../docs/commands.md) for all flags and options.

## Documentation

| Page | Content |
|---|---|
| [Quick start](../../docs/quick-start.md) | From empty workspace to validated quarter |
| [quarter-planning](../../docs/quarter-planning.md) | What the skill does and needs |
| [Concepts](../../docs/concepts.md) | Budget ladder, two stages, checks, optional layers |
| [Configuration](../../docs/configuration.md) | Every binding key with type, default and example |
| [Commands](../../docs/commands.md) | Every command and option |
| [Troubleshooting](../../docs/troubleshooting.md) | Every message and what to do |
| [Examples](../../docs/examples.md) | Test workspace files |
| [References](references/) | 12 detailed references the agent reads |

## Updating

To update after a new release:

### Automated Update (Recommended)

The repository includes update scripts that automatically fetch the latest version, backup your current installation, and verify:

**bash:**
```bash
# From repository root
./scripts/update-quarter-planning.sh             # Update workspace skill
./scripts/update-quarter-planning.sh --user      # Update user-level skill
./scripts/update-quarter-planning.sh --check-only  # Check version without updating
```

**PowerShell:**
```powershell
# From repository root
.\scripts\update-quarter-planning.ps1            # Update workspace skill
.\scripts\update-quarter-planning.ps1 -User      # Update user-level skill
.\scripts\update-quarter-planning.ps1 -CheckOnly # Check version without updating
```

The script will:
1. Check current vs latest version
2. Backup your current installation to `.skill-backups/`
3. Download and install the latest version
4. Verify the installation
5. Remind you to check for new bindings

### Manual Update

1. **Delete old installation:**
   ```bash
   rm -rf .agents/skills/quarter-planning
   ```

2. **Reinstall:**
   ```bash
   gh skill install dermot-obrien/delivery-planning quarter-planning
   ```
   
   Or copy from repository:
   ```bash
   git clone --depth 1 --branch quarter-planning--v3.6.0 https://github.com/dermot-obrien/delivery-planning.git
   cp -r delivery-planning/skills/quarter-planning .agents/skills/
   ```

3. **Verify:**
   ```bash
   python .agents/skills/quarter-planning/bin/check.py
   ```

4. **Check for new bindings:**
   ```bash
   python .agents/skills/quarter-planning/bin/quarter.py --quarter <your-quarter> --where
   cat .agents/skills/quarter-planning/inputs.toml
   ```

5. **Re-validate your quarters** after updating:
   ```bash
   python .agents/skills/quarter-planning/bin/quarter.py --quarter 2027-q1 --validate
   ```

**New releases may add:**
- New required or optional bindings (check `inputs.toml`)
- New validation rules or approval stage requirements
- New commands or fields in the data model

Check the [CHANGELOG](../../CHANGELOG.md) for breaking changes.

## Requirements

- Python 3.11+ (for `tomllib` to read config)
- PyYAML: `python -m pip install pyyaml`
- No other skills required

Check:
```bash
python --version  # Should be 3.11+
python -c "import yaml; import tomllib"
```

## Configuration

The skill requires **6 mandatory paths** with **no defaults** - you must configure them:

1. `sources.work_item` - Epics with budget and deliverables
2. `sources.activity` - Stories with assignments
3. `register` - Product types and base story points
4. `basis` - Quarter assumptions (working days, points, totals)
5. `calendar` - Working days per period
6. `resourcing` - Person capacity and allocations

See [docs/configuration.md](../../docs/configuration.md) and [references/data-contract.md](references/data-contract.md) for complete field definitions.

## The Two-Stage Model

1. **Stage 1: Budget** - Allocate capacity as `budget_points` per epic (before stories exist)
2. **Stage 2: Elaboration** - Name `deliverables` that roll up to `planned_points`

The epic is where they meet. They're compared, not reconciled. Over-subscription is a scoping decision, not a defect.

## Testing

2 test files covering budget calculation and validation logic:

```bash
python -m unittest discover -s .agents/skills/quarter-planning/tests
```

## Licence

Content under [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt), code under [Apache-2.0](../../LICENSES/Apache-2.0.txt). See [LICENSE](LICENSE) and [NOTICE](NOTICE).
