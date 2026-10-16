#!/usr/bin/env bash
# Invoked by EasyBuild.ShipIt as a command-type updater (see CHANGELOG.md frontmatter).
# Receives a SemVer version (e.g. 5.0.0-rc.1), translates it to PEP 440
# (e.g. 5.0.0rc1), and writes it into pyproject.toml, reactivex/_version.py
# and uv.lock.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 <semver-version>" >&2
  exit 64
fi

SEMVER="$1"

# SemVer -> PEP 440 pre-release mapping.
# Only the common prefixes are handled; extend as needed.
PEP440=$(echo "$SEMVER" | sed -E '
  s/-alpha\.([0-9]+)$/a\1/
  s/-beta\.([0-9]+)$/b\1/
  s/-rc\.([0-9]+)$/rc\1/
')

# Restrict the substitution to the [project] table. An unanchored '^version = '
# would also rewrite a top-level version key in any later [tool.*] section.
sed -i "/^\[project\]/,/^\[/ s/^version = \".*\"/version = \"$PEP440\"/" pyproject.toml
printf '__version__ = "%s"\n' "$PEP440" > reactivex/_version.py

# uv.lock records the project's own version, so it goes stale on every release
# unless it is refreshed here. This only re-resolves the local package; the
# pinned dependency versions are left alone (that is what --upgrade would do).
uv lock --quiet

echo "Bumped version to $PEP440 (from SemVer $SEMVER)"
