#!/usr/bin/env bash
set -euo pipefail
command -v git >/dev/null || { echo 'Git is required'; exit 1; }
PUBLISH_ROOT="$(cd "$(dirname "$0")" && pwd)"
REMOTE="https://github.com/yannickmoiseilunga/yannickmoiseilunga.git"
TARGET="research/principia-ai-laboratory"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
 git clone "$REMOTE" "$TMPDIR/repo"
mkdir -p "$TMPDIR/repo/$TARGET"
cp -a "$PUBLISH_ROOT"/. "$TMPDIR/repo/$TARGET/"
rm -f "$TMPDIR/repo/$TARGET/publish_to_github.sh" "$TMPDIR/repo/$TARGET/publish_to_github.bat"
cd "$TMPDIR/repo"
git add "$TARGET"
# Version ZIPs intentionally ignore reports/ to avoid normal development runs. Force-add the frozen evidence snapshots.
for v in v1 v2 v3; do git add -f "$TARGET/versions/$v/reports"; done
# GitHub Actions must live at repository root, not inside research/.
mkdir -p .github/workflows
cp "$PUBLISH_ROOT/.github/workflows/checks.yml" .github/workflows/principia-lab-checks.yml
git add .github/workflows/principia-lab-checks.yml
if git diff --cached --quiet; then echo 'No changes to publish.'; exit 0; fi
git commit -m 'Publish full Principia AI Laboratory V1 V2 V3 sources and evidence'
git push origin HEAD:main
printf 'Published: https://github.com/yannickmoiseilunga/yannickmoiseilunga/tree/main/%s
' "$TARGET"
