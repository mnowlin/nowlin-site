#!/bin/bash
# Copy the C.V. from the nowlin-cv folder into the site, then commit and push so the site redeploys.
# Run by the launchd agent com.nowlin.cv-sync (~/Library/LaunchAgents) whenever the source PDF changes;
# it can also be run by hand. Log: ~/Library/Logs/nowlin-cv-sync.log
set -uo pipefail

RESOURCES="$HOME/Library/CloudStorage/OneDrive-UTArlington/04-RESOURCES"
SRC="$RESOURCES/nowlin-cv/nowlin-cv-short.pdf"
SITE="$RESOURCES/nowlin-site"
REL="static/files/nowlin-cv-short.pdf"

log() { echo "$(date '+%F %T') $*"; }

[ -f "$SRC" ] || { log "source not found: $SRC"; exit 0; }

# launchd fires as soon as the file is touched, which can be while it is still being written or
# synced by OneDrive. Wait until the size stops changing.
prev=-1
for _ in $(seq 1 12); do
  size=$(stat -f %z "$SRC" 2>/dev/null || echo 0)
  [ "$size" = "$prev" ] && break
  prev=$size
  sleep 5
done

# Skip a half-written file: a complete PDF starts with %PDF and ends with %%EOF.
if ! head -c 5 "$SRC" | grep -q '%PDF' || ! tail -c 2048 "$SRC" | grep -aq '%%EOF'; then
  log "source does not look like a complete PDF yet; skipping"
  exit 0
fi

cd "$SITE" || exit 1
cmp -s "$SRC" "$REL" && git diff --quiet -- "$REL" && exit 0

cp "$SRC" "$REL"
log "copied new C.V. into $REL"

branch=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ "$branch" != "main" ]; then
  log "site repo is on '$branch', not main; copied but not committing"
  exit 0
fi

# Commit only the C.V., so any other uncommitted work in the repo is left alone.
git add -- "$REL"
git commit -q -m "Update C.V." -- "$REL" || { log "commit failed"; exit 1; }

if ! git push -q origin main; then
  log "push rejected; rebasing on origin/main and retrying"
  git pull -q --rebase origin main && git push -q origin main || { log "push failed; run 'git push' by hand"; exit 1; }
fi
log "pushed; the site will redeploy"
