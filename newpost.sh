#!/usr/bin/env bash
set -euo pipefail

# Where this script lives (so paths work no matter where you run it from)
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ask for the slug
read -rp "Slug (e.g. spy-pycon-de): " SLUG
if [[ -z "${SLUG}" ]]; then
  echo "Error: slug cannot be empty." >&2
  exit 1
fi

# Compute year/month
YEAR="$(date +%Y)"
MONTH="$(date +%m)"

# Paths
BASE_DIR="${SCRIPT_DIR}/blog/posts"
NEW_DIR="${BASE_DIR}/${YEAR}/${MONTH}-${SLUG}"
TEMPLATE_FILE="${BASE_DIR}/template/index.md.txt"
NEW_FILE="${NEW_DIR}/index.md"

# Create directory
mkdir -p "${NEW_DIR}"

# Copy template -> index.md
if [[ ! -f "${TEMPLATE_FILE}" ]]; then
  echo "Error: template not found at ${TEMPLATE_FILE}" >&2
  exit 1
fi

cp "${TEMPLATE_FILE}" "${NEW_FILE}"

# Open in editor using `e`
e "${NEW_FILE}"
