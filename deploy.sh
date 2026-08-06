#!/usr/bin/env bash
# Deploy/CI script for running on the PythonAnywhere bash console.
#
# Usage:
#   ./deploy.sh              # pull, install deps, test, migrate, collectstatic
#   ./deploy.sh --no-pull    # skip "git pull" (deploy what's already checked out)
#   ./deploy.sh --no-tests   # skip the test suite
#
# After it finishes, reload the web app from the PythonAnywhere "Web" tab.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ACTIVATE="$PROJECT_DIR/venv/bin/activate"

DO_PULL=1
DO_TESTS=1
for arg in "$@"; do
  case "$arg" in
    --no-pull) DO_PULL=0 ;;
    --no-tests) DO_TESTS=0 ;;
    -h|--help)
      grep '^#' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }
fail() { printf '\033[1;31mERROR: %s\033[0m\n' "$1" >&2; exit 1; }

cd "$PROJECT_DIR"

if [ "$DO_PULL" -eq 1 ]; then
  step "Pulling latest code"
  if [ -n "$(git status --porcelain)" ]; then
    fail "Working tree has uncommitted changes in $PROJECT_DIR — commit or stash them first, otherwise 'git pull' may fail or clobber them."
  fi
  git pull
fi

step "Activating virtualenv"
if [ -f "$VENV_ACTIVATE" ]; then
  # shellcheck disable=SC1090
  source "$VENV_ACTIVATE"
else
  fail "No virtualenv found at $PROJECT_DIR/venv/bin/activate. Create one first, e.g.: python3.12 -m venv venv"
fi

step "Installing dependencies"
pip install -r requirements.txt

if [ "$DO_TESTS" -eq 1 ]; then
  step "Running tests"
  # Force DJANGO_ENV=development for the test run so Django builds its throwaway
  # test database against local SQLite instead of trying (and likely failing, due
  # to permissions) to CREATE a test database on the production MySQL server.
  DJANGO_ENV=development python manage.py test
fi

step "Applying database migrations"
python manage.py migrate --noinput

step "Collecting static files"
python manage.py collectstatic --noinput

step "Deploy finished"
echo "Reload the web app from the PythonAnywhere Web tab to pick up the changes."
