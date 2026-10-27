#!/bin/bash
# Add new publications from Zotero's "Publications" collection, then commit and push after you confirm.
# Zotero must be open. See scripts/add_pubs.py for what it does; UPDATING.md for the workflow.
set -uo pipefail

SITE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SITE" || exit 1

branch=$(git symbolic-ref --short HEAD 2>/dev/null)
[ "$branch" = "main" ] || { echo "The site repo is on '$branch', not main. Switch to main first."; exit 1; }

list=$(mktemp)
trap 'rm -f "$list"' EXIT
python3 scripts/add_pubs.py --changed-list "$list" || exit 1
[ -s "$list" ] || exit 0

echo
echo "Changed files:"
sed 's/^/  /' "$list"
echo
read -r -p "Publish these to the live site now? [y/N] " answer
if [[ ! "$answer" =~ ^[Yy] ]]; then
  echo "Not published. The new and updated files are still in place: edit them (e.g. fix research areas),"
  echo "then commit and push as usual, or run this script again (already-added papers are skipped)."
  exit 0
fi

# Commit only the files this run touched, so other uncommitted work is left alone.
xargs git add -- < "$list"
xargs git commit -q -m "Add publications from Zotero" -- < "$list" || { echo "Commit failed."; exit 1; }
if ! git push -q origin main; then
  git pull -q --rebase origin main && git push -q origin main || { echo "Push failed; run 'git push' by hand."; exit 1; }
fi
echo "Pushed. Netlify will rebuild the site in a minute or two."
