#!/usr/bin/env bash
# Prisma AI — minimal API workflow example
set -euo pipefail

API="${API_URL:-http://127.0.0.1:8080}"
FILE="${1:-sample-data/sales.csv}"

echo "Uploading $FILE..."
SESSION=$(curl -s -F "file=@${FILE}" "${API}/api/upload" | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
echo "Session: $SESSION"

echo "Analysis summary:"
curl -s "${API}/api/sessions/${SESSION}/analysis" | python -c "import sys,json; d=json.load(sys.stdin); print(f\"Rows: {d['profile']['rows']}, Insights: {d['insight_count']}\")"

echo "Chat:"
curl -s -X POST "${API}/api/sessions/${SESSION}/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize this dataset"}' | python -c "import sys,json; print(json.load(sys.stdin)['answer'][:200], '...')"
