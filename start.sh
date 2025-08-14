#!/usr/bin/env bash

# Helper to install dependencies and launch backend & frontend together.
# Usage: ./start.sh

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python dependencies if FastAPI is missing
if ! python -c "import fastapi" >/dev/null 2>&1; then
  echo "Installing backend dependencies..."
  pip install -r "$ROOT_DIR/requirements.txt"
fi

# Install frontend dependencies if node_modules absent
if [ ! -d "$ROOT_DIR/web/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$ROOT_DIR/web" && npm install)
fi

# Start backend FastAPI server
(
  cd "$ROOT_DIR"
  uvicorn src.app:app --reload
) &
BACKEND_PID=$!

# Start React frontend
(
  cd "$ROOT_DIR/web"
  npm start
) &
FRONTEND_PID=$!

# Ensure both processes exit when the script is terminated
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

# Wait for processes to finish
wait $BACKEND_PID $FRONTEND_PID
