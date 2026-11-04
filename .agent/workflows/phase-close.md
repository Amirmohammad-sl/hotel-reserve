---
description: Prepare a phase for delivery (on the phase's gate task branch): tests, clean clone, DB dump, demo script
---
# /phase-close <N>
Run together, INSIDE the gate task (`P<N>-gate`: P2-12, P3-11, P4-18) after `/task-start <gate-ID>` — so every file lands via a normal PR into `phase/<N>`.
This does NOT merge to main (that is `/phase-deliver`).
1. `python scripts/board.py --summary` + list of phase tasks: all `must` tasks of the phase DONE (bonus/optional may remain). Open PRs with base `phase/<N>` must be merged or consciously deferred. Run `/propagate` check: phase/<N> must not be behind its upstream.
2. Clean-clone test of the pushed branch: `git clone --branch phase/<N> --single-branch <repo-url> <tmpdir>`; follow README only: fresh DB → migrate → (P2+) seed_demo → backend tests → `npm ci && npm run build` → run. Fix README gaps.
3. Tick the phase's "Exit checklist" at the bottom of `docs/tasks/phase-<N>.md` with evidence.
4. `/db-backup phase<N>` — dump built from a SCRATCH DB migrated from THIS branch (not the dev DB).
5. Write `docs/demo/phase-<N>.md` (Persian, 5–8 min): who presents what, exact URLs, accounts/passwords from seed, click order, 5 "show the code" moments (view → form → model/manager), each operator presenting half AND able to answer on the other half.
6. Update docs/REPORT_OUTLINE.md progress. (Phase 1/Phase 2 reminders: repo link e-mail rules from TEAM.md.)
7. `/task-pr` for the gate task (Status DONE). After merge the phase is READY TO DELIVER.
8. Rehearse: `/viva-drill phase <N>` for both operators. To demo phase N later while the stack is ahead: `git worktree add ../hotel-demo-N origin/phase/<N>` (or the tag `phase-N` after delivery) + restore `db_backup/hotel_db_phase<N>.sql` into a scratch DB.
