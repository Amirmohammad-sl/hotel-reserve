#!/usr/bin/env bash
# Usage: scripts/restore_db.sh <file.sql> [target_db]   (defaults to DB_NAME from .env)
set -euo pipefail
FILE="${1:?usage: restore_db.sh <file.sql> [target_db]}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$ROOT/backend/.env" "$ROOT/.env"; do
  if [ -f "$f" ]; then set -a; . "$f"; set +a; break; fi
done
TARGET_DB="${2:-${DB_NAME:?DB_NAME missing}}"
PGPASSWORD="${DB_PASSWORD:-}" psql -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$TARGET_DB" -f "$FILE"
