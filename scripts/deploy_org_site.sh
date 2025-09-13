#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == "" ]]; then
  echo "Usage: $0 <git_remote_url>" >&2
  echo "Example: $0 git@github.com:Nuti-Consultants/Nuti-Consultants.github.io.git" >&2
  exit 1
fi

REMOTE="$1"
DIR="Nuti-Consultants.github.io"

if [[ ! -d "$DIR" ]]; then
  echo "Directory '$DIR' not found. Run from repo root." >&2
  exit 1
fi

cd "$DIR"

if [[ ! -d .git ]]; then
  git init
fi

git add .
git commit -m "Init org site" || true
git branch -M main || true
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main

echo "Pushed to $REMOTE. GitHub Pages will publish at https://nuti-consultants.github.io/"

