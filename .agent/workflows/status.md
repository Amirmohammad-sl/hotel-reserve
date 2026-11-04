---
description: Project status across phase branches: progress, drift, open PRs, deliveries, risks
---
# /status
// turbo
1. `python scripts/board.py` and `python scripts/board.py --summary` (global view: DONE comes from each phase branch).
// turbo
2. Stack health: for `main → phase/2 → phase/3 → phase/4`: commits behind per pair; tags present (`git tag -l "phase-*" final`) → which phases are DELIVERED.
// turbo
3. `gh pr list --state open --json number,title,author,baseRefName` grouped by base branch; `git log --since="7 days ago" --format="%h %an %s" origin/phase/2 origin/phase/3 origin/phase/4 | head -60`.
4. Read docs/TEAM.md deadlines: for each phase compute days left, tasks left (READY/UPSTREAM/BLOCKED), and whether the delivery chain order is feasible (phase N+1 can't be delivered before N).
5. Persian report: progress per phase · what each operator did this week · open PRs and who reviews · UPSTREAM/BLOCKED chains · drift · top 3 risks · focus for next 2 days · commit/task balance between A and B.
