# SPDX-License-Identifier: Apache-2.0
#
# Install the architecture-pattern skills and the two they need (model, markdown-deck) into a
# repository, or update an installation to the latest releases.
#
#   .\update-skills.ps1 [-CheckOnly] [-Skills pattern,use-case,...] [-Yes]
#
# Run from the root of the repository to install into.
#
# With a .agents/skills.json (a workspace that declares its skills, as Architecture Continuum's
# installer does): moves every source it knows to its latest release tag (a skill from its own
# repository to <skill>--vX.Y.Z; the Architecture Continuum bundle to its latest release), adds
# any skill named in -Skills that is not declared yet, then reinstalls with the workspace's own
# installer. Sources it does not know are left as they are.
#
# Without one: copies the skills from the latest release into .agents/skills, every skill the
# release ships (pattern, use-case, cross-reference, portfolio, draft, convert) unless -Skills
# names some, with model and markdown-deck, backing up any installed copy first. A first install
# and an update are the same run.
#
# -CheckOnly shows what would change and changes nothing. -Yes skips the confirmation.
# Windows PowerShell 5 or later; needs git, Node 18 or later and Python 3.11 or later.

param(
    [switch]$CheckOnly,
    [string[]]$Skills,
    [switch]$Yes
)

# Native tools write notes to stderr; failures are read from $LASTEXITCODE instead.
$ErrorActionPreference = "Continue"

$REPO_PATTERN = "https://github.com/dermot-obrien/architecture-pattern.git"
$REPO_MODEL = "https://github.com/dermot-obrien/diagram-model.git"
$REPO_DECK = "https://github.com/dermot-obrien/markdown-deck.git"
$REPO_CONTINUUM = "https://github.com/dermot-obrien/architecture-continuum.git"
$SKILLS_DIR = ".agents\skills"
$DECLARATION = ".agents\skills.json"

function Get-LatestTag {
    param([string]$Repo, [string]$Prefix)
    $lines = git ls-remote --tags $Repo 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $pattern = "refs/tags/(" + [regex]::Escape($Prefix) + "(\d+\.\d+\.\d+))$"
    $best = $null; $bestVersion = $null
    foreach ($line in $lines) {
        if ($line -match $pattern) {
            $version = [version]$Matches[2]
            if (-not $bestVersion -or $version -gt $bestVersion) { $bestVersion = $version; $best = $Matches[1] }
        }
    }
    return $best
}

# Architecture Continuum's latest published release, which a stray tag cannot outrank.
function Get-ContinuumRelease {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/dermot-obrien/architecture-continuum/releases/latest" -Headers @{ "User-Agent" = "update-skills" } -UseBasicParsing
        if ($release.tag_name) { return $release.tag_name }
    } catch { }
    return (Get-LatestTag $REPO_CONTINUUM "v")
}

function Get-SkillVersion {
    param([string]$SkillPath)
    $skillMd = Join-Path $SkillPath "SKILL.md"
    if ((Test-Path $skillMd) -and ((Get-Content $skillMd -Raw) -match 'version:\s*"([^"]+)"')) { return $Matches[1] }
    return "not installed"
}

function Confirm-Step {
    param([string]$Question)
    if ($Yes) { return $true }
    $answer = Read-Host "$Question (y/N)"
    return ($answer -eq "y" -or $answer -eq "Y")
}

foreach ($tool in @("git", "node")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { Write-Host "$tool is not on the PATH." -ForegroundColor Red; exit 2 }
}
if (-not (Test-Path ".git")) {
    Write-Host "WARNING: no .git here. Skills go into $(Join-Path (Get-Location) $SKILLS_DIR)." -ForegroundColor Yellow
    if (-not (Confirm-Step "Continue anyway?")) { Write-Host "Cancelled."; exit 0 }
}

