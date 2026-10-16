#!/bin/bash
# Check that all version references are in sync across documentation and examples
# Run this before committing version changes

set -e

ERRORS=0

echo "Checking version consistency across repository..."
echo ""

# Extract versions from SKILL.md files (first occurrence of version: in metadata section)
PATTERN_VERSION=$(grep 'version:' skills/pattern/SKILL.md | head -1 | sed 's/.*"\(.*\)".*/\1/')
USE_CASE_VERSION=$(grep 'version:' skills/use-case/SKILL.md | head -1 | sed 's/.*"\(.*\)".*/\1/')
XREF_VERSION=$(grep 'version:' skills/cross-reference/SKILL.md | head -1 | sed 's/.*"\(.*\)".*/\1/')

# Extract required dependency versions from pattern SKILL.md x-skill-requires line
REQUIRED_MODEL=$(grep 'x-skill-requires:' skills/pattern/SKILL.md | grep -o 'model \^[0-9\.]*' | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
REQUIRED_DECK=$(grep 'x-skill-requires:' skills/pattern/SKILL.md | grep -o 'markdown-deck \^[0-9\.]*' | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)

echo "Current skill versions:"
echo "  pattern:          v$PATTERN_VERSION"
echo "  use-case:         v$USE_CASE_VERSION"
echo "  cross-reference:  v$XREF_VERSION"
echo ""
echo "Required dependencies (from pattern SKILL.md):"
echo "  model:            >= v$REQUIRED_MODEL"
echo "  markdown-deck:    >= v$REQUIRED_DECK"
echo ""

# Check quick-start.md
echo "Checking docs/quick-start.md..."
if ! grep -q "pattern--v$PATTERN_VERSION" docs/quick-start.md; then
    echo "  ✗ Error: quick-start.md doesn't reference pattern--v$PATTERN_VERSION"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ pattern version matches"
fi

if ! grep -q "model--v$REQUIRED_MODEL" docs/quick-start.md; then
    echo "  ✗ Error: quick-start.md doesn't reference model--v$REQUIRED_MODEL"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ model version matches"
fi

# For markdown-deck, allow any patch version >= minimum
DECK_MAJOR=$(echo "$REQUIRED_DECK" | cut -d. -f1)
DECK_MINOR=$(echo "$REQUIRED_DECK" | cut -d. -f2)
if grep -qE "markdown-deck--v${DECK_MAJOR}\.${DECK_MINOR}\.[0-9]+" docs/quick-start.md; then
    echo "  + markdown-deck version compatible (>= v$REQUIRED_DECK)"
else
    echo "  x Error: quick-start.md doesn't reference markdown-deck--v${DECK_MAJOR}.${DECK_MINOR}.x"
    ERRORS=$((ERRORS + 1))
fi

# Check README.md
echo ""
echo "Checking README.md..."
# README should mention the dependencies but doesn't pin versions - that's OK
echo "  + (version-agnostic references only)"

# Check update scripts reference the right repos
echo ""
echo "Checking scripts/update-skills.sh..."
if ! grep -q 'REPO_PATTERN="https://github.com/dermot-obrien/architecture-pattern.git"' scripts/update-skills.sh; then
    echo "  ✗ Error: update-skills.sh has wrong REPO_PATTERN"
    ERRORS=$((ERRORS + 1))
fi
if ! grep -q 'REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"' scripts/update-skills.sh; then
    echo "  ✗ Error: update-skills.sh has wrong REPO_MODEL"
    ERRORS=$((ERRORS + 1))
fi
if ! grep -q 'REPO_DECK="https://github.com/dermot-obrien/markdown-deck.git"' scripts/update-skills.sh; then
    echo "  ✗ Error: update-skills.sh has wrong REPO_DECK"
    ERRORS=$((ERRORS + 1))
fi
echo "  + Repository URLs correct"

echo ""
echo "Checking scripts/update-skills.ps1..."
if ! grep -q 'REPO_PATTERN = "https://github.com/dermot-obrien/architecture-pattern.git"' scripts/update-skills.ps1; then
    echo "  x Error: update-skills.ps1 has wrong REPO_PATTERN"
    ERRORS=$((ERRORS + 1))
fi
if ! grep -q 'REPO_MODEL = "https://github.com/dermot-obrien/diagram-model.git"' scripts/update-skills.ps1; then
    echo "  x Error: update-skills.ps1 has wrong REPO_MODEL"
    ERRORS=$((ERRORS + 1))
fi
if ! grep -q 'REPO_DECK = "https://github.com/dermot-obrien/markdown-deck.git"' scripts/update-skills.ps1; then
    echo "  x Error: update-skills.ps1 has wrong REPO_DECK"
    ERRORS=$((ERRORS + 1))
fi
echo "  + Repository URLs correct"

# Check that tags exist locally for current skill versions
echo ""
echo "Checking if current skill versions are tagged..."
for skill in "pattern:$PATTERN_VERSION" "use-case:$USE_CASE_VERSION" "cross-reference:$XREF_VERSION"; do
    SKILL_NAME=$(echo "$skill" | cut -d: -f1)
    VERSION=$(echo "$skill" | cut -d: -f2)
    TAG="${SKILL_NAME}--v${VERSION}"
    
    if git tag -l "$TAG" | grep -q "$TAG"; then
        echo "  + $TAG exists locally"
    else
        echo "  ! Warning: $TAG not found locally (may not be released yet)"
    fi
done

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo "== All version references are consistent"
    exit 0
else
    echo "!! Found $ERRORS version inconsistency error(s)"
    echo ""
    echo "To fix:"
    echo "  1. Update version in skills/*/SKILL.md"
    echo "  2. Update docs/quick-start.md to match"
    echo "  3. Run this script again to verify"
    exit 1
fi
