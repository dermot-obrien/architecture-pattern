# Automated Update Scripts - Complete Implementation

This document describes the automated update scripts added to all skill repositories to simplify skill maintenance and reduce update errors.

## ✅ What Was Implemented

### 1. architecture-pattern Repository (Committed & Pushed)

**Commits:**
- `85da51f` - feat: add automated update scripts for all skills
- `a6737c1` - docs: add documentation update summary and README files for other repositories  
- `1dde609` - docs: add quick start and comprehensive update instructions to all skill READMEs

**New Files:**

#### Update Scripts (Repository Root)
- `scripts/update-skills.sh` (bash, 171 lines) - Updates pattern, use-case, cross-reference, model, and markdown-deck
- `scripts/update-skills.ps1` (PowerShell, 188 lines) - PowerShell equivalent

**Features:**
- Checks current vs latest versions from GitHub tags
- Automatically detects workspace vs user-level installations
- Backs up current installations to `.skill-backups/YYYYMMDD-HHMMSS/`
- Downloads latest versions at coordinated release tags
- Installs all 5 skills with proper dependency versions
- Runs `npm install` for markdown-deck automatically
- Verifies all installations with their check scripts
- Shows before/after versions
- `--user` flag for user-level updates
- `--check-only` flag to check versions without updating

#### Updated Documentation
- `skills/pattern/README.md` - Added "Automated Update (Recommended)" section
- `skills/use-case/README.md` - Added automated update section
- `skills/cross-reference/README.md` - Added automated update section

### 2. Other Repositories (Ready for Distribution)

**Location:** `.updates-for-other-repos/`

#### For diagram-model Repository
- `update-model.sh` (bash, 101 lines)
- `update-model.ps1` (PowerShell, 112 lines)
- `model-README.md` (updated with automated update section)

**Copy to diagram-model:**
```bash
cp update-model.sh scripts/
cp update-model.ps1 scripts/
cp model-README.md skills/model/README.md
```

#### For markdown-deck Repository
- `update-markdown-deck.sh` (bash, 107 lines)  
- `update-markdown-deck.ps1` (PowerShell, 118 lines)
- `markdown-deck-README.md` (updated with automated update section)

**Copy to markdown-deck:**
```bash
cp update-markdown-deck.sh scripts/
cp update-markdown-deck.ps1 scripts/
cp markdown-deck-README.md skills/markdown-deck/README.md
```

#### For delivery-planning Repository
- `update-quarter-planning.sh` (bash, 108 lines)
- `update-quarter-planning.ps1` (PowerShell, 119 lines)
- `quarter-planning-README.md` (updated with automated update section)

**Copy to delivery-planning:**
```bash
cp update-quarter-planning.sh scripts/
cp update-quarter-planning.ps1 scripts/
cp quarter-planning-README.md skills/quarter-planning/README.md
```

---

## 🚀 How to Use the Update Scripts

### architecture-pattern (All Skills)

```bash
# bash - workspace level
./scripts/update-skills.sh

# bash - user level  
./scripts/update-skills.sh --user

# bash - check only (no changes)
./scripts/update-skills.sh --check-only

# PowerShell - workspace level
.\scripts\update-skills.ps1

# PowerShell - user level
.\scripts\update-skills.ps1 -User

# PowerShell - check only
.\scripts\update-skills.ps1 -CheckOnly
```

### Individual Skills

Each repository has its own update script following the same pattern:

**diagram-model:**
```bash
./scripts/update-model.sh [--user] [--check-only]
.\scripts\update-model.ps1 [-User] [-CheckOnly]
```

**markdown-deck:**
```bash
./scripts/update-markdown-deck.sh [--user] [--check-only]
.\scripts\update-markdown-deck.ps1 [-User] [-CheckOnly]
```

**delivery-planning:**
```bash
./scripts/update-quarter-planning.sh [--user] [--check-only]
.\scripts\update-quarter-planning.ps1 [-User] [-CheckOnly]
```

---

## 🔧 Script Features

### Common to All Scripts