if (Test-Path $DECLARATION) {
    # A declared workspace: move the pins, then reinstall with its own installer.
    Write-Host "Reading $DECLARATION and finding the latest releases..." -ForegroundColor Cyan
    $json = Get-Content -Raw $DECLARATION | ConvertFrom-Json
    $changes = 0
    foreach ($s in $json.sources) {
        if ($s.bundle -and $s.bundle -match "dermot-obrien/(architecture-continuum|ai-assisted-architecture)(\.git)?$") {
            $tag = Get-ContinuumRelease
            if ($tag -and ($s.ref -ne $tag -or $s.bundle -ne $REPO_CONTINUUM)) {
                Write-Host ("  {0,-24} {1} -> {2}" -f "architecture-continuum", $s.ref, $tag)
                $s.bundle = $REPO_CONTINUUM; $s.ref = $tag; $changes++
            }
        } elseif ($s.repo -and $s.name) {
            $tag = Get-LatestTag $s.repo "$($s.name)--v"
            if ($tag -and $s.ref -ne $tag) {
                Write-Host ("  {0,-24} {1} -> {2}" -f $s.name, $s.ref, $tag)
                $s.ref = $tag; $changes++
            }
        }
    }
    $declared = @($json.sources | Where-Object { $_.name } | ForEach-Object { $_.name })
    foreach ($name in $Skills) {
        if ($declared -notcontains $name) {
            $tag = Get-LatestTag $REPO_PATTERN "$name--v"
            if (-not $tag) { Write-Host "architecture-pattern has no release of a skill called $name." -ForegroundColor Red; exit 2 }
            Write-Host ("  {0,-24} added at {1}" -f $name, $tag)
            $json.sources += [pscustomobject]@{ repo = $REPO_PATTERN; ref = $tag; path = "skills/$name"; name = $name }
            $changes++
        }
    }
    if ($changes -eq 0) { Write-Host "Every source this script knows is at its latest release." -ForegroundColor Green }
    if ($CheckOnly) { Write-Host "Check only: nothing changed."; exit 0 }
    if ($changes -gt 0) {
        if (-not (Confirm-Step "Change these and reinstall?")) { Write-Host "Cancelled."; exit 0 }
        [System.IO.File]::WriteAllText((Join-Path (Get-Location) $DECLARATION), (($json | ConvertTo-Json -Depth 10) + "`n"))
        Write-Host "Updated $DECLARATION."
    }
    if (Test-Path "scripts/architecture.mjs") {
        node scripts/architecture.mjs reinit
    } elseif (Test-Path "scripts/skills.mjs") {
        node scripts/skills.mjs sync --copy
    } else {
        Write-Host "This workspace declares its skills but has no installer: copy AI-Assisted Work's bin/skills.mjs to scripts/skills.mjs, or run Architecture Continuum's update-skills script." -ForegroundColor Yellow
        exit 2
    }
    if ($LASTEXITCODE -ne 0) { Write-Host "The reinstall stopped (exit $LASTEXITCODE); its output says why." -ForegroundColor Red; exit $LASTEXITCODE }
    if (Test-Path "scripts/skills.mjs") { node scripts/skills.mjs check }
    Write-Host ""
    Write-Host "Done. Read each release's changelog for anything a workspace must change, then commit .agents/skills.json and .agents/skills.lock.json." -ForegroundColor Green
    exit 0
}

