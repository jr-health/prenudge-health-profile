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
# The date in the download links has to be the date in the ASSET FILENAMES, which is
# NOT health-profile.json's ".generated": release.yml builds the filenames from the
# released commit's date (git log -1 --date=short), while ".generated" is the release
# build's timestamp. They only agree when the release is cut on the same UTC day as
# the last commit to main. Mirrors the same fix in pages.yml - keep the two in sync.
ASSET_NAME=$(printf '%s' "$RELEASE_JSON" \
  | grep -o '"name": *"health-profile-v[^"]*\.de\.docx"' | cut -d'"' -f4 \
  | grep -E -- '-[0-9]{4}-[0-9]{2}-[0-9]{2}\.de\.docx$' | head -1 || true)
if [ -n "$ASSET_NAME" ]; then
  GENERATED=$(printf '%s' "$ASSET_NAME" | sed -E 's/.*-([0-9]{4}-[0-9]{2}-[0-9]{2})\.de\.docx$/\1/')
else
  echo "  WARNING: no dated .docx asset on $TAG; falling back to health-profile.json .generated - download links may 404." >&2
  GENERATED=$(grep -o '"generated": *"[^"]*"' "$OUT/health-profile.json" | head -1 | cut -d'"' -f4 | cut -c1-10)
fi
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
