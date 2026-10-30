---
description: Create and verify a PostgreSQL dump in db_backup/ (course requirement)
---
# /db-backup <label>   (e.g. phase2, final)
1. Confirm `pg_dump`/`psql` exist and `backend/.env` has DB_* values; confirm which DB will be dumped (name/host) with the operator.
2. Reproducibility first: ensure migrations are applied and (for phase gates) the DB was freshly built with `migrate` + `seed_demo`.
3. `bash scripts/backup_db.sh <label>`; check the file is non-empty and contains `CREATE TABLE` for all our tables.
4. Restore test into a scratch DB (`createdb hotel_restore_test`, `psql ... -f`), compare table list, then drop the scratch DB (ask before dropping).
5. Branch `chore/db-backup-<label>`, commit `chore(db): add <label> database backup`, PR as usual (reviewer = partner). Dumps contain only demo data — warn if real personal data is present.
