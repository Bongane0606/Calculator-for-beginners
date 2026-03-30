#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8030}"
HOST="${2:-127.0.0.1}"

cd "$ROOT_DIR"
echo "Starting Student Analysis web app on http://${HOST}:$PORT/ (bind=${HOST})"
python3 student-analysis/server.py "$PORT" "$HOST"
