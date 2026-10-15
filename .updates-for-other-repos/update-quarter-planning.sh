#!/bin/bash
# Update quarter-planning skill
# Usage: ./scripts/update-quarter-planning.sh [--user] [--check-only]

set -e

REPO_PLANNING="https://github.com/dermot-obrien/delivery-planning.git"

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
    echo "📦 Updating user-level quarter-planning skill at: $SKILLS_DIR"
else
    SKILLS_DIR=".agents/skills"
    echo "📦 Updating workspace-level quarter-planning skill at: $SKILLS_DIR"
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
    git ls-remote --tags "$REPO_PLANNING" | grep "quarter-planning--v" | sed 's/.*refs\/tags\///' | sort -V | tail -1
}

echo ""
echo "🔍 Current version: $(get_version "$SKILLS_DIR/quarter-planning")"
echo "🌐 Fetching latest version from GitHub..."
LATEST_QP=$(get_latest_tag)
echo "   Latest: $LATEST_QP"

if [ "$CHECK_ONLY" = true ]; then
    echo ""
    echo "✅ Check complete. Use without --check-only to update."
    exit 0
fi

echo ""
read -p "🔄 Update quarter-planning skill to $LATEST_QP? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

# Download latest version
TEMP_DIR=$(mktemp -d)
echo ""
echo "📥 Downloading $LATEST_QP..."
cd "$TEMP_DIR"
git clone --depth 1 --branch "$LATEST_QP" "$REPO_PLANNING" delivery-planning 2>&1 | grep -v "Cloning" || true
cd - > /dev/null

# Backup and remove old installation
if [ -d "$SKILLS_DIR/quarter-planning" ]; then
    echo ""
    echo "💾 Backing up current installation..."
    BACKUP_DIR=".skill-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$SKILLS_DIR/quarter-planning" "$BACKUP_DIR/quarter-planning"
    echo "   Backup saved to: $BACKUP_DIR"
    
    echo "🗑️  Removing old installation..."
    rm -rf "$SKILLS_DIR/quarter-planning"
fi

# Install new version
echo "📋 Installing $LATEST_QP..."
mkdir -p "$SKILLS_DIR"
cp -r "$TEMP_DIR/delivery-planning/skills/quarter-planning" "$SKILLS_DIR/"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify
echo ""
echo "✅ Verifying installation..."
python "$SKILLS_DIR/quarter-planning/bin/check.py"

echo ""
echo "🎉 Update complete!"
echo "📊 Installed version: $(get_version "$SKILLS_DIR/quarter-planning")"
echo ""
echo "💡 Next steps:"
echo "  1. Check for new bindings: python $SKILLS_DIR/quarter-planning/bin/quarter.py --quarter <your-quarter> --where"
echo "  2. Re-validate quarters: python $SKILLS_DIR/quarter-planning/bin/quarter.py --quarter <your-quarter> --validate"
echo "  3. Review CHANGELOG for breaking changes"
