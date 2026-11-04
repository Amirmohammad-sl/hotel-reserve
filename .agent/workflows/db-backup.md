---
description: Create and verify a PostgreSQL dump for a phase from a SCRATCH database built from the current branch
---
# /db-backup <label>   (e.g. phase2, phase3, final)
Never dump the developer's everyday DB: it may be ahead of (or different from) the phase code. Always rebuild from this checkout.
1. Confirm tools: `pg_dump`, `psql`, `createdb`/`dropdb` (or equivalent via psql) and `backend/.env` DB_* values. Confirm with the operator which Postgres server is used. Scripts are bash: on Windows use Git Bash or WSL.
2. Scratch DB name: `hotel_<label>_scratch`. Create it (ask before dropping if it already exists).
3. From `backend/` with the project's venv: run `migrate` and (if the command exists on this branch) `seed_demo`, with the DB name overridden for THIS command only (e.g. env var `DB_NAME=hotel_<label>_scratch` — check that settings read DB_NAME from the environment before `.env`; otherwise temporarily use a copy of `.env`).
4. `DB_NAME_OVERRIDE=hotel_<label>_scratch bash scripts/backup_db.sh <label>`; check the file is non-empty, contains `CREATE TABLE` for all our tables and includes the seed rows.
5. Restore test: create `hotel_<label>_restore`, `psql -f db_backup/hotel_db_<label>.sql`, compare table list; drop both scratch DBs (ask first).
6. Commit on the current task branch (`chore(db): add <label> database backup [<ID>]`) — it ships with the gate PR into `phase/N`.
Dumps contain demo data only — warn if real personal data is present.
