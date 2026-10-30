---
description: Show which tasks this operator can start now and recommend one
---
# /next
// turbo
1. `python scripts/board.py --next --me` (READY tasks of this operator). Also run `python scripts/board.py --me` to see WIP and BLOCKED ones.
2. If a PR from the partner is waiting for review, recommend reviewing it first (`/review-pr <N>`) — reviews unblock the partner.
3. Recommend ONE task: prefer tasks that unblock the partner (look at other tasks' `Depends:`), then Priority `must` before `bonus`/`optional`, then smaller Size.
4. For the recommended task print: goal, deliverables, DoD (copy from `python scripts/board.py --task <ID>`), and the exact next command: `/task-start <ID>`.
5. If nothing is READY: suggest `/review-pr`, `/viva-drill`, docs/report work, or reading the partner's journal entries (`docs/journal/`).
