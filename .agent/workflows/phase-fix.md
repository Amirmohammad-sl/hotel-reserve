---
description: Fix a bug that belongs to an EARLIER phase, then carry it down the stack
---
# /phase-fix <phase-number> <short description>
Use when working on phase M and discovering a bug/missing piece that belongs to phase N < M (or to main).
1. Never fix it on the later branch (it would be lost/duplicated). Stash nothing: commit or park current work first (`/commit` or `/end-session`).
2. Branch from the EARLIER phase: `git fetch`; `git switch -c fix/p<N>-<slug> origin/phase/<N>` (for N=1 use `origin/main`).
3. Reproduce with the smallest case, write/adjust a test if cheap, fix minimally, `/verify`, `/commit` (message `fix(<scope>): ... [P<N>-fix]`).
4. PR with base `phase/<N>` via `/task-pr`-style flow (journal file `docs/journal/fix-p<N>-<slug>.md`), partner reviews, squash-merge via `/merge-pr`.
5. Immediately `/propagate` so phase/N+1…4 receive the fix. Then return to your task branch and `git merge origin/<its BASE>`.
6. If phase N was ALREADY delivered (tag exists): tell the operator the fix will reach `main` with the next delivery (it travels via propagate); if it must be graded in the delivered snapshot, they must ask the professor.
