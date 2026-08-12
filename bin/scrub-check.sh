#!/bin/sh
# scrub-check — fail if anything that looks like vault content is present.
#
#   sh scrub-check.sh [path]        # defaults to the repo root
#
# The engine is meant to be shareable. Vault content is not. This is the gate
# between them: run it before publishing the engine, and after any change that
# copied text out of a real vault (examples, edge cases, eval fixtures).
#
# Patterns live in bin/scrub-patterns.txt, one extended-regex per line.
# Lines starting with # are comments.

set -eu

ROOT=${1:-$(cd "$(dirname "$0")/.." && pwd)}
PATTERNS="$(dirname "$0")/scrub-patterns.txt"

[ -f "$PATTERNS" ] || { echo "error: no pattern file at $PATTERNS" >&2; exit 2; }

echo "scrub-check: $ROOT"
HITS=0
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

while IFS= read -r pat; do
  case "$pat" in ''|\#*) continue ;; esac
  if grep -rInE "$pat" "$ROOT" \
      --exclude-dir=.git \
      --exclude=scrub-patterns.txt \
      --exclude=scrub-check.sh > "$TMP" 2>/dev/null; then
    echo
    echo "!! pattern: $pat"
    sed 's|^|   |' < "$TMP"
    HITS=$((HITS + 1))
  fi
done < "$PATTERNS"

echo
if [ "$HITS" -gt 0 ]; then
  echo "FAIL — $HITS pattern(s) matched. Scrub before sharing this repo."
  exit 1
fi
echo "PASS — no vault content detected."
