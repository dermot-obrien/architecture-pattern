#!/bin/bash
# Update architecture-pattern skills and dependencies
# Usage: ./scripts/update-skills.sh [--user] [--check-only]

set -e

# Configuration
REPO_PATTERN="https://github.com/dermot-obrien/architecture-pattern.git"
REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"
REPO_DECK="https://github.com/dermot-obrien/markdown-deck.git"

# Parse arguments
CHECK_ONLY=false
for arg in "$@"; do
    case $arg in
        --check-only) CHECK_ONLY=true ;;
    esac
done

# Always install in current directory
SKILLS_DIR=".agents/skills"
WORKSPACE_SKILLS_PATH="$(pwd)/$SKILLS_DIR"
echo "📦 Updating skills in current directory at: $WORKSPACE_SKILLS_PATH"

# Warn if not in a repository root
if [ ! -d ".git" ]; then
    echo ""
    echo "⚠️  WARNING: No .git directory found in current location."
    echo "   Skills will be installed in: $WORKSPACE_SKILLS_PATH"
    echo "   Make sure you are in your repository root directory."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Update cancelled."
        exit 0
    fi
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
        # Use rsync to exclude node_modules (can be reinstalled, causes path issues)
        if command -v rsync >/dev/null 2>&1; then
            rsync -a --exclude='node_modules' "$SKILLS_DIR/$skill/" "$BACKUP_DIR/$skill/"
        else
            # Fallback to cp with find to exclude node_modules
            mkdir -p "$BACKUP_DIR/$skill"
            (cd "$SKILLS_DIR/$skill" && find . -name node_modules -prune -o -print | cpio -pdm "$BACKUP_DIR/$skill" 2>/dev/null)
        fi
    fi
done
echo "  Backups saved to: $BACKUP_DIR (node_modules excluded)"

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

# Copy helper scripts to pattern skill
echo ""
echo "📋 Installing helper scripts to pattern skill..."
if [ -f "$TEMP_DIR/architecture-pattern/scripts/list-patterns.sh" ]; then
    cp "$TEMP_DIR/architecture-pattern/scripts/list-patterns.sh" "$SKILLS_DIR/pattern/scripts/"
    chmod +x "$SKILLS_DIR/pattern/scripts/list-patterns.sh"
    echo "  Installed list-patterns.sh to pattern skill"
fi
if [ -f "$TEMP_DIR/architecture-pattern/scripts/list-patterns.ps1" ]; then
    cp "$TEMP_DIR/architecture-pattern/scripts/list-patterns.ps1" "$SKILLS_DIR/pattern/scripts/"
    echo "  Installed list-patterns.ps1 to pattern skill"
fi

# Install npm dependencies for markdown-deck
echo ""
echo "📦 Installing npm dependencies for markdown-deck..."
if ! npm install --prefix "$SKILLS_DIR/markdown-deck" --no-audit --no-fund; then
    echo "  ⚠️  npm install failed. You may need to run it manually:"
    echo "  npm install --prefix $SKILLS_DIR/markdown-deck"
fi

# Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify installation
echo ""
echo "✅ Verifying installation..."
echo ""
echo "Note: Warnings about bindings or catalogue mappings are normal"
echo "      if you haven't set up .agents/skill-bindings.toml yet"
echo ""
echo "pattern:"
python "$SKILLS_DIR/pattern/scripts/check.py" 2>&1 | head -10 || echo "  ⚠️  Check failed"
echo ""
echo "use-case:"
python "$SKILLS_DIR/use-case/scripts/check.py" 2>&1 | head -10 || echo "  ⚠️  Check failed"
echo ""
echo "cross-reference:"
node "$SKILLS_DIR/cross-reference/scripts/check.cjs" 2>&1 | head -10 || echo "  ⚠️  Check failed"
echo ""
echo "model:"
python "$SKILLS_DIR/model/bin/model.py" doctor 2>&1 | head -10 || echo "  ⚠️  Check failed"

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
echo "  1. Set up skill bindings if needed: create .agents/skill-bindings.toml"
echo "     See: https://github.com/dermot-obrien/architecture-pattern/blob/main/docs/quick-start.md"
echo "  2. Check bindings: python $SKILLS_DIR/model/bin/model.py doctor --skill pattern"
echo "  3. List patterns: $SKILLS_DIR/pattern/scripts/list-patterns.sh <directory> [--verbose]"
echo "  4. Re-validate existing content: python $SKILLS_DIR/model/bin/model.py scan <your-folder> --recursive"
echo ""
echo "Note: Catalogue mapping warnings are normal if you haven't created .agents/skill-bindings.toml yet"
