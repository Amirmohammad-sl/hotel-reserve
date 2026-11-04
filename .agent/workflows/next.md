---
description: Show which tasks this operator can start now (across phases) and recommend one
---
# /next
// turbo
1. `python scripts/board.py --next --me` (READY) and `python scripts/board.py --me` (all states). States: ▶ READY · ↧ UPSTREAM (deps done on an earlier phase branch but not yet propagated into this task's base branch → `/propagate`) · … WIP · ✖ BLOCKED · ✔ DONE.
2. Priorities: (1) review a waiting PR from the partner, (2) `/propagate` if it unlocks UPSTREAM tasks, (3) a task that unblocks the partner, (4) earlier phase before later phase (their deadline comes first), (5) `must` before `bonus`/`optional`, (6) smaller Size.
3. Parallel-phase rule: starting a later-phase task while an earlier phase is unfinished is OK only if the board says READY (its real dependencies exist in its base branch).
4. For the chosen task print goal, deliverables, DoD (`python scripts/board.py --task <ID>`), its BASE branch, and the next command `/task-start <ID>`.
5. Nothing READY → `/review-pr`, `/propagate`, `/viva-drill`, report docs, or read partner's journal files.
