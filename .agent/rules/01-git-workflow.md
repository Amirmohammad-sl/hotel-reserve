# 01 — Git & GitHub workflow (PHASE-BRANCH MODEL, v2)

Goal: finish the project early WITHOUT delivering early. We build phases 2, 3, 4 ahead of their deadlines on long-lived
phase branches, and merge a phase into `main` only on its delivery day. Full explanation: docs/PHASE_BRANCHES.md.

## Branches
| Branch | Purpose | Who may change it |
|---|---|---|
| `main` | ONLY delivered state. Tags `phase-1`, `phase-2`, … `final` | delivery PRs (`/phase-deliver`) only |
| `phase/2`, `phase/3`, `phase/4` | integration branch of each phase (**stacked**: phase/3 contains phase/2, phase/4 contains phase/3) | task PRs + propagate PRs only |
| `<type>/<TASK-ID>-<slug>` | one task | the task author |
| `chore/propagate-p<N>-into-p<M>` | carries upstream work down the stack | whoever merged the upstream PR |
| `fix/p<N>-<slug>` | fix for an EARLIER phase found later (`/phase-fix`) | author |

All of `main` and `phase/*` are protected: PR + 1 approval from the OTHER operator + CI green. No force-push, no deletion.

## Which branch is the BASE of a task?
Derived from the task id: `P2-xx → phase/2`, `P3-xx → phase/3`, `P4-xx → phase/4`, `P0/P1 → main` (only for fixes).
Ask the board: `python scripts/board.py --base <TASK-ID>`.
- Cut the task branch from `origin/<BASE>`, open the PR against `<BASE>` (never against main unless base is main).

## Flow direction (the one rule that keeps this sane)
Changes flow ONE way: `main → phase/2 → phase/3 → phase/4`. A fix for phase 2 is made on `phase/2` (via `/phase-fix`) and then
carried down with `/propagate`. NEVER merge a later phase into an earlier one, NEVER cherry-pick between phases.

## Merge methods (important — the wrong one breaks the stack)
| PR | Method |
|---|---|
| task PR → phase/N | **Squash** (one commit per task), delete task branch |
| propagate PR (upstream → downstream phase) | **Merge commit** (never squash/rebase — history must be shared) |
| delivery PR (phase/N → main) | **Merge commit**, do NOT delete the phase branch |
Branch → task branches sync with `git merge origin/<BASE>` (no rebase, no force push).

## Commits (small, explainable)
Format: `<type>(<scope>): <imperative summary> [<TASK-ID>]` (≤ 72 chars) + bullets about WHY.
Types: feat, fix, docs, chore, test, refactor, wip (wip only on task branches, end of session).
Scopes: core, accounts, hotels, bookings, reviews, frontend, docs, ci, db.
- Commit under your own git identity. Push after every commit. Never commit directly on `main` or `phase/*`.

## Pull requests
- Created by `/task-pr` (template `.github/pull_request_template.md`), reviewer = the other operator via `/review-pr`, merged by the reviewer via `/merge-pr`.
- Reviewer passes the understanding gate (2 questions) before approving.

## Migrations & shared docs in a stacked world
- Prefer schema changes in the EARLIEST phase that needs them. If two branches add migrations to the same app, the propagate PR
  resolves it with `python manage.py makemigrations --merge` (never delete migrations).
- docs/API_CONTRACT.md, DATA_MODEL.md, ARCHITECTURE.md may conflict on propagate — `/conflict` explains how.

## Delivery day
`/phase-close N` (prepare: tests, DB dump, demo script) any time before; `/phase-deliver N` on the day: PR `phase/N → main`
(merge commit), tag `phase-N`. A phase can only be delivered after the previous phase was delivered.
`main` must receive nothing else (except the rare docs/hotfix PR; then `/propagate` immediately).

## Backups & tags
- DB dump per phase `db_backup/hotel_db_phaseN.sql`, built from a SCRATCH database migrated from that phase's code (never from your dev DB, which may be ahead).
- Tags: annotated `phase-N` on the delivery merge commit, `final` at the end. (Branches are `phase/N`; tags are `phase-N` — different names on purpose.)
