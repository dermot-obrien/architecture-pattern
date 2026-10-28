# Scripts

Helper scripts for working with architecture patterns.

## Version Sync Checker

### `check-version-sync.sh` / `check-version-sync.ps1`

**Purpose:** Prevent version drift between SKILL.md, documentation, and examples.

Verifies that version references are consistent across:
- SKILL.md files (source of truth for versions)
- docs/quick-start.md (installation examples)
- Repository URLs in update scripts
- Local git tags (warns if version not yet tagged)

**Usage:**
```bash
# bash
bash scripts/check-version-sync.sh

# PowerShell
.\scripts\check-version-sync.ps1
```

**When to run:**
- Before committing version bumps in SKILL.md
- Before creating a release tag
- As part of CI/PR checks
- When updating dependency versions

**Exit codes:**
- `0` - All versions are consistent ✓
- `1` - Found inconsistencies (details printed)

**Example output:**
```
Checking version consistency across repository...

Current skill versions:
  pattern:          v0.11.0
  use-case:         v0.3.0
  cross-reference:  v0.3.0

Required dependencies (from pattern SKILL.md):
  model:            >= v0.9.0
  markdown-deck:    >= v0.6.0

Checking docs/quick-start.md...
  ✓ pattern version matches
  ✓ model version matches
  ✓ markdown-deck version compatible (>= v0.6.0)

== All version references are consistent
```

## Update Scripts

### `update-skills.sh` / `update-skills.ps1`

Install the skills into a repository, or update them to the latest releases. A first install and an update are the same run. Run from the root of the repository the skills go into.

```bash
bash update-skills.sh                            # install or update every skill of the latest release
bash update-skills.sh --check-only               # what would change, changing nothing
bash update-skills.sh --skills pattern,use-case  # only these (copies), or add these (a declaration)
bash update-skills.sh --yes                      # do not ask first
```

```powershell
.\update-skills.ps1
.\update-skills.ps1 -CheckOnly
.\update-skills.ps1 -Skills pattern,use-case
.\update-skills.ps1 -Yes
```

With copies in `.agents/skills/` (no `.agents/skills.json`), it reads the latest release's `bundle.json` and installs every skill it lists (`pattern`, `use-case`, `cross-reference`, `portfolio`, `draft`, `convert`), with the latest `model` and `markdown-deck`: it backs up any installed copy to `.skill-backups/<time>/`, copies the new ones, runs `npm install` for `markdown-deck`, and runs each skill's post-install check from `bundle.json`. A skill added to a later release is installed with no change to the script.

With a `.agents/skills.json`, it moves each declared skill to its latest `<skill>--v` tag (and the Architecture Continuum bundle to its latest release), adds any skill named with `--skills`, and reinstalls with the workspace's own installer: `scripts/architecture.mjs reinit`, else `scripts/skills.mjs sync --copy`.

Needs git, Node 18 or later and Python 3.11 or later. [Updating](../docs/updating.md) has the details for users.

## List Scripts

### `list-patterns.sh` / `list-patterns.ps1`

List all patterns, use cases, and reference architectures in a directory with validation status.

**Usage:**
```bash
# Bash
./scripts/list-patterns.sh                    # List in current directory
./scripts/list-patterns.sh patterns           # List in patterns/ directory
./scripts/list-patterns.sh patterns --verbose # Show validation warnings

# PowerShell
.\scripts\list-patterns.ps1                   # List in current directory
.\scripts\list-patterns.ps1 -Path patterns    # List in patterns/ directory
.\scripts\list-patterns.ps1 -Path patterns -Verbose  # Show validation warnings
```

The script will:
1. Search for all `index.md` files with pattern metadata
2. Display ID, title, version, and path for each pattern
3. Show validation status (✓ valid, ✗ has issues) if model skill is installed
4. In verbose mode: show detailed validation warnings and full scan results

**Example output:**
```
[AP-001] ✓ Order Intake Pattern
  Version: 1.0
  Path: ./patterns/AP-001-order-intake

[AP-002] ✗ Event-Driven Architecture
  Version: 2.1
  Path: ./patterns/AP-002-event-driven
  Validation:
    warning: diagram drift detected in components.drawio
```
