#!/usr/bin/env bash
# Prisma AI — dev startup (backend :8080 + frontend :3000)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "Starting Prisma AI dev stack..."

# Free ports if something is listening (best effort)
for port in 8080 3000; do
  if command -v lsof >/dev/null 2>&1; then
    lsof -ti:"$port" | xargs -r kill -9 2>/dev/null || true
  fi
done

echo "Starting backend on http://127.0.0.1:8080 ..."
(
  cd "$BACKEND"
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
) &

sleep 3

echo "Starting frontend on http://localhost:3000 ..."
(
  cd "$FRONTEND"
  npm run dev
) &

sleep 4
if command -v curl >/dev/null 2>&1; then
  curl -sf "http://127.0.0.1:8080/health" && echo ""
fi

echo "Open http://localhost:3000 — upload a dataset after each backend restart."
wait
