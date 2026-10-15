#!/bin/bash
# Update markdown-deck skill
# Usage: ./scripts/update-markdown-deck.sh [--user] [--check-only]

set -e

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
    echo "📦 Updating user-level markdown-deck skill at: $SKILLS_DIR"
else
    SKILLS_DIR=".agents/skills"
    echo "📦 Updating workspace-level markdown-deck skill at: $SKILLS_DIR"
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
    git ls-remote --tags "$REPO_DECK" | grep "markdown-deck--v" | sed 's/.*refs\/tags\///' | sort -V | tail -1
}

echo ""
echo "🔍 Current version: $(get_version "$SKILLS_DIR/markdown-deck")"
echo "🌐 Fetching latest version from GitHub..."
LATEST_DECK=$(get_latest_tag)
echo "   Latest: $LATEST_DECK"

if [ "$CHECK_ONLY" = true ]; then
    echo ""
    echo "✅ Check complete. Use without --check-only to update."
    exit 0
fi

echo ""
read -p "🔄 Update markdown-deck skill to $LATEST_DECK? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

# Download latest version
TEMP_DIR=$(mktemp -d)
echo ""
echo "📥 Downloading $LATEST_DECK..."
cd "$TEMP_DIR"
git clone --depth 1 --branch "$LATEST_DECK" "$REPO_DECK" markdown-deck 2>&1 | grep -v "Cloning" || true
cd - > /dev/null

# Backup and remove old installation
if [ -d "$SKILLS_DIR/markdown-deck" ]; then
    echo ""
    echo "💾 Backing up current installation..."
    BACKUP_DIR=".skill-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$SKILLS_DIR/markdown-deck" "$BACKUP_DIR/markdown-deck"
    echo "   Backup saved to: $BACKUP_DIR"
    
    echo "🗑️  Removing old installation..."
    rm -rf "$SKILLS_DIR/markdown-deck"
fi

# Install new version
echo "📋 Installing $LATEST_DECK..."
mkdir -p "$SKILLS_DIR"
cp -r "$TEMP_DIR/markdown-deck/skills/markdown-deck" "$SKILLS_DIR/"

# Install npm dependencies
echo ""
echo "📦 Installing npm dependencies..."
npm install --prefix "$SKILLS_DIR/markdown-deck" --no-audit --no-fund

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify
echo ""
echo "✅ Verifying installation..."
node "$SKILLS_DIR/markdown-deck/bin/check.mjs"

echo ""
echo "🎉 Update complete!"
echo "📊 Installed version: $(get_version "$SKILLS_DIR/markdown-deck")"
echo ""
echo "💡 Next steps:"
echo "  1. Rebuild existing decks: node $SKILLS_DIR/markdown-deck/bin/markdown-deck.mjs build <file> --out <dir>"
echo "  2. Check your bindings: node $SKILLS_DIR/markdown-deck/bin/check.mjs"
