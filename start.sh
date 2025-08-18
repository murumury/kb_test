#!/usr/bin/env bash

# Helper to install dependencies and launch backend & frontend together.
# Usage: ./start.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Python virtualenv & deps ----------------------------------------------
# Create venv if missing and activate it
if [ ! -d "$ROOT_DIR/.venv" ]; then
  python3 -m venv "$ROOT_DIR/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

# Upgrade packaging toolchain (proxy is picked up from env if set)
python -m pip install --upgrade pip setuptools wheel

# Some old deps still reference the deprecated 'sklearn' meta-package.
# Allow installation to proceed, and we'll ensure scikit-learn is present.
export SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

# Ensure correct wheels (avoid building Rust from source for tokenizers)
pip install --only-binary tokenizers -r "$ROOT_DIR/requirements.txt"

# --- Frontend deps ----------------------------------------------------------
if [ ! -d "$ROOT_DIR/web/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$ROOT_DIR/web" && npm install)
fi

# --- Start backend ----------------------------------------------------------
(
  cd "$ROOT_DIR"
  # uvicorn from the venv
  uvicorn src.app:app --reload
) &
BACKEND_PID=$!

# --- Start frontend ---------------------------------------------------------
(
  cd "$ROOT_DIR/web"
  npm start
) &
FRONTEND_PID=$!

# Ensure both processes exit when the script is terminated
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

# Wait for processes to finish
wait $BACKEND_PID $FRONTEND_PID
