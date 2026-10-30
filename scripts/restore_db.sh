#!/usr/bin/env bash
# Usage: scripts/restore_db.sh db_backup/hotel_db_phase1.sql   (restores INTO the DB from .env)
set -euo pipefail
FILE="${1:?usage: restore_db.sh <file.sql>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$ROOT/backend/.env" "$ROOT/.env"; do
  if [ -f "$f" ]; then set -a; . "$f"; set +a; break; fi
done
PGPASSWORD="${DB_PASSWORD:-}" psql -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -f "$FILE"
