# AGENTS.md — Hotel Booking (Web Programming course project)

> Read this file completely at the start of EVERY conversation. Then read only the task you were given
> (docs/tasks/phase-N.md) and the docs it references. Do NOT scan the whole repository.
> Detailed rules live in `.agent/rules/`. Slash-commands live in `.agent/workflows/`.

## 0. Language
- Talk to the operators in **Persian (Farsi)**: simple, short, friendly. Technical terms stay in English
  (model, view, queryset, migration...).
- Code, identifiers, comments, commit messages, branch names, PR titles/bodies: **English**.
- Text shown to end users in the website UI: **Persian, RTL** (see docs/DECISIONS.md D-005).

## 1. The project
A hotel search & reservation website for a university Web Programming course.
- Two roles: **Hotel Manager** (defines hotels, room types, discount codes, sees bookings/availability) and
  **Guest** (searches, views, books rooms, uses discount codes).
- No bank gateway (explicitly not required by the course).
- Two students ("Operator A" and "Operator B") build it with AI agents, phase by phase. The professor will
  question BOTH students about ALL code and ALL commits. Therefore: small tasks, cross-review, journal notes.
- Source of truth for requirements: docs/PLAN.md and `.agent/rules/00-course-requirements.md`.

## 2. Stack (fixed — change only via /decision)
| Layer | Choice |
|---|---|
| Backend | Python 3.12, Django 5.x, **plain Django views + Django Forms** returning JSON (no DRF) |
| DB | **PostgreSQL** (mandatory by the course) |
| Auth | Django session auth (cookie) + CSRF. No JWT, no localStorage tokens |
| Frontend | React (JavaScript, NOT TypeScript) + Vite + React Router + Tailwind CSS, `fetch` API |
| Tests | Django test runner (`python manage.py test`), coverage.py |
| CI | GitHub Actions (.github/workflows/ci.yml) |

## 3. Repository layout
```
backend/            Django project (manage.py, config/, apps/, templates/)
  apps/core/        shared helpers: JSON responses, decorators, middleware, logging utils
  apps/accounts/    custom User (role), auth views, email verification
  apps/hotels/      Hotel, Amenity, RoomType (+ manager-side CRUD, public search)
  apps/bookings/    Booking, DiscountCode, availability logic
  apps/reviews/     Review (bonus)
frontend/           React + Vite + Tailwind (src/api, src/pages, src/components, src/context)
docs/               PLAN, TEAM, ARCHITECTURE, DATA_MODEL, API_CONTRACT, DECISIONS, tasks/, journal/ ...
scripts/            board.py (task board), backup_db.sh, restore_db.sh
db_backup/          PostgreSQL dumps required by the course (committed at each phase end)
.agent/             rules + workflows (slash-commands) for Antigravity
```

## 4. HARD RULES (never break)
1. Never push or commit to `main` or `phase/*`. Never force-push. Never `git reset --hard`, `git clean -fd`, or rewrite history
   without the operator explicitly typing the confirmation.
2. Work on ONE task per conversation, on its own branch `<type>/<TASK-ID>-<slug>` cut from the task's PHASE branch. Do not touch things outside the task.
3. Never commit secrets (`.env`, keys, passwords), `node_modules/`, `venv/`, `logs/`, `__pycache__/`.
4. Never invent endpoints, fields, or models. Follow `docs/API_CONTRACT.md` and `docs/DATA_MODEL.md`.
   If the contract must change → stop and tell the operator to run `/pair-contract`.
5. Never add a new dependency (pip/npm) without `/decision`.
6. Never say "done / passes / works" without showing real command output (see `/verify`).
7. Never edit an already-merged migration. Add a new one.
8. Never modify files owned by the other operator's app without it being written in the task
   (see `.agent/rules/04-two-operator-protocol.md`).
9. Never log passwords, tokens, or full session keys.
10. If you are unsure or the task is ambiguous: STOP and ask the operator (in Persian). A short question is cheaper than a wrong 300-line change.

## 5. How to work (the model is fast but weak at long context — be explicit and small)
1. Read: this file → the task block → referenced docs → only the files you must change.
2. Write a short plan (Persian, bullets: files, order, tests, risks). WAIT for operator approval.
3. Implement in small steps (≤ ~150 changed lines per commit). Suggest `/commit` after each step.
4. Run `/verify`. Fix failures. Only then `/task-pr`.
5. Always finish a reply with: **what I did / what to run / what is next**.

## 6. Command cheat sheet
```
# backend (from backend/)
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver                              # http://localhost:8000
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
coverage run manage.py test && coverage report
python manage.py seed_demo                              # after P2-10

# frontend (from frontend/)
npm ci            # or npm install the first time
npm run dev       # http://localhost:5173 (proxies /api -> :8000)
npm run lint
npm run build

# board
python scripts/board.py --me          # my tasks
python scripts/board.py --next --me   # what can I start now
```

## 7. Definition of Done (every task)
- Code matches the task's DoD list and the contract docs.
- `/verify` passed with evidence; no console errors; no leftover debug prints.
- Logging added where the task touches behaviour (after P3-08: mandatory).
- Docs touched if behaviour/contract changed (API_CONTRACT, DATA_MODEL, ARCHITECTURE).
- `docs/journal/<TASK-ID>.md` written (summary + 3–5 viva questions with answers).
- Task block `Status: DONE` in the PR. PR reviewed by the OTHER operator, who must be able to explain the change.

## 8. Branch model (v2) — READ `.agent/rules/01-git-workflow.md` and docs/PHASE_BRANCHES.md
- `main` = delivered phases only. Long-lived stacked branches `phase/2` → `phase/3` → `phase/4` hold work ahead of deadlines.
- Base branch of a task: P2→`phase/2`, P3→`phase/3`, P4→`phase/4` (P0/P1→`main`). Ask: `python scripts/board.py --base <ID>`.
- Task PR → its phase branch (squash). `/propagate` carries upstream work down (merge commit). `/phase-deliver N` merges `phase/N` → `main` (merge commit).
- Fix for an earlier phase → `/phase-fix`, never on the later branch. Changes flow only downward: main → phase/2 → phase/3 → phase/4.
