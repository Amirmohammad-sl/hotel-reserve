#!/usr/bin/env bash
# Usage: scripts/backup_db.sh <label>      e.g. phase2, phase3, final
# Creates db_backup/hotel_db_<label>.sql (plain SQL, readable by the professor).
# To dump a SCRATCH database instead of the one in .env:  DB_NAME_OVERRIDE=hotel_phase2_scratch bash scripts/backup_db.sh phase2
set -euo pipefail
LABEL="${1:-manual}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$ROOT/backend/.env" "$ROOT/.env"; do
  if [ -f "$f" ]; then set -a; . "$f"; set +a; break; fi
done
if [ -n "${DB_NAME_OVERRIDE:-}" ]; then DB_NAME="$DB_NAME_OVERRIDE"; fi
: "${DB_NAME:?DB_NAME missing}"; : "${DB_USER:?DB_USER missing}"
OUT="$ROOT/db_backup/hotel_db_${LABEL}.sql"
mkdir -p "$ROOT/db_backup"
echo "Dumping database: $DB_NAME"
PGPASSWORD="${DB_PASSWORD:-}" pg_dump -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" \
  --no-owner --no-privileges --clean --if-exists "$DB_NAME" > "$OUT"
echo "Backup written: $OUT ($(wc -c < "$OUT") bytes)"
grep -c "CREATE TABLE" "$OUT" | xargs echo "CREATE TABLE statements:"
