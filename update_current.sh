#!/bin/bash
# Find the most recently edited .md file and symlink "current" to its parent directory

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# Find the most recently modified .md file under blog/posts/
LATEST_MD=$(find blog/posts -name "*.md" -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$LATEST_MD" ]; then
    echo "No .md files found under blog/posts/" >&2
    exit 1
fi

PARENT_DIR="$(dirname "$LATEST_MD")"
echo "Most recent: $LATEST_MD"
echo "Linking 'current' -> $PARENT_DIR"

# Remove existing symlink or fail if it's a real directory
if [ -L "current" ]; then
    rm "current"
elif [ -e "current" ]; then
    echo "Error: 'current' exists and is not a symlink" >&2
    exit 1
fi

ln -s "$PARENT_DIR" "current"
echo "Done."
