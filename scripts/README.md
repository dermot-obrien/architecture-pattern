# Scripts

Helper scripts for working with architecture patterns.

## Update Scripts

### `update-skills.sh` / `update-skills.ps1`

Automatically update the pattern, use-case, cross-reference, model, and markdown-deck skills to the latest versions.

**Usage:**
```bash
# Bash
./scripts/update-skills.sh              # Update workspace skills
./scripts/update-skills.sh --user       # Update user-level skills (~/.agents/skills)
./scripts/update-skills.sh --check-only # Check versions without updating

# PowerShell
.\scripts\update-skills.ps1             # Update workspace skills
.\scripts\update-skills.ps1 -User       # Update user-level skills
.\scripts\update-skills.ps1 -CheckOnly  # Check versions without updating
```

The script will:
1. Check current vs latest versions
2. Backup your current installation to `.skill-backups/`
3. Download and install latest versions
4. Run `npm install` for markdown-deck
5. Verify all installations

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
[PAT-001] ✓ Order Intake Pattern
  Version: 1.0
  Path: ./patterns/PAT-001-order-intake

[PAT-002] ✗ Event-Driven Architecture
  Version: 2.1
  Path: ./patterns/PAT-002-event-driven
  Validation:
    warning: diagram drift detected in components.drawio
```
