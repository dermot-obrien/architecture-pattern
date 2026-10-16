#!/bin/bash
# List all patterns in the workspace with validation
# Usage: ./scripts/list-patterns.sh [directory] [--verbose]

SEARCH_DIR="."
VERBOSE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --verbose|-v)
            VERBOSE=true
            ;;
        *)
            SEARCH_DIR="$arg"
            ;;
    esac
done

echo "Searching for patterns in: $SEARCH_DIR"
if [ "$VERBOSE" = true ]; then
    echo "(verbose mode enabled)"
fi
echo ""

MODEL_PY=".agents/skills/model/bin/model.py"

# Find all index.md files that have pattern metadata
find "$SEARCH_DIR" -type f -name "index.md" | sort | while read -r file; do
    # Check if file has pattern front matter
    if grep -q "^title:" "$file" && grep -q "^id:" "$file"; then
        dir=$(dirname "$file")
        
        # Extract pattern info
        title=$(grep "^title:" "$file" | head -1 | sed 's/title: *//' | tr -d '"')
        id=$(grep "^id:" "$file" | head -1 | sed 's/id: *//' | tr -d '"')
        version=$(grep "^version:" "$file" | head -1 | sed 's/version: *//' | tr -d '"')
        
        if [ -n "$id" ]; then
            # Try to validate if model.py is available
            status=""
            if [ -f "$MODEL_PY" ]; then
                validation=$(python "$MODEL_PY" validate "$file" 2>&1)
                if echo "$validation" | grep -q "0 problems"; then
                    status=" ✓"
                else
                    status=" ✗"
                fi
            fi
            
            echo "[$id]$status $title"
            if [ -n "$version" ]; then
                echo "  Version: $version"
            fi
            echo "  Path: $dir"
            
            # Show validation details in verbose mode
            if [ "$VERBOSE" = true ] && [ -f "$MODEL_PY" ]; then
                echo "  Validation:"
                python "$MODEL_PY" validate "$file" 2>&1 | sed 's/^/    /'
            fi
            
            echo ""
        fi
    fi
done

# Summary from model.py scan if available
if [ -f "$MODEL_PY" ] && [ "$VERBOSE" = true ]; then
    echo "---"
    echo "Full scan results:"
    echo ""
    python "$MODEL_PY" scan "$SEARCH_DIR" --recursive 2>&1
fi
