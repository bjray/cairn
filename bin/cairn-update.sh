#!/bin/sh
# cairn-update — refresh the vendored engine inside a vault.
#
#   sh cairn-update.sh <engine-repo> <vault-path> [--apply]
#
# Without --apply this is a dry run: it lists what would change and exits.
# Engine-owned paths are replaced wholesale. Everything else in the vault is
# never touched — raw/, wiki/, outputs/, system/log.md, system/lint-reports/,
# system/templates/ (store-local), system/vault-profile.yml, and CLAUDE.md.

set -eu

ENGINE=${1:-}
VAULT=${2:-}
APPLY=${3:-}

if [ -z "$ENGINE" ] || [ -z "$VAULT" ]; then
  echo "usage: sh cairn-update.sh <engine-repo> <vault-path> [--apply]" >&2
  exit 2
fi

[ -f "$ENGINE/constitution.md" ] || { echo "error: $ENGINE is not a cairn engine repo" >&2; exit 1; }
[ -f "$VAULT/system/vault-profile.yml" ] || { echo "error: $VAULT is not a cairn vault (no system/vault-profile.yml)" >&2; exit 1; }

VERSION=$(cd "$ENGINE" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
CURRENT=$(cat "$VAULT/system/cairn/VERSION" 2>/dev/null || echo "none")

echo "engine:  $ENGINE @ $VERSION"
echo "vault:   $VAULT (currently on $CURRENT)"
echo

# Refuse to clobber local edits to engine-owned paths — that drift is a bug
# worth surfacing, not silently overwriting.
if [ -d "$VAULT/.git" ] && [ "$CURRENT" != "none" ]; then
  DRIFT=$(cd "$VAULT" && git status --porcelain -- system/cairn .claude/skills 2>/dev/null || true)
  if [ -n "$DRIFT" ]; then
    echo "!! Local modifications to engine-owned paths:" >&2
    echo "$DRIFT" >&2
    echo "!! Those changes belong upstream in the engine repo, not here." >&2
    echo "!! Commit or discard them, then re-run." >&2
    exit 1
  fi
fi

echo "would replace:"
echo "  system/cairn/constitution.md"
echo "  system/cairn/templates/"
echo "  system/cairn/bin/"
echo "  system/cairn/VERSION            ($CURRENT -> $VERSION)"
echo "  .claude/skills/kb-compile/"
[ -d "$VAULT/.claude/skills/cairn-init" ] && echo "  .claude/skills/cairn-init/"
echo
echo "untouched: raw/ wiki/ outputs/ system/log.md system/lint-reports/"
echo "           system/templates/ system/vault-profile.yml CLAUDE.md"

if [ "$APPLY" != "--apply" ]; then
  echo
  echo "dry run — re-run with --apply to write."
  exit 0
fi

echo
mkdir -p "$VAULT/system/cairn" "$VAULT/.claude/skills"
rm -rf "$VAULT/system/cairn/templates" "$VAULT/system/cairn/bin" "$VAULT/.claude/skills/kb-compile"
cp "$ENGINE/constitution.md" "$VAULT/system/cairn/constitution.md"
cp -R "$ENGINE/templates" "$VAULT/system/cairn/templates"
cp -R "$ENGINE/bin" "$VAULT/system/cairn/bin"
cp -R "$ENGINE/skills/kb-compile" "$VAULT/.claude/skills/kb-compile"
if [ -d "$VAULT/.claude/skills/cairn-init" ]; then
  rm -rf "$VAULT/.claude/skills/cairn-init"
  cp -R "$ENGINE/skills/cairn-init" "$VAULT/.claude/skills/cairn-init"
fi
echo "$VERSION" > "$VAULT/system/cairn/VERSION"

echo "engine updated: $CURRENT -> $VERSION"
echo "review with 'git diff', then commit as: system: cairn engine -> $VERSION"
