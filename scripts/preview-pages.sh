#!/usr/bin/env bash
# Builds a local mirror of the GitHub Pages site (Explore, Downloads, sunburst,
# browse) so it can be checked in a browser before pushing - mirrors the build
# steps in .github/workflows/pages.yml:
#   - version/generated/health-profile.json come from the actual latest GitHub
#     Release (public API, no auth needed), not the possibly-stale local checkout
#   - render/, admin/, media/ are pinned to that release's tagged commit via
#     `git archive`, same as pages.yml's "Checkout released commit" step
#
# Output goes to _site_test/ (already gitignored). Re-run any time; it wipes
# and rebuilds that directory.
#
# Usage: scripts/preview-pages.sh [port]   (default port: 8000)

set -euo pipefail
cd "$(dirname "$0")/.."

REPO="jr-health/prenudge-health-profile"
OUT="_site_test"
PORT="${1:-8000}"

PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" --version >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done
if [ -z "$PY" ]; then
  for candidate in "$USERPROFILE/AppData/Local/miniconda3/python.exe" "$USERPROFILE/miniconda3/python.exe" "$USERPROFILE/Anaconda3/python.exe"; do
    if [ -f "$candidate" ]; then
      PY="$candidate"
      break
    fi
  done
fi
if [ -z "$PY" ]; then
  echo "No working Python interpreter found (tried python3, python, common Miniconda/Anaconda paths)." >&2
  exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT"

echo "Resolving latest GitHub release..."
RELEASE_JSON=$(curl -sf "https://api.github.com/repos/$REPO/releases/latest")
TAG=$(printf '%s' "$RELEASE_JSON" | grep -o '"tag_name": *"[^"]*"' | head -1 | cut -d'"' -f4)
VERSION="${TAG#v}"
echo "  Latest release: $TAG"

ASSET_URL=$(printf '%s' "$RELEASE_JSON" | grep -o '"browser_download_url": *"[^"]*health-profile\.json"' | cut -d'"' -f4)
curl -sfL "$ASSET_URL" -o "$OUT/health-profile.json"
GENERATED=$(grep -o '"generated": *"[^"]*"' "$OUT/health-profile.json" | head -1 | cut -d'"' -f4 | cut -c1-10)
echo "  Generated: $GENERATED"

echo "Pinning render/admin/media to the released commit ($TAG)..."
git archive "$TAG" render admin media | tar -x -C "$OUT"

echo "Rendering Explore/Downloads pages..."
"$PY" scripts/render_index.py \
  --version "$VERSION" \
  --generated "$GENERATED" \
  --release-base "https://github.com/$REPO/releases/latest/download" \
  --profile "$OUT/health-profile.json" \
  --out-dir "$OUT"

echo
echo "Build done: $OUT/"
echo "Serve it with:"
echo "  cd $OUT && \"$PY\" -m http.server $PORT"
echo "then open http://localhost:$PORT/index.html"
