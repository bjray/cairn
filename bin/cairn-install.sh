#!/bin/sh
# cairn-install — make the cairn skills available everywhere on this machine.
#
#   sh bin/cairn-install.sh [--uninstall]
#
# Claude Code discovers skills in a project's .claude/skills/ or in the
# user-level ~/.claude/skills/. The cairn repo keeps its skills under skills/
# so they can be vendored into vaults — which means they are NOT discoverable
# from the cairn repo itself. This installs them user-level so `cairn init`
# works from any directory, including an empty one you are about to turn into
# a vault.
#
# Vaults do not need this: `cairn init` vendors kb-compile and cairn-init into
# each vault's own .claude/skills/, so working inside a vault always works.

set -eu

ENGINE=$(cd "$(dirname "$0")/.." && pwd)
DEST="$HOME/.claude/skills"

if [ "${1:-}" = "--uninstall" ]; then
  for s in "$ENGINE"/skills/*/; do
    name=$(basename "$s")
    if [ -e "$DEST/$name" ]; then rm -rf "$DEST/$name"; echo "removed $DEST/$name"; fi
  done
  echo "done. vault-local skills are untouched."
  exit 0
fi

mkdir -p "$DEST"
for s in "$ENGINE"/skills/*/; do
  name=$(basename "$s")
  rm -rf "$DEST/$name"
  cp -R "$s" "$DEST/$name"
  echo "installed $name -> $DEST/$name"
done

cat <<EOF

Installed from: $ENGINE
These are COPIES. After 'git pull' in the engine repo, re-run this to refresh
them, or they will drift from upstream.

You can now run, from any directory:
  "cairn init ~/Projects/my-kb"
EOF
