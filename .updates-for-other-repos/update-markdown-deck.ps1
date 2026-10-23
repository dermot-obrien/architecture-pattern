# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
# Update markdown-deck skill
# Usage: .\scripts\update-markdown-deck.ps1 [-User] [-CheckOnly]

param(
    [switch]$User,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$REPO_DECK = "https://github.com/dermot-obrien/markdown-deck.git"

# Determine installation directory
if ($User) {
    $SKILLS_DIR = "$env:USERPROFILE\.agents\skills"
    Write-Host "📦 Updating user-level markdown-deck skill at: $SKILLS_DIR" -ForegroundColor Cyan
} else {
    $SKILLS_DIR = ".agents\skills"
    Write-Host "📦 Updating workspace-level markdown-deck skill at: $SKILLS_DIR" -ForegroundColor Cyan
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
    $tags = git ls-remote --tags $REPO_DECK 2>&1 | Select-String "markdown-deck--v"
    if ($tags) {
        $tags = $tags | ForEach-Object { $_.ToString() -replace '.*refs/tags/', '' }
        $sorted = $tags | Sort-Object { [Version]($_ -replace '.*--v', '') }
        return $sorted[-1]
    }
    return "unknown"
}

Write-Host ""
Write-Host "🔍 Current version: $(Get-SkillVersion "$SKILLS_DIR\markdown-deck")" -ForegroundColor Yellow
Write-Host "🌐 Fetching latest version from GitHub..." -ForegroundColor Yellow
$LATEST_DECK = Get-LatestTag
Write-Host "   Latest: $LATEST_DECK"

if ($CheckOnly) {
    Write-Host ""
    Write-Host "✅ Check complete. Run without -CheckOnly to update." -ForegroundColor Green
    exit 0
}

Write-Host ""
$response = Read-Host "🔄 Update markdown-deck skill to $LATEST_DECK? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "❌ Update cancelled." -ForegroundColor Red
    exit 0
}

# Download latest version
$TEMP_DIR = Join-Path $env:TEMP "markdown-deck-update-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host ""
Write-Host "📥 Downloading $LATEST_DECK..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TEMP_DIR | Out-Null

Push-Location $TEMP_DIR
git clone --depth 1 --branch $LATEST_DECK $REPO_DECK markdown-deck 2>&1 | Out-Null
Pop-Location

# Backup and remove old installation
if (Test-Path "$SKILLS_DIR\markdown-deck") {
    Write-Host ""
    Write-Host "💾 Backing up current installation..." -ForegroundColor Yellow
    $BACKUP_DIR = ".skill-backups\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
    Copy-Item -Recurse "$SKILLS_DIR\markdown-deck" "$BACKUP_DIR\markdown-deck"
    Write-Host "   Backup saved to: $BACKUP_DIR"
    
    Write-Host "🗑️  Removing old installation..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "$SKILLS_DIR\markdown-deck"
}

# Install new version
Write-Host "📋 Installing $LATEST_DECK..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null
Copy-Item -Recurse "$TEMP_DIR\markdown-deck\skills\markdown-deck" "$SKILLS_DIR\"

# Install npm dependencies
Write-Host ""
Write-Host "📦 Installing npm dependencies..." -ForegroundColor Cyan
npm install --prefix "$SKILLS_DIR\markdown-deck" --no-audit --no-fund

# Clean up
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $TEMP_DIR

# Verify
Write-Host ""
Write-Host "✅ Verifying installation..." -ForegroundColor Green
node "$SKILLS_DIR\markdown-deck\bin\check.mjs"

Write-Host ""
Write-Host "🎉 Update complete!" -ForegroundColor Green
Write-Host "📊 Installed version: $(Get-SkillVersion "$SKILLS_DIR\markdown-deck")" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Rebuild existing decks: node $SKILLS_DIR\markdown-deck\bin\markdown-deck.mjs build <file> --out <dir>"
Write-Host "  2. Check your bindings: node $SKILLS_DIR\markdown-deck\bin\check.mjs"
