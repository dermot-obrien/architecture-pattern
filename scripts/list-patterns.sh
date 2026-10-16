#!/bin/bash
# List all patterns in the workspace
# Usage: ./scripts/list-patterns.sh [directory]

SEARCH_DIR="${1:-.}"

echo "Searching for patterns in: $SEARCH_DIR"
echo ""

# Find all index.md files that have pattern metadata
find "$SEARCH_DIR" -type f -name "index.md" | while read -r file; do
    # Check if file has pattern front matter
    if grep -q "^title:" "$file" && grep -q "^id:" "$file"; then
        dir=$(dirname "$file")
        
        # Extract pattern info
        title=$(grep "^title:" "$file" | head -1 | sed 's/title: *//' | tr -d '"')
        id=$(grep "^id:" "$file" | head -1 | sed 's/id: *//' | tr -d '"')
        version=$(grep "^version:" "$file" | head -1 | sed 's/version: *//' | tr -d '"')
        
        if [ -n "$id" ]; then
            echo "[$id] $title"
            if [ -n "$version" ]; then
                echo "  Version: $version"
            fi
            echo "  Path: $dir"
            echo ""
        fi
    fi
done

# Also look for patterns via model.py scan if available
if [ -f ".agents/skills/model/bin/model.py" ]; then
    echo "---"
    echo "Using model.py scan for validation:"
    echo ""
    python .agents/skills/model/bin/model.py scan "$SEARCH_DIR" --recursive 2>&1 | grep -E "^(PAT-|REF-|UC-)" || echo "No patterns found by model.py"
fi
