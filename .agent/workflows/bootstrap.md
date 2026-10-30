---
description: One-time machine setup check for an operator (tools, venv, DB, deps, git identity)
---
# /bootstrap — first-time setup on this laptop
Talk to the operator in Persian. Do each step, show output, and stop to ask if something fails.

1. Check tools and print versions (don't install anything silently): `git --version`, `python --version` (need 3.12+), `node --version` (20+), `npm --version`, `psql --version`, `gh --version` (GitHub CLI; if missing, explain how to install and `gh auth login`).
// turbo
2. `git config user.name && git config user.email` — if empty, ask the operator for their real name/e-mail and set them with `git config --global`. These must match docs/TEAM.md (their row) so the board and commits attribute correctly.
3. Run `python scripts/board.py --me`. If it says it cannot identify the operator, tell the operator to add their email to docs/TEAM.md via the P0-01/P0-02 task.
4. If `backend/manage.py` exists: create venv `backend/.venv`, `pip install -r backend/requirements.txt`, copy `.env.example` → `backend/.env` (if absent), ask the operator to confirm DB credentials, make sure PostgreSQL is running (`docker compose up -d` or local service), create DB `hotel_db` if missing, then `python manage.py migrate` and `python manage.py test`.
5. If `frontend/package.json` exists: `cd frontend && npm ci` (or `npm install`), then `npm run lint --if-present` and `npm run build`.
6. Print a Persian checklist of what works / what's missing, and the next command: `/next`.
