<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Updating

How to update the pattern, model, and markdown-deck skills to the latest versions.

## Automated update (recommended)

The repository includes scripts that automatically fetch the latest versions, backup your current installation, and verify the update:

### bash

```bash
# Download the update script
curl -o update-skills.sh https://raw.githubusercontent.com/dermot-obrien/architecture-pattern/main/scripts/update-skills.sh
chmod +x update-skills.sh

# Update workspace skills (.agents/skills)
./update-skills.sh

# Update user-level skills (~/.agents/skills)
./update-skills.sh --user

# Check versions without updating
./update-skills.sh --check-only
```

### PowerShell

```powershell
# Download the update script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dermot-obrien/architecture-pattern/main/scripts/update-skills.ps1" -OutFile "update-skills.ps1"

# Update workspace skills (.agents\skills)
.\update-skills.ps1

# Update user-level skills
.\update-skills.ps1 -User

# Check versions without updating
.\update-skills.ps1 -CheckOnly
```

### What the script does

1. Checks current vs latest versions
2. Backs up your current installation to `.skill-backups/`
3. Downloads and installs the latest versions of:
   - pattern
   - use-case
   - cross-reference
   - model
   - markdown-deck
4. Runs `npm install` for markdown-deck
5. Installs helper scripts to the pattern skill
6. Verifies all installations

## Manual update

**Important**: You must delete the old installations first to avoid stale files:

PowerShell:
```powershell
Remove-Item -Recurse -Force .agents/skills/pattern, .agents/skills/model, .agents/skills/markdown-deck
```

bash:
```bash
rm -rf .agents/skills/{pattern,model,markdown-deck}
```

Then reinstall using the same method you used initially:

- With `gh skill`: 
  ```bash
  gh skill install dermot-obrien/architecture-pattern pattern
  gh skill install dermot-obrien/diagram-model model
  gh skill install dermot-obrien/markdown-deck markdown-deck
  npm install --prefix .agents/skills/markdown-deck
  ```
  
- By copying: Follow the [install instructions](../README.md#install) again

### Verify the update

```bash
python .agents/skills/pattern/scripts/check.py
python .agents/skills/model/bin/model.py doctor --skill pattern
```

### Check for new bindings

New releases may add required configuration:

```bash
python .agents/skills/model/bin/model.py doctor --skill pattern --json
```

### Republish existing patterns

Verify they still build with the updated skills:

```bash
python .agents/skills/pattern/scripts/publish.py patterns/PAT-001-order-intake
```

**Always update all three skills together** (`pattern`, `model`, `markdown-deck`) because they have coordinated version dependencies.
