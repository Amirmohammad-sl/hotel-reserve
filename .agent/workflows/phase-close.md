---
description: Close a phase: clean-clone test, fresh DB + seed, DB dump, tag, demo script (both operators)
---
# /phase-close <N>
Run together (both operators present — the course requires both at every delivery).
1. `python scripts/board.py --summary`: every task of the phase must be DONE (bonus/optional may remain). List exceptions and ask.
2. `/sync` on main; open PRs of this phase must be merged or consciously deferred.
3. Clean-clone test: clone the repo into a temp dir, follow README only: fresh DB → `migrate` → (from Phase 2) `seed_demo` → backend tests → `npm ci && npm run build` → run. Fix README if any step failed (small docs PR).
4. Phase-specific exit checklist at the bottom of `docs/tasks/phase-<N>.md`: tick each item with evidence.
5. `/db-backup phase<N>` (merge that PR).
6. Update docs/REPORT_OUTLINE.md progress. Phase 1 reminder: e-mail the repo link ONE DAY before the deadline.
7. Create the demo script (Persian, ~5–8 min): who shows what, in which order, with exact URLs/accounts — split so each operator presents half and can answer about the other half.
8. After both confirm: `git switch main && git pull --ff-only`, `git tag -a phase-<N> -m "Phase <N> delivery"`, `git push origin phase-<N>`.
9. Run `/viva-drill phase <N>` for both operators before the real delivery.
