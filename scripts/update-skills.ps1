# Update architecture-pattern skills and dependencies
# Usage: .\scripts\update-skills.ps1 [-User] [-CheckOnly]

param(
    [switch]$User,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

# Configuration
$REPO_PATTERN = "https://github.com/dermot-obrien/architecture-pattern.git"
$REPO_MODEL = "https://github.com/dermot-obrien/diagram-model.git"
$REPO_DECK = "https://github.com/dermot-obrien/markdown-deck.git"

# Determine installation directory
if ($User) {
    $SKILLS_DIR = "$env:USERPROFILE\.agents\skills"
    Write-Host "Updating user-level skills at: $SKILLS_DIR" -ForegroundColor Cyan
} else {
    $SKILLS_DIR = ".agents\skills"
    Write-Host "Updating workspace-level skills at: $SKILLS_DIR" -ForegroundColor Cyan
}

# Function to get current version
function Get-SkillVersion {
    param($SkillPath)
    $skillMd = "$SkillPath\SKILL.md"
    if (Test-Path $skillMd) {
        $content = Get-Content $skillMd -Raw
        if ($content -match 'version:\s*"([^"]+)"') {
            return $matches[1]
        }
    }
    return "not installed"
}

# Function to get latest tag for a skill
function Get-LatestTag {
    param($Repo, $Skill)
    $tags = git ls-remote --tags $Repo 2>&1 | Select-String "$Skill--v"
    if ($tags) {
        $tags = $tags | ForEach-Object { $_.ToString() -replace '.*refs/tags/', '' }
        $sorted = $tags | Sort-Object {
            $versionStr = ($_ -replace '.*--v', '')
            try {
                [Version]$versionStr
            } catch {
                [Version]"0.0.0"
            }
        }
        return $sorted[-1]
    }
    return "unknown"
}

Write-Host ""
Write-Host "Checking current versions..." -ForegroundColor Yellow
Write-Host "  pattern:          $(Get-SkillVersion "$SKILLS_DIR\pattern")"
Write-Host "  use-case:         $(Get-SkillVersion "$SKILLS_DIR\use-case")"
Write-Host "  cross-reference:  $(Get-SkillVersion "$SKILLS_DIR\cross-reference")"
Write-Host "  model:            $(Get-SkillVersion "$SKILLS_DIR\model")"
Write-Host "  markdown-deck:    $(Get-SkillVersion "$SKILLS_DIR\markdown-deck")"

Write-Host ""
Write-Host "Fetching latest versions from GitHub..." -ForegroundColor Yellow
$LATEST_PATTERN = Get-LatestTag $REPO_PATTERN "pattern"
$LATEST_USE_CASE = Get-LatestTag $REPO_PATTERN "use-case"
$LATEST_XREF = Get-LatestTag $REPO_PATTERN "cross-reference"
$LATEST_MODEL = Get-LatestTag $REPO_MODEL "model"
$LATEST_DECK = Get-LatestTag $REPO_DECK "markdown-deck"

Write-Host "  Latest pattern:          $LATEST_PATTERN"
Write-Host "  Latest use-case:         $LATEST_USE_CASE"
Write-Host "  Latest cross-reference:  $LATEST_XREF"
Write-Host "  Latest model:            $LATEST_MODEL"
Write-Host "  Latest markdown-deck:    $LATEST_DECK"

# Check if any tags are unknown
if ($LATEST_PATTERN -eq "unknown" -or $LATEST_MODEL -eq "unknown" -or $LATEST_DECK -eq "unknown") {
    Write-Host ""
    Write-Host "Error: Unable to fetch latest versions from GitHub." -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Red
    exit 1
}

if ($CheckOnly) {
    Write-Host ""
    Write-Host "Check complete. Run without -CheckOnly to update." -ForegroundColor Green
    exit 0
}

# Confirm update
Write-Host ""
$response = Read-Host "Update skills to latest versions? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Update cancelled." -ForegroundColor Red
    exit 0
}

# Create temp directory in the current location (avoids long paths and spaces in AppData)
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$TEMP_DIR = ".skill-update-temp-$timestamp"
Write-Host ""
Write-Host "Downloading latest versions to $TEMP_DIR..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null

# Clone repositories at latest tags
Push-Location $TEMP_DIR
try {
    Write-Host "  Cloning architecture-pattern..."
    $ErrorActionPreference = "Continue"
    git clone --depth 1 --branch $LATEST_PATTERN $REPO_PATTERN architecture-pattern 2>&1 | ForEach-Object { 
        if ($_ -match "fatal:|error:") { 
            Write-Host $_ -ForegroundColor Red 
        }
    }
    $ErrorActionPreference = "Stop"
    if ($LASTEXITCODE -ne 0) { 
        throw "Failed to clone architecture-pattern (exit code: $LASTEXITCODE)" 
    }
    
    Write-Host "  Cloning diagram-model..."
    $ErrorActionPreference = "Continue"
    git clone --depth 1 --branch $LATEST_MODEL $REPO_MODEL diagram-model 2>&1 | ForEach-Object { 
        if ($_ -match "fatal:|error:") { 
            Write-Host $_ -ForegroundColor Red 
        }
    }
    $ErrorActionPreference = "Stop"
    if ($LASTEXITCODE -ne 0) { 
        throw "Failed to clone diagram-model (exit code: $LASTEXITCODE)" 
    }
    
    Write-Host "  Cloning markdown-deck..."
    $ErrorActionPreference = "Continue"
    git clone --depth 1 --branch $LATEST_DECK $REPO_DECK markdown-deck 2>&1 | ForEach-Object { 
        if ($_ -match "fatal:|error:") { 
            Write-Host $_ -ForegroundColor Red 
        }
    }
    $ErrorActionPreference = "Stop"
    if ($LASTEXITCODE -ne 0) { 
        throw "Failed to clone markdown-deck (exit code: $LASTEXITCODE)" 
    }
} catch {
    Pop-Location
    Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Clone error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "This might be due to:" -ForegroundColor Yellow
    Write-Host "  - Network connectivity issues" -ForegroundColor Yellow
    Write-Host "  - Git not installed or not in PATH" -ForegroundColor Yellow
    Write-Host "  - Missing or invalid repository tag" -ForegroundColor Yellow
    exit 1
}
Pop-Location

