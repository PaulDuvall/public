#!/bin/bash
# Copy global_rules.md to the Codeium Windsurf memories directory

SRC="$HOME/Code/public/windsurf/global_rules.md"
DEST="$HOME/.codeium/windsurf/memories/global_rules.md"

# Create destination directory if it doesn't exist
mkdir -p "$(dirname "$DEST")"

# Copy the file
cp "$SRC" "$DEST"

echo "Copied $SRC to $DEST"
