#!/bin/bash

# Default to today's date
DEFAULT_DATE=$(date +%Y-%m-%d)

# Ask for the date with default
read -p "Enter date [$DEFAULT_DATE]: " DATE
DATE=${DATE:-$DEFAULT_DATE}

# Extract year and month from the date
YEAR=$(echo $DATE | cut -d'-' -f1)
MONTH=$(echo $DATE | cut -d'-' -f2)

# Ask for the directory name
read -p "Enter directory name: " DIR_NAME

# Create the target directory
TARGET_DIR="posts/$YEAR/$MONTH/$DIR_NAME"
mkdir -p "$TARGET_DIR"

# Copy template files
cp -r talk/template/* "$TARGET_DIR/"

echo "New talk created at $TARGET_DIR"
echo "Files copied from template"
