# 01 — Git & GitHub workflow (both operators must be visible on the repo)

## Branching
- `main` is protected: PR + 1 approval from the OTHER operator + CI green. Squash-merge only.
- Branch name: `<type>/<TASK-ID>-<slug>`  e.g. `feat/P1-04-hotel-models`. Types: feat, fix, docs, chore, test, refactor.
- One task = one branch = one PR. Branches live ≤ 2–3 days; sync with `/sync` daily.
- Never force-push. To bring main into your branch use **merge** (`git merge origin/main`), not rebase.

## Commits (small and frequent — every commit must be explainable)
Format: `<type>(<scope>): <imperative summary> [<TASK-ID>]` (subject ≤ 72 chars). Body: short bullets of WHY.
Examples:
- `feat(hotels): add Hotel and RoomType models [P1-04]`
- `test(bookings): cover overlapping date availability [P4-04]`
- `wip(P3-05): half-done select_for_update (end of session)`  ← only on feature branches
Scopes: core, accounts, hotels, bookings, reviews, frontend, docs, ci, db.
- Commit under the operator's own git identity (`git config user.name/email`). Never change or fake the author.
- Commit parts logically (models separate from views separate from UI). Avoid giant "everything" commits.
- Push after every commit on your feature branch so the partner can see progress.

## Pull requests
- Created by `/task-pr` using `.github/pull_request_template.md`. Reviewer = the other operator, via `/review-pr`.
- The reviewer must pass the **understanding gate** (answer 2 questions about the diff) before approving.
- The reviewer merges via `/merge-pr` (squash, delete branch). Squash message: `[<ID>] <title> (#<PR>)`.

## Tags & backups
- At each phase end (`/phase-close N`): DB dump `db_backup/hotel_db_phaseN.sql` + annotated tag `phase-N`.
- Final: tag `final`.

## Conflicts
- Prefer avoiding them: see ownership map in 04-two-operator-protocol.md. When they happen use `/conflict`.
- Migration conflicts: `python manage.py makemigrations --merge`, never delete other people's migrations.
