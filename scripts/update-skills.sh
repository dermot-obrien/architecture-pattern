#!/bin/bash
# Update architecture-pattern skills and dependencies
# Usage: ./scripts/update-skills.sh [--user] [--check-only]

set -e

# Configuration
REPO_PATTERN="https://github.com/dermot-obrien/architecture-pattern.git"
REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"
REPO_DECK="https://github.com/dermot-obrien/markdown-deck.git"

# Parse arguments
SCOPE="workspace"
CHECK_ONLY=false
for arg in "$@"; do
    case $arg in
        --user) SCOPE="user" ;;
        --check-only) CHECK_ONLY=true ;;
    esac
done

# Determine installation directory
if [ "$SCOPE" = "user" ]; then
    SKILLS_DIR="$HOME/.agents/skills"
    echo "📦 Updating user-level skills at: $SKILLS_DIR"
else
    SKILLS_DIR=".agents/skills"
    echo "📦 Updating workspace-level skills at: $SKILLS_DIR"
fi

# Function to get current version
get_version() {
    local skill_path=$1
    if [ -f "$skill_path/SKILL.md" ]; then
        grep "version:" "$skill_path/SKILL.md" | head -1 | sed 's/.*version: *"\(.*\)".*/\1/'
    else
        echo "not installed"
    fi
}

# Function to get latest tag for a skill
get_latest_tag() {
    local repo=$1
    local skill=$2
    git ls-remote --tags "$repo" | grep "$skill--v" | sed 's/.*refs\/tags\///' | grep -v '\^{}' | sort -V | tail -1
}

echo ""
echo "🔍 Checking current versions..."
echo "  pattern:          $(get_version "$SKILLS_DIR/pattern")"
echo "  use-case:         $(get_version "$SKILLS_DIR/use-case")"
echo "  cross-reference:  $(get_version "$SKILLS_DIR/cross-reference")"
echo "  model:            $(get_version "$SKILLS_DIR/model")"
echo "  markdown-deck:    $(get_version "$SKILLS_DIR/markdown-deck")"

echo ""
echo "🌐 Fetching latest versions from GitHub..."
LATEST_PATTERN=$(get_latest_tag "$REPO_PATTERN" "pattern")
LATEST_USE_CASE=$(get_latest_tag "$REPO_PATTERN" "use-case")
LATEST_XREF=$(get_latest_tag "$REPO_PATTERN" "cross-reference")
LATEST_MODEL=$(get_latest_tag "$REPO_MODEL" "model")
LATEST_DECK=$(get_latest_tag "$REPO_DECK" "markdown-deck")

echo "  Latest pattern:          $LATEST_PATTERN"
echo "  Latest use-case:         $LATEST_USE_CASE"
echo "  Latest cross-reference:  $LATEST_XREF"
echo "  Latest model:            $LATEST_MODEL"
echo "  Latest markdown-deck:    $LATEST_DECK"

if [ "$CHECK_ONLY" = true ]; then
    echo ""
    echo "✅ Check complete. Use without --check-only to update."
    exit 0
fi

# Confirm update
echo ""
read -p "🔄 Update skills to latest versions? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo ""
echo "📥 Downloading latest versions to $TEMP_DIR..."

# Clone repositories at latest tags
cd "$TEMP_DIR"
echo "  Cloning architecture-pattern..."
git clone --depth 1 --branch "$LATEST_PATTERN" "$REPO_PATTERN" architecture-pattern 2>&1 | grep -v "Cloning" || true
echo "  Cloning diagram-model..."
git clone --depth 1 --branch "$LATEST_MODEL" "$REPO_MODEL" diagram-model 2>&1 | grep -v "Cloning" || true
echo "  Cloning markdown-deck..."
git clone --depth 1 --branch "$LATEST_DECK" "$REPO_DECK" markdown-deck 2>&1 | grep -v "Cloning" || true

cd - > /dev/null

# Backup old installations
echo ""
echo "💾 Backing up current installations..."
BACKUP_DIR=".skill-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
for skill in pattern use-case cross-reference model markdown-deck; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "  Backing up $skill..."
        cp -r "$SKILLS_DIR/$skill" "$BACKUP_DIR/$skill"
    fi
done
echo "  Backups saved to: $BACKUP_DIR"

# Remove old installations
echo ""
echo "🗑️  Removing old installations..."
for skill in pattern use-case cross-reference model markdown-deck; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "  Removing $skill..."
        rm -rf "$SKILLS_DIR/$skill"
    fi
done

# Install new versions
echo ""
echo "📋 Installing new versions..."
mkdir -p "$SKILLS_DIR"

echo "  Installing pattern..."
cp -r "$TEMP_DIR/architecture-pattern/skills/pattern" "$SKILLS_DIR/"

echo "  Installing use-case..."
cp -r "$TEMP_DIR/architecture-pattern/skills/use-case" "$SKILLS_DIR/"

echo "  Installing cross-reference..."
cp -r "$TEMP_DIR/architecture-pattern/skills/cross-reference" "$SKILLS_DIR/"

echo "  Installing model..."
cp -r "$TEMP_DIR/diagram-model/skills/model" "$SKILLS_DIR/"

echo "  Installing markdown-deck..."
cp -r "$TEMP_DIR/markdown-deck/skills/markdown-deck" "$SKILLS_DIR/"

# Install npm dependencies for markdown-deck
echo ""
echo "📦 Installing npm dependencies for markdown-deck..."
npm install --prefix "$SKILLS_DIR/markdown-deck" --no-audit --no-fund

# Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify installation
echo ""
echo "✅ Verifying installation..."
echo ""
echo "pattern:"
python "$SKILLS_DIR/pattern/scripts/check.py" || echo "  ⚠️  Check failed"
echo ""
echo "use-case:"
python "$SKILLS_DIR/use-case/scripts/check.py" || echo "  ⚠️  Check failed"
echo ""
echo "cross-reference:"
node "$SKILLS_DIR/cross-reference/scripts/check.cjs" || echo "  ⚠️  Check failed"
echo ""
echo "model:"
python "$SKILLS_DIR/model/bin/model.py" doctor || echo "  ⚠️  Check failed"

echo ""
echo "🎉 Update complete!"
echo ""
echo "📊 Installed versions:"
echo "  pattern:          $(get_version "$SKILLS_DIR/pattern")"
echo "  use-case:         $(get_version "$SKILLS_DIR/use-case")"
echo "  cross-reference:  $(get_version "$SKILLS_DIR/cross-reference")"
echo "  model:            $(get_version "$SKILLS_DIR/model")"
echo "  markdown-deck:    $(get_version "$SKILLS_DIR/markdown-deck")"
echo ""
echo "💡 Next steps:"
echo "  1. Re-validate your patterns: python $SKILLS_DIR/model/bin/model.py scan patterns --recursive"
echo "  2. Republish any existing patterns: python $SKILLS_DIR/pattern/scripts/publish.py <folder>"
echo "  3. Check your bindings: python $SKILLS_DIR/model/bin/model.py doctor --skill pattern"
