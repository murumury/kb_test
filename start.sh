#!/usr/bin/env bash

# Simple helper to launch the backend API and React frontend together.
# Usage: ./start.sh

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
