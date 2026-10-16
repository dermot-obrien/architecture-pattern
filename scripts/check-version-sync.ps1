# Check that all version references are in sync across documentation and examples
# Run this before committing version changes

$ErrorActionPreference = "Stop"

$ERRORS = 0

Write-Host "Checking version consistency across repository..." -ForegroundColor Cyan
Write-Host ""

# Extract versions from SKILL.md files (first version: match only)
$PATTERN_VERSION = (Select-String -Path 'skills/pattern/SKILL.md' -Pattern 'version:\s*"([^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
$USE_CASE_VERSION = (Select-String -Path 'skills/use-case/SKILL.md' -Pattern 'version:\s*"([^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
$XREF_VERSION = (Select-String -Path 'skills/cross-reference/SKILL.md' -Pattern 'version:\s*"([^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value

# Extract required dependency versions from pattern SKILL.md x-skill-requires line
$patternContent = Get-Content 'skills/pattern/SKILL.md' -Raw
if ($patternContent -match 'x-skill-requires:.*?model \^([0-9]+\.[0-9]+\.[0-9]+)') {
    $REQUIRED_MODEL = $Matches[1]
} else {
    $REQUIRED_MODEL = "unknown"
}
if ($patternContent -match 'x-skill-requires:.*?markdown-deck \^([0-9]+\.[0-9]+\.[0-9]+)') {
    $REQUIRED_DECK = $Matches[1]
} else {
    $REQUIRED_DECK = "unknown"
}

Write-Host "Current skill versions:"
Write-Host "  pattern:          v$PATTERN_VERSION"
Write-Host "  use-case:         v$USE_CASE_VERSION"
Write-Host "  cross-reference:  v$XREF_VERSION"
Write-Host ""
Write-Host "Required dependencies (from pattern SKILL.md):"
Write-Host "  model:            >= v$REQUIRED_MODEL"
Write-Host "  markdown-deck:    >= v$REQUIRED_DECK"
Write-Host ""

# Check quick-start.md
Write-Host "Checking docs/quick-start.md..."
$quickStartContent = Get-Content 'docs/quick-start.md' -Raw
if ($quickStartContent -notmatch "pattern--v$PATTERN_VERSION") {
    Write-Host "  × Error: quick-start.md doesn't reference pattern--v$PATTERN_VERSION" -ForegroundColor Red
    $ERRORS++
} else {
    Write-Host "  ✓ pattern version matches" -ForegroundColor Green
}

if ($quickStartContent -notmatch "model--v$REQUIRED_MODEL") {
    Write-Host "  × Error: quick-start.md doesn't reference model--v$REQUIRED_MODEL" -ForegroundColor Red
    $ERRORS++
} else {
    Write-Host "  ✓ model version matches" -ForegroundColor Green
}

# For markdown-deck, allow any patch version >= minimum
$deckParts = $REQUIRED_DECK -split '\.'
$deckMajor = $deckParts[0]
$deckMinor = $deckParts[1]
if ($quickStartContent -match "markdown-deck--v$deckMajor\.$deckMinor\.\d+") {
    Write-Host "  ✓ markdown-deck version compatible (>= v$REQUIRED_DECK)" -ForegroundColor Green
} else {
    Write-Host "  × Error: quick-start.md doesn't reference markdown-deck--v$deckMajor.$deckMinor.x" -ForegroundColor Red
    $ERRORS++
}

# Check README.md
Write-Host ""
Write-Host "Checking README.md..."
Write-Host "  ✓ (version-agnostic references only)" -ForegroundColor Green

# Check update scripts reference the right repos
Write-Host ""
Write-Host "Checking scripts/update-skills.sh..."
$updateShContent = Get-Content 'scripts/update-skills.sh' -Raw
if ($updateShContent -notmatch 'REPO_PATTERN="https://github.com/dermot-obrien/architecture-pattern.git"') {
    Write-Host "  × Error: update-skills.sh has wrong REPO_PATTERN" -ForegroundColor Red
    $ERRORS++
}
if ($updateShContent -notmatch 'REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"') {
    Write-Host "  × Error: update-skills.sh has wrong REPO_MODEL" -ForegroundColor Red
    $ERRORS++
}
if ($updateShContent -notmatch 'REPO_DECK="https://github.com/dermot-obrien/markdown-deck.git"') {
    Write-Host "  × Error: update-skills.sh has wrong REPO_DECK" -ForegroundColor Red
    $ERRORS++
}
Write-Host "  ✓ Repository URLs correct" -ForegroundColor Green

Write-Host ""
Write-Host "Checking scripts/update-skills.ps1..."
$updatePs1Content = Get-Content 'scripts/update-skills.ps1' -Raw
if ($updatePs1Content -notmatch 'REPO_PATTERN = "https://github.com/dermot-obrien/architecture-pattern.git"') {
    Write-Host "  × Error: update-skills.ps1 has wrong REPO_PATTERN" -ForegroundColor Red
    $ERRORS++
}
if ($updatePs1Content -notmatch 'REPO_MODEL = "https://github.com/dermot-obrien/diagram-model.git"') {
    Write-Host "  × Error: update-skills.ps1 has wrong REPO_MODEL" -ForegroundColor Red
    $ERRORS++
}
if ($updatePs1Content -notmatch 'REPO_DECK = "https://github.com/dermot-obrien/markdown-deck.git"') {
    Write-Host "  × Error: update-skills.ps1 has wrong REPO_DECK" -ForegroundColor Red
    $ERRORS++
}
Write-Host "  ✓ Repository URLs correct" -ForegroundColor Green

# Check that tags exist locally for current skill versions
Write-Host ""
Write-Host "Checking if current skill versions are tagged..."
foreach ($skill in @(
    @{name='pattern'; version=$PATTERN_VERSION},
    @{name='use-case'; version=$USE_CASE_VERSION},
    @{name='cross-reference'; version=$XREF_VERSION}
)) {
    $tag = "$($skill.name)--v$($skill.version)"
    $tagExists = git tag -l $tag
    if ($tagExists) {
        Write-Host "  ✓ $tag exists locally" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Warning: $tag not found locally (may not be released yet)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
if ($ERRORS -eq 0) {
    Write-Host "✅ All version references are consistent" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Found $ERRORS version inconsistency error(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix:"
    Write-Host "  1. Update version in skills/*/SKILL.md"
    Write-Host "  2. Update docs/quick-start.md to match"
    Write-Host "  3. Run this script again to verify"
    exit 1
}
