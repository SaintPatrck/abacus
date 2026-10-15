#!/bin/sh
# Vendor textkit from repo-a at an exact commit: scripts/sync-textkit.sh <rev>
# Reads repo-a's published remote only; never writes outside this repository (or worktree).
set -e
rev=${1:?usage: sync-textkit.sh <repo-a commit>}
root=$(git rev-parse --show-toplevel)
# A relative source is relative to the MAIN checkout, so it resolves the same from any worktree.
main=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
src=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["textkit"]["source"])' "$root/vendor.json")
case "$src" in /*) ;; *) src="$main/$src" ;; esac
tmp=$(mktemp -d)
git --git-dir="$src" archive "$rev" textkit | tar -x -C "$tmp"
[ -f "$tmp/textkit/core.py" ] || { echo "sync-textkit: $rev has no textkit/core.py; vendor/ left untouched" >&2; exit 1; }
# Replace only after a successful extract, so a failure never leaves vendor/ half-deleted.
mkdir -p "$root/vendor" && rm -rf "$root/vendor/textkit.new" && cp -R "$tmp/textkit" "$root/vendor/textkit.new"
rm -rf "$root/vendor/textkit" && mv "$root/vendor/textkit.new" "$root/vendor/textkit"
touch "$root/vendor/__init__.py"
python3 - "$root/vendor.json" "$rev" <<'EOF'
import json, sys
p, rev = sys.argv[1], sys.argv[2]
d = json.load(open(p)); d["textkit"]["rev"] = rev
open(p, "w").write(json.dumps(d, indent=2) + "\n")
EOF
rm -rf "$tmp"
echo "vendored textkit at $rev"
