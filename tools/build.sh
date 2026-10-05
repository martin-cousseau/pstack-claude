#!/usr/bin/env bash
# Rebuild plugin/ from cursor/plugins and package dist/pstack.plugin.
#
# Usage: tools/build.sh [upstream-ref]   (default: origin/main)
#
# Prints the upstream SHA and version it built from. It never writes UPSTREAM;
# the sync runbook records that only after tools/verify.py passes.
set -euo pipefail

repo=$(cd "$(dirname "$0")/.." && pwd)
up="$repo/.upstream/plugins"
ref="${1:-origin/main}"

if [ ! -d "$up/.git" ]; then
	git clone --quiet --filter=blob:none https://github.com/cursor/plugins.git "$up"
fi
git -C "$up" fetch --quiet origin main
git -C "$up" checkout --quiet --detach "$ref"

sha=$(git -C "$up" rev-parse HEAD)
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$up/pstack/.cursor-plugin/plugin.json")

# Port revision: claude.N restarts at 1 on a new upstream version and bumps when
# the same upstream version gets new commits, so `/plugin update` sees a change.
manifest="$repo/plugin/.claude-plugin/plugin.json"
prev_version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest" 2>/dev/null || true)
prev_sha=$(cat "$repo/UPSTREAM" 2>/dev/null || true)
rev=1
if [ "${prev_version%-claude.*}" = "$version" ]; then
	prev_rev=${prev_version##*-claude.}
	if [ "$prev_sha" = "$sha" ]; then rev=$prev_rev; else rev=$((prev_rev + 1)); fi
fi

export UPSTREAM_DIR="$up" OUT="$repo/plugin" UPSTREAM_SHA="$sha" UPSTREAM_VERSION="$version" PORT_REV="$rev"
python3 "$repo/tools/convert.py"
python3 "$repo/tools/apply_patches.py"

mkdir -p "$repo/dist"
rm -f "$repo/dist/pstack.plugin"
(cd "$repo/plugin" && zip -qr "$repo/dist/pstack.plugin" . -x '*.DS_Store' -x '*/node_modules/*')

echo "built pstack ${version}-claude.${rev} from cursor/plugins@${sha}"