1. **Version Checking**
   - Queries GitHub API for latest release tags
   - Compares with currently installed version
   - Shows current → latest version

2. **Safe Updates**
   - Confirms before proceeding
   - Backs up current installation to `.skill-backups/`
   - Allows rollback if needed

3. **Automatic Installation**
   - Clones at specific release tag
   - Copies to correct location
   - Runs required setup (npm install for markdown-deck)
   - Cleans up temporary files

4. **Verification**
   - Runs post-install checks
   - Shows final installed version
   - Suggests next steps

5. **Flexibility**
   - Works for workspace or user installations
   - Check-only mode for CI/automated checks
   - Handles both .agents/skills and ~/.agents/skills

### architecture-pattern Specific

Updates **5 skills** in coordinated versions:
- pattern
- use-case  
- cross-reference
- model (from diagram-model repo)
- markdown-deck (from markdown-deck repo)

Ensures version compatibility across all dependencies.

---

## 📋 Script Output Example

```
📦 Updating workspace-level skills at: .agents/skills

🔍 Checking current versions...
  pattern:          0.10.3
  use-case:         0.2.0
  cross-reference:  0.2.0
  model:            0.8.2
  markdown-deck:    0.6.8

🌐 Fetching latest versions from GitHub...
  Latest pattern:          pattern--v0.11.0
  Latest use-case:         use-case--v0.3.0
  Latest cross-reference:  cross-reference--v0.3.0
  Latest model:            model--v0.9.0
  Latest markdown-deck:    markdown-deck--v0.6.8

🔄 Update skills to latest versions? (y/N) y

📥 Downloading latest versions...
  Cloning architecture-pattern...
  Cloning diagram-model...
  Cloning markdown-deck...

💾 Backing up current installations...
  Backups saved to: .skill-backups/20261015-204500

🗑️  Removing old installations...

📋 Installing new versions...
  Installing pattern...
  Installing use-case...
  Installing cross-reference...
  Installing model...
  Installing markdown-deck...

📦 Installing npm dependencies for markdown-deck...

🧹 Cleaning up...

✅ Verifying installation...
[check output from each skill]

🎉 Update complete!

📊 Installed versions:
  pattern:          0.11.0
  use-case:         0.3.0
  cross-reference:  0.3.0
  model:            0.9.0
  markdown-deck:    0.6.8

💡 Next steps:
  1. Re-validate your patterns: python .agents/skills/model/bin/model.py scan patterns --recursive
  2. Republish any existing patterns: python .agents/skills/pattern/scripts/publish.py <folder>
  3. Check your bindings: python .agents/skills/model/bin/model.py doctor --skill pattern
```

---

## 🎯 Benefits

### For Users

1. **One Command Updates** - No need to remember multiple repos and version compatibility
2. **Safe Updates** - Automatic backups before any changes
3. **Verified Installs** - Post-update checks ensure everything works
4. **Clear Feedback** - Shows exactly what's happening at each step
5. **Flexible** - Works for both workspace and user installations

### For Maintainers

1. **Reduces Support** - Fewer "how do I update?" questions
2. **Version Coordination** - Scripts handle coordinated releases automatically
3. **Testing Helper** - `--check-only` flag useful for CI checks
4. **Consistent Process** - Same update process across all skills

### Technical Quality

1. **Error Handling** - Scripts exit cleanly on errors
2. **Rollback Capability** - Backups enable quick rollback
3. **Cross-Platform** - Both bash and PowerShell supported
4. **No Manual npm install** - Automated for markdown-deck
5. **Version Validation** - Checks GitHub tags, not arbitrary commits

---

## 📊 Code Statistics

| Repository | Script Lines | README Updates | Total Changes |
|---|---|---|---|
| **architecture-pattern** | 359 (sh + ps1) | +159 lines | +518 lines |
| **diagram-model** | 213 (sh + ps1) | +89 lines | +302 lines |
| **markdown-deck** | 225 (sh + ps1) | +98 lines | +323 lines |
| **delivery-planning** | 227 (sh + ps1) | +93 lines | +320 lines |
| **TOTAL** | **1,024 lines** | **+439 lines** | **1,463 lines** |

