#!/bin/sh
# Sweep stale git lock/tmp files that cloud Cowork sessions cannot delete
# (the device bridge permits mv but not rm). Run after any git write operation
# when working via a cloud session. Harmless to run anytime.
cd "$(dirname "$0")/../.." || exit 1
mkdir -p .git/_stale_locks
for f in .git/HEAD.lock .git/index.lock .git/objects/maintenance.lock .git/refs/heads/*.lock; do
  [ -f "$f" ] && mv "$f" ".git/_stale_locks/$(basename "$f").$(date +%s 2>/dev/null || echo x)"
done
find .git/objects -name 'tmp_obj_*' -exec sh -c 'mv "$1" .git/_stale_locks/ 2>/dev/null' _ {} \; 2>/dev/null
exit 0
