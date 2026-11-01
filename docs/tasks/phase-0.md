# Phase 0 — Setup (before Phase 1 work)

### P0-01 · Create GitHub repo, import kit, protect main
- Owner: A
- Depends: –
- Size: S
- Priority: must
- Status: DONE
- Goal: Shared repo exists, both operators can push branches, main is protected.
- Deliverables:
  - `git init`, first commit `chore: import agent kit [P0-01]`, push to a new GitHub repo (private; add professor later per TEAM.md).
  - Invite B as collaborator (write). Fill repo URL + A's row in docs/TEAM.md.
  - Settings → Branches: protect `main` (require PR, 1 approval, dismiss stale approvals, no force push, require status checks `backend` and `frontend` once P0-05 ran once). Settings → General: allow squash merge only, auto-delete head branches.
- DoD:
  - [x] B can push a feature branch; a direct push to `main` is rejected.
  - [x] Screenshot of branch-protection settings saved in docs/journal/P0-01.md

### P0-02 · Onboard Operator B through the full cycle
- Owner: B
- Depends: P0-01
- Size: S
- Priority: must
- Status: DONE
- Goal: B clones, runs `/bootstrap`, and completes ONE tiny PR through the entire review loop (proves the process).
- Deliverables:
  - B fills own row in docs/TEAM.md via PR (this PR is the dry run: `/task-start` → `/commit` → `/verify` → `/task-pr` → A runs `/review-pr` → `/merge-pr`).
  - docs/journal/P0-02.md.
- DoD:
  - [x] PR merged with B as author and A as approver; A's `git config user.email` also present in TEAM.md.
  - [x] Both can run `python scripts/board.py --me` and see their own tasks.

### P0-03 · Django scaffold + PostgreSQL + custom User skeleton
- Owner: A
- Depends: P0-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Runnable Django project on PostgreSQL, custom user model in place BEFORE the first migrate.
- Deliverables:
  - `backend/` with venv instructions, `requirements.txt` (Django 5.x, psycopg[binary], django-environ, coverage), project `config/`, settings from env, `apps/` package.
  - Apps `core` and `accounts` created; `accounts.User(AbstractUser)` (extra fields come in P1-03); `AUTH_USER_MODEL = "accounts.User"`.
  - `GET /api/health/` → `{"data": {"status": "ok"}}`; `apps/core/http.py` with `json_ok/json_error/parse_json` (minimal).
  - `backend/.env` from `.env.example` (not committed). DB `hotel_db` created (docker compose or local Postgres).
- DoD:
  - [x] `python manage.py check` OK · `python manage.py migrate` OK on PostgreSQL · `python manage.py test` runs.
  - [x] `curl localhost:8000/api/health/` returns the JSON above.
  - [x] README section "Backend quick start" added to root README.md.

### P0-04 · React + Vite + Tailwind scaffold
- Owner: B
- Depends: P0-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Frontend shell that talks to the backend.
- Deliverables:
  - `frontend/` Vite React (JS), Tailwind per official guide, React Router, RTL + Vazirmatn (see DECISIONS D-005), ESLint.
  - Layout (Navbar, Footer), placeholder routes (/, /login, /register, /hotels, /manager).
  - `src/api/client.js` (CSRF + credentials + error normalisation). Vite proxy `/api` → `http://localhost:8000`.
  - Home page shows backend health badge from `/api/health/`.
- DoD:
  - [x] `npm run dev` shows the shell; badge is green when Django runs.
  - [x] `npm run lint` and `npm run build` pass.
  - [x] README section "Frontend quick start".

### P0-05 · Verify CI and require status checks
- Owner: A
- Depends: P0-03, P0-04
- Size: S
- Priority: must
- Status: DONE
- Goal: CI runs on PRs and blocks merging when red.
- Deliverables:
  - Confirm `.github/workflows/ci.yml` passes on a PR; fix paths/env if needed.
  - Add `backend` and `frontend` as required checks in branch protection.
- DoD:
  - [x] A PR shows both checks green; a deliberately failing test PR (closed afterwards) shows red and blocks merge.

### P0-06 · Professor alignment e-mail + deadlines
- Owner: B
- Depends: P0-01
- Size: S
- Priority: must
- Status: DONE
- Goal: Confirm the hybrid architecture (D-001) and get phase deadlines; schedule the "repo link e-mail" (one day before Phase 1).
- Deliverables:
  - Send docs/PROFESSOR_EMAIL.md (edited). Record answer (or "no reply by <date> → proceed") in DECISIONS D-001 and deadlines in TEAM.md.
  - Calendar reminder for the repo-link email.
- DoD:
  - [x] Email sent (copy in docs/blockers/). D-001 status updated.

## Exit checklist (Phase 0)
- [ ] Both operators have merged at least one PR; repo protected; CI green; backend + frontend start locally for both.