---

## 🔄 Workflow for Other Repositories

### For diagram-model Maintainer

1. **Copy scripts:**
   ```bash
   cd /path/to/diagram-model
   mkdir -p scripts
   cp /path/to/architecture-pattern/.updates-for-other-repos/update-model.* scripts/
   chmod +x scripts/update-model.sh
   ```

2. **Update README:**
   ```bash
   cp /path/to/architecture-pattern/.updates-for-other-repos/model-README.md skills/model/README.md
   ```

3. **Commit:**
   ```bash
   git add scripts/update-model.* skills/model/README.md
   git commit -m "feat: add automated update script and enhanced skill README"
   ```

### For markdown-deck Maintainer

Same process using `update-markdown-deck.*` and `markdown-deck-README.md`

### For delivery-planning Maintainer

Same process using `update-quarter-planning.*` and `quarter-planning-README.md`

---

## ✅ Testing Performed

### architecture-pattern Scripts

- ✅ Version checking works correctly
- ✅ Backup creates timestamped directories
- ✅ Downloads correct release tags
- ✅ Installs to correct locations
- ✅ npm install runs for markdown-deck
- ✅ Post-install checks execute
- ✅ `--check-only` flag works
- ✅ `--user` flag targets correct directory
- ✅ PowerShell and bash scripts equivalent

### Error Handling

- ✅ Exits cleanly when user cancels
- ✅ Handles missing installations gracefully  
- ✅ Reports GitHub connection issues
- ✅ Validates git and npm availability

---

## 🎓 Design Decisions

### Why Shell Scripts?

1. **No Dependencies** - Works with standard shell/PowerShell
2. **Direct Control** - Full control over git, npm, file operations
3. **Cross-Platform** - bash (Unix) + PowerShell (Windows)
4. **Inspectable** - Users can read and understand the script
5. **CI Friendly** - Easy to run in automated workflows

### Why Backup Before Update?

1. **Safety** - Enables quick rollback if issues found
2. **Confidence** - Users more willing to update
3. **Debugging** - Can compare old vs new if problems occur
4. **Timestamped** - Multiple backups retained

### Why --check-only Flag?

1. **CI Integration** - Automated version checks
2. **Preview** - Users can see what would update
3. **Scheduled Checks** - Cron jobs to monitor updates
4. **No Surprises** - Know what's new before updating

---

## 📚 Documentation Organization

```
architecture-pattern/
├── scripts/
│   ├── update-skills.sh           ← Users run this
│   ├── update-skills.ps1          ← PowerShell users run this
│   ├── validate-skills.mjs        ← Existing
│   └── validate-bundle.mjs        ← Existing
├── skills/
│   ├── pattern/README.md          ← References update-skills.*
│   ├── use-case/README.md         ← References update-skills.*
│   └── cross-reference/README.md  ← References update-skills.*
├── .updates-for-other-repos/      ← For distribution
│   ├── update-model.*             ← For diagram-model
│   ├── update-markdown-deck.*     ← For markdown-deck
│   ├── update-quarter-planning.*  ← For delivery-planning
│   ├── model-README.md            ← Updated README
│   ├── markdown-deck-README.md    ← Updated README
│   └── quarter-planning-README.md ← Updated README
└── DOCUMENTATION_UPDATES.md       ← Overview of all doc changes
```

---

## 🎉 Summary

**Three commits, 1,463 lines of code and documentation** added to streamline skill updates across four repositories:

1. **Automated update scripts** (bash + PowerShell) for all skills
2. **Enhanced READMEs** with quick start and update sections  
3. **Ready-to-distribute** files for other repositories

**Result:** Users can now update all skills with one command, with automatic backups, version coordination, and verification.

---

Generated: 2026-10-15  
Agent: Claude Sonnet 4.5 (Cursor Cloud Agent)  
Repository: architecture-pattern (main branch)  
Commits: `85da51f`, `a6737c1`, `1dde609`
