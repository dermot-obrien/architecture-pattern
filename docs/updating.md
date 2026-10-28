<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Updating

How to update the skills from this repository, and the `model` and `markdown-deck` skills they need, to the latest releases. The same script installs them the first time.

## With the script (recommended)

Run it from the root of the repository the skills are installed in. It works out how they were installed:

| The repository has | What the script does |
|---|---|
| Copies in `.agents/skills/` and no `.agents/skills.json` | Backs up each installed copy to `.skill-backups/<time>/`, installs every skill of the latest release (`pattern`, `use-case`, `cross-reference`, `portfolio`, `draft`, `convert`) with the latest `model` and `markdown-deck`, runs `npm install` for `markdown-deck`, and runs each skill's post-install check |
| A `.agents/skills.json` declaring its skills | Moves each declared skill to its latest release tag (the Architecture Continuum bundle to its latest release), adds any skill named with `-Skills`, writes the declaration, and reinstalls with the workspace's own installer (`scripts/architecture.mjs reinit`, else `scripts/skills.mjs sync --copy`) |

PowerShell:

```powershell
Set-Location C:\path\to\your\repository
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dermot-obrien/architecture-pattern/main/scripts/update-skills.ps1" -OutFile update-skills.ps1
.\update-skills.ps1 -CheckOnly   # what would change, changing nothing
.\update-skills.ps1
```

bash:

```bash
cd /path/to/your/repository
curl -fsSL https://raw.githubusercontent.com/dermot-obrien/architecture-pattern/main/scripts/update-skills.sh -o update-skills.sh
bash update-skills.sh --check-only
bash update-skills.sh
```

| Option | PowerShell | bash |
|---|---|---|
| Show what would change, change nothing | `-CheckOnly` | `--check-only` |
| Only these skills (copies), or add these skills (a declaration) | `-Skills pattern,use-case` | `--skills pattern,use-case` |
| Do not ask before changing anything | `-Yes` | `--yes` |

It needs git, Node 18 or later and Python 3.11 or later. Add `.agents/skills/` and `.skill-backups/` to `.gitignore`; in a declared workspace, commit `.agents/skills.json` and `.agents/skills.lock.json` afterwards.

## By hand

Delete the old copies first: copying over the top leaves files a release removed.

PowerShell:

```powershell
Remove-Item -Recurse -Force .agents/skills/pattern, .agents/skills/use-case, .agents/skills/model, .agents/skills/markdown-deck
```

bash:

```bash
rm -rf .agents/skills/{pattern,use-case,model,markdown-deck}
```

Then install again the way you did the first time: the [git route](../README.md#with-git-for-any-agent) at the current tags, or with `gh skill`:

```bash
gh skill install dermot-obrien/architecture-pattern pattern
gh skill install dermot-obrien/architecture-pattern use-case
gh skill install dermot-obrien/diagram-model model
gh skill install dermot-obrien/markdown-deck markdown-deck
npm install --prefix .agents/skills/markdown-deck
```

Add `cross-reference`, `portfolio`, `draft` or `convert` the same way if you use them.

## After any update

```bash
python .agents/skills/pattern/scripts/check.py
python .agents/skills/model/bin/model.py doctor --skill pattern --json   # a new release may add a binding
python .agents/skills/pattern/scripts/publish.py patterns/AP-001-order-intake   # an existing pattern still builds
```

Update `pattern`, `model` and `markdown-deck` together: their versions are coordinated, and `pattern` names the ones it needs in its `SKILL.md`. Read each skill's `CHANGELOG.md` for anything a workspace must change.
