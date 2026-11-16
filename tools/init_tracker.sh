#!/usr/bin/env bash
# Copy tracker-template into ./candidates and git-init it as a private tracker.
# Does not create a GitHub remote and does not commit. Refuses a non-empty destination.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$ROOT/candidates}"
TEMPLATE="$ROOT/tracker-template"

if [[ ! -d "$TEMPLATE/db" ]]; then
  echo "tracker-template is missing at $TEMPLATE" >&2
  exit 1
fi
if [[ -e "$DEST" ]] && [[ -n "$(ls -A "$DEST" 2>/dev/null || true)" ]]; then
  echo "Refusing to overwrite non-empty $DEST" >&2
  exit 1
fi

mkdir -p "$DEST"
cp -a "$TEMPLATE/." "$DEST/"
if [[ ! -d "$DEST/.git" ]]; then
  git -C "$DEST" init -b main
fi
chmod 700 "$DEST"
echo "Private tracker ready at $DEST"
echo "Next: create your own private GitHub repository, add it as origin, and keep this folder out of the engine repo."
echo "The engine gitignores ./candidates. Do not commit applicant files into the engine."
