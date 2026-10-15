# Update quarter-planning skill
# Usage: .\scripts\update-quarter-planning.ps1 [-User] [-CheckOnly]

param(
    [switch]$User,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$REPO_PLANNING = "https://github.com/dermot-obrien/delivery-planning.git"

# Determine installation directory
if ($User) {
    $SKILLS_DIR = "$env:USERPROFILE\.agents\skills"
    Write-Host "📦 Updating user-level quarter-planning skill at: $SKILLS_DIR" -ForegroundColor Cyan
} else {
    $SKILLS_DIR = ".agents\skills"
    Write-Host "📦 Updating workspace-level quarter-planning skill at: $SKILLS_DIR" -ForegroundColor Cyan
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

# Function to get latest tag
function Get-LatestTag {
    $tags = git ls-remote --tags $REPO_PLANNING 2>&1 | Select-String "quarter-planning--v"
    if ($tags) {
        $tags = $tags | ForEach-Object { $_.ToString() -replace '.*refs/tags/', '' }
        $sorted = $tags | Sort-Object { [Version]($_ -replace '.*--v', '') }
        return $sorted[-1]
    }
    return "unknown"
}

Write-Host ""
Write-Host "🔍 Current version: $(Get-SkillVersion "$SKILLS_DIR\quarter-planning")" -ForegroundColor Yellow
Write-Host "🌐 Fetching latest version from GitHub..." -ForegroundColor Yellow
$LATEST_QP = Get-LatestTag
Write-Host "   Latest: $LATEST_QP"

if ($CheckOnly) {
    Write-Host ""
    Write-Host "✅ Check complete. Run without -CheckOnly to update." -ForegroundColor Green
    exit 0
}

Write-Host ""
$response = Read-Host "🔄 Update quarter-planning skill to $LATEST_QP? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "❌ Update cancelled." -ForegroundColor Red
    exit 0
}

# Download latest version
$TEMP_DIR = Join-Path $env:TEMP "quarter-planning-update-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host ""
Write-Host "📥 Downloading $LATEST_QP..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null

Push-Location $TEMP_DIR
git clone --depth 1 --branch $LATEST_QP $REPO_PLANNING delivery-planning 2>&1 | Out-Null
Pop-Location

# Backup and remove old installation
if (Test-Path "$SKILLS_DIR\quarter-planning") {
    Write-Host ""
    Write-Host "💾 Backing up current installation..." -ForegroundColor Yellow
    $BACKUP_DIR = ".skill-backups\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
    Copy-Item -Recurse "$SKILLS_DIR\quarter-planning" "$BACKUP_DIR\quarter-planning"
    Write-Host "   Backup saved to: $BACKUP_DIR"
    
    Write-Host "🗑️  Removing old installation..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "$SKILLS_DIR\quarter-planning"
}

# Install new version
Write-Host "📋 Installing $LATEST_QP..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null
Copy-Item -Recurse "$TEMP_DIR\delivery-planning\skills\quarter-planning" "$SKILLS_DIR\"

# Clean up
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $TEMP_DIR

# Verify
Write-Host ""
Write-Host "✅ Verifying installation..." -ForegroundColor Green
python "$SKILLS_DIR\quarter-planning\bin\check.py"

Write-Host ""
Write-Host "🎉 Update complete!" -ForegroundColor Green
Write-Host "📊 Installed version: $(Get-SkillVersion "$SKILLS_DIR\quarter-planning")" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check for new bindings: python $SKILLS_DIR\quarter-planning\bin\quarter.py --quarter <your-quarter> --where"
Write-Host "  2. Re-validate quarters: python $SKILLS_DIR\quarter-planning\bin\quarter.py --quarter <your-quarter> --validate"
Write-Host "  3. Review CHANGELOG for breaking changes"
