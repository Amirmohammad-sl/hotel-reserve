---
description: Project status for both operators: progress per phase, open PRs, risks
---
# /status
// turbo
1. `python scripts/board.py` (all tasks) and `python scripts/board.py --summary`.
// turbo
2. `gh pr list --state open` and `git log --oneline --since="7 days ago" --format="%h %an %s" | head -40` (who did what this week).
3. Read docs/TEAM.md deadlines. Compute remaining READY/BLOCKED work vs days left per phase (rough).
4. Report in Persian: % per phase · what each operator did this week · open PRs and who must review · blocked chains (and who unblocks) · top 3 risks · recommended focus for the next 2 days.
5. Check balance: commits/tasks per operator; if lopsided, suggest moving a not-started task to the lighter operator (edit `Owner:` in a docs PR).