# Backup old installations
Write-Host ""
Write-Host "Backing up current installations..." -ForegroundColor Yellow
$BACKUP_DIR = ".skill-backups\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
$skills = @("pattern", "use-case", "cross-reference", "model", "markdown-deck")
foreach ($skill in $skills) {
    $skillPath = "$SKILLS_DIR\$skill"
    if (Test-Path $skillPath) {
        Write-Host "  Backing up $skill..."
        Copy-Item -Recurse $skillPath "$BACKUP_DIR\$skill"
    }
}
Write-Host "  Backups saved to: $BACKUP_DIR"

# Remove old installations
Write-Host ""
Write-Host "Removing old installations..." -ForegroundColor Yellow
foreach ($skill in $skills) {
    $skillPath = "$SKILLS_DIR\$skill"
    if (Test-Path $skillPath) {
        Write-Host "  Removing $skill..."
        Remove-Item -Recurse -Force $skillPath
    }
}

# Install new versions
Write-Host ""
Write-Host "Installing new versions..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null

Write-Host "  Installing pattern..."
Copy-Item -Recurse "$TEMP_DIR\architecture-pattern\skills\pattern" "$SKILLS_DIR\"

Write-Host "  Installing use-case..."
Copy-Item -Recurse "$TEMP_DIR\architecture-pattern\skills\use-case" "$SKILLS_DIR\"

Write-Host "  Installing cross-reference..."
Copy-Item -Recurse "$TEMP_DIR\architecture-pattern\skills\cross-reference" "$SKILLS_DIR\"

Write-Host "  Installing model..."
Copy-Item -Recurse "$TEMP_DIR\diagram-model\skills\model" "$SKILLS_DIR\"

Write-Host "  Installing markdown-deck..."
Copy-Item -Recurse "$TEMP_DIR\markdown-deck\skills\markdown-deck" "$SKILLS_DIR\"

# Install npm dependencies for markdown-deck
Write-Host ""
Write-Host "Installing npm dependencies for markdown-deck..." -ForegroundColor Cyan
$markdownDeckPath = Join-Path (Get-Location) "$SKILLS_DIR\markdown-deck"
if (Test-Path "$markdownDeckPath\package.json") {
    Push-Location $markdownDeckPath
    try {
        npm install --no-audit --no-fund 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Warning: npm install failed. Run manually:" -ForegroundColor Yellow
            Write-Host "  cd $markdownDeckPath" -ForegroundColor Yellow
            Write-Host "  npm install" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Warning: Could not install npm dependencies: $_" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Warning: markdown-deck package.json not found at: $markdownDeckPath" -ForegroundColor Yellow
    Write-Host "Skipping npm install. Install manually if needed." -ForegroundColor Yellow
}

# Clean up
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $TEMP_DIR

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Green
Write-Host ""
Write-Host "Note: Warnings about bindings or catalogue mappings are normal" -ForegroundColor Cyan
Write-Host "      if you haven't set up .agents\skill-bindings.toml yet" -ForegroundColor Cyan
Write-Host ""
Write-Host "pattern:"
python "$SKILLS_DIR\pattern\scripts\check.py" 2>&1 | Select-Object -First 10
Write-Host ""
Write-Host "use-case:"
python "$SKILLS_DIR\use-case\scripts\check.py" 2>&1 | Select-Object -First 10
Write-Host ""
Write-Host "cross-reference:"
node "$SKILLS_DIR\cross-reference\scripts\check.cjs" 2>&1 | Select-Object -First 10
Write-Host ""
Write-Host "model:"
python "$SKILLS_DIR\model\bin\model.py" doctor 2>&1 | Select-Object -First 10

Write-Host ""
Write-Host "Update complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Installed versions:" -ForegroundColor Cyan
Write-Host "  pattern:          $(Get-SkillVersion "$SKILLS_DIR\pattern")"
Write-Host "  use-case:         $(Get-SkillVersion "$SKILLS_DIR\use-case")"
Write-Host "  cross-reference:  $(Get-SkillVersion "$SKILLS_DIR\cross-reference")"
Write-Host "  model:            $(Get-SkillVersion "$SKILLS_DIR\model")"
Write-Host "  markdown-deck:    $(Get-SkillVersion "$SKILLS_DIR\markdown-deck")"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Set up skill bindings if needed: create .agents\skill-bindings.toml"
Write-Host "     See: https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/quick-start.md"
Write-Host "  2. Check bindings: python $SKILLS_DIR\model\bin\model.py doctor --skill pattern"
Write-Host "  3. Re-validate existing content: python $SKILLS_DIR\model\bin\model.py scan <your-folder> --recursive"
Write-Host ""
Write-Host "Note: Catalogue mapping warnings are normal if you haven't created .agents\skill-bindings.toml yet" -ForegroundColor Cyan
