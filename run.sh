#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

LINT_PATHS=(
    accounts
    core
    transactions
    tests
    manage.py
)

if ! command -v flake8 >/dev/null 2>&1; then
    echo "flake8 not found. Install dev dependencies first:"
    echo "  pip install -r requirements/dev.txt"
    exit 1
fi

echo "Running flake8..."
flake8 "${LINT_PATHS[@]}"
echo "flake8 passed."
