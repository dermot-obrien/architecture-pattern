#!/bin/bash
# Update diagram-model skill
# Usage: ./scripts/update-model.sh [--user] [--check-only]

set -e

REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"

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
    echo "📦 Updating user-level model skill at: $SKILLS_DIR"
else
    SKILLS_DIR=".agents/skills"
    echo "📦 Updating workspace-level model skill at: $SKILLS_DIR"
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

# Function to get latest tag
get_latest_tag() {
    git ls-remote --tags "$REPO_MODEL" | grep "model--v" | sed 's/.*refs\/tags\///' | sort -V | tail -1
}

echo ""
echo "🔍 Current version: $(get_version "$SKILLS_DIR/model")"
echo "🌐 Fetching latest version from GitHub..."
LATEST_MODEL=$(get_latest_tag)
echo "   Latest: $LATEST_MODEL"

if [ "$CHECK_ONLY" = true ]; then
    echo ""
    echo "✅ Check complete. Use without --check-only to update."
    exit 0
fi

echo ""
read -p "🔄 Update model skill to $LATEST_MODEL? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

# Download latest version
TEMP_DIR=$(mktemp -d)
echo ""
echo "📥 Downloading $LATEST_MODEL..."
cd "$TEMP_DIR"
git clone --depth 1 --branch "$LATEST_MODEL" "$REPO_MODEL" diagram-model 2>&1 | grep -v "Cloning" || true
cd - > /dev/null

# Backup and remove old installation
if [ -d "$SKILLS_DIR/model" ]; then
    echo ""
    echo "💾 Backing up current installation..."
    BACKUP_DIR=".skill-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$SKILLS_DIR/model" "$BACKUP_DIR/model"
    echo "   Backup saved to: $BACKUP_DIR"
    
    echo "🗑️  Removing old installation..."
    rm -rf "$SKILLS_DIR/model"
fi

# Install new version
echo "📋 Installing $LATEST_MODEL..."
mkdir -p "$SKILLS_DIR"
cp -r "$TEMP_DIR/diagram-model/skills/model" "$SKILLS_DIR/"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify
echo ""
echo "✅ Verifying installation..."
python "$SKILLS_DIR/model/bin/model.py" doctor

echo ""
echo "🎉 Update complete!"
echo "📊 Installed version: $(get_version "$SKILLS_DIR/model")"
echo ""
echo "💡 Next steps:"
echo "  1. Re-validate your models: python $SKILLS_DIR/model/bin/model.py scan <folder> --recursive"
echo "  2. Check your bindings: python $SKILLS_DIR/model/bin/model.py doctor --json"