# Copies in .agents/skills: install or update from the latest release.
Write-Host "Finding the latest releases..." -ForegroundColor Cyan
$LATEST_PATTERN = Get-LatestTag $REPO_PATTERN "pattern--v"
$LATEST_MODEL = Get-LatestTag $REPO_MODEL "model--v"
$LATEST_DECK = Get-LatestTag $REPO_DECK "markdown-deck--v"
if (-not $LATEST_PATTERN -or -not $LATEST_MODEL -or -not $LATEST_DECK) {
    Write-Host "Could not read the release tags from GitHub. Check the network and try again." -ForegroundColor Red
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$TEMP_DIR = ".skill-update-temp-$timestamp"
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null
try {
    foreach ($clone in @(@($REPO_PATTERN, $LATEST_PATTERN, "architecture-pattern"), @($REPO_MODEL, $LATEST_MODEL, "diagram-model"), @($REPO_DECK, $LATEST_DECK, "markdown-deck"))) {
        git -c advice.detachedHead=false clone --quiet --depth 1 --branch $clone[1] $clone[0] "$TEMP_DIR\$($clone[2])"
        if ($LASTEXITCODE -ne 0) { throw "could not fetch $($clone[2]) at $($clone[1])" }
    }
    $bundle = Get-Content -Raw "$TEMP_DIR\architecture-pattern\bundle.json" | ConvertFrom-Json
    $released = @($bundle.skills | ForEach-Object { $_.name })
    $wanted = if ($Skills) { $Skills } else { $released }
    foreach ($name in $wanted) {
        if ($released -notcontains $name) { throw "release $LATEST_PATTERN has no skill called $name; it has $($released -join ', ')" }
    }

    Write-Host ""
    Write-Host ("  {0,-18} {1,-16} {2}" -f "skill", "installed", "release")
    foreach ($skill in $bundle.skills | Where-Object { $wanted -contains $_.name }) {
        Write-Host ("  {0,-18} {1,-16} {2}" -f $skill.name, (Get-SkillVersion "$SKILLS_DIR\$($skill.name)"), $skill.version)
    }
    Write-Host ("  {0,-18} {1,-16} {2}" -f "model", (Get-SkillVersion "$SKILLS_DIR\model"), ($LATEST_MODEL -replace '.*--v', ''))
    Write-Host ("  {0,-18} {1,-16} {2}" -f "markdown-deck", (Get-SkillVersion "$SKILLS_DIR\markdown-deck"), ($LATEST_DECK -replace '.*--v', ''))

    if ($CheckOnly) { Write-Host ""; Write-Host "Check only: nothing changed."; return }
    if (-not (Confirm-Step "Install these into $SKILLS_DIR?")) { Write-Host "Cancelled."; return }

    $targets = @($wanted) + @("model", "markdown-deck")
    $BACKUP_DIR = ".skill-backups\$timestamp"
    foreach ($name in $targets) {
        $path = "$SKILLS_DIR\$name"
        if (Test-Path $path) {
            robocopy $path "$BACKUP_DIR\$name" /E /XD node_modules /NFL /NDL /NJH /NJS | Out-Null
            if ($LASTEXITCODE -ge 8) { Write-Host "  Warning: $name may not be fully backed up" -ForegroundColor Yellow }
            Remove-Item -Recurse -Force $path
        }
    }
    if (Test-Path $BACKUP_DIR) { Write-Host "Backed up the old copies to $BACKUP_DIR (node_modules left out)." }

    New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null
    foreach ($skill in $bundle.skills | Where-Object { $wanted -contains $_.name }) {
        Copy-Item -Recurse "$TEMP_DIR\architecture-pattern\$($skill.path)" "$SKILLS_DIR\"
        Write-Host "  installed $($skill.name) $($skill.version)"
    }
    Copy-Item -Recurse "$TEMP_DIR\diagram-model\skills\model" "$SKILLS_DIR\"
    Write-Host "  installed model $($LATEST_MODEL -replace '.*--v', '')"
    Copy-Item -Recurse "$TEMP_DIR\markdown-deck\skills\markdown-deck" "$SKILLS_DIR\"
    Write-Host "  installed markdown-deck $($LATEST_DECK -replace '.*--v', '')"
    if ($wanted -contains "pattern") {
        foreach ($helper in @("list-patterns.ps1", "list-patterns.sh")) {
            if (Test-Path "$TEMP_DIR\architecture-pattern\scripts\$helper") { Copy-Item "$TEMP_DIR\architecture-pattern\scripts\$helper" "$SKILLS_DIR\pattern\scripts\" -Force }
        }
    }

    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "Installing markdown-deck's npm packages..." -ForegroundColor Cyan
    npm install --prefix "$SKILLS_DIR\markdown-deck" --no-audit --no-fund 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "  npm install failed: run npm install --prefix $SKILLS_DIR\markdown-deck" -ForegroundColor Yellow }

    Write-Host ""
    Write-Host "Running each skill's post-install check (binding warnings are normal before .agents\skill-bindings.toml exists)..." -ForegroundColor Cyan
    foreach ($skill in $bundle.skills | Where-Object { $wanted -contains $_.name }) {
        $command = @($skill.check.command)
        if ($command.Count -lt 2) { continue }
        $script = Join-Path "$SKILLS_DIR\$($skill.name)" $command[1]
        Write-Host "$($skill.name):"
        & $command[0] $script @($command | Select-Object -Skip 2) 2>&1 | Select-Object -First 8 | ForEach-Object { Write-Host "  $_" }
    }
} catch {
    Write-Host "Stopped: $_" -ForegroundColor Red
    exit 1
} finally {
    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
}

if (-not $CheckOnly) {
    Write-Host ""
    Write-Host "Done. Add .agents/skills/ to .gitignore if it is not there. Next:" -ForegroundColor Green
    Write-Host "  1. Bind the skills: .agents\skill-bindings.toml (docs/quick-start.md, step 3)"
    Write-Host "  2. Check the bindings: python $SKILLS_DIR\model\bin\model.py doctor --skill pattern"
    Write-Host "  3. Re-validate existing documents: python $SKILLS_DIR\model\bin\model.py scan <folder> --recursive"
}
exit 0
