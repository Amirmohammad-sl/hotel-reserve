---
description: Start-of-day sync: pull main, merge into current branch, see what the partner merged, refresh deps
---
# /sync — start of every session
1. Identify the operator: `git config user.email` → docs/TEAM.md. Unknown → stop and ask.
// turbo
2. `git fetch --all --prune` then `git status -sb` and `git branch --show-current`.
3. If there are uncommitted changes: show them and ask the operator whether to `/commit` them first. Do NOT stash or discard silently.
4. If on `main` and clean: `git pull --ff-only origin main`. If on a feature branch and clean: `git merge origin/main` (merge, never rebase). If conflicts appear → run the `/conflict` workflow.
5. Summarize in Persian what changed since the last time on this machine: `git log --oneline --no-merges ORIG_HEAD..HEAD` (if ORIG_HEAD exists) — group by author, explain each commit in ONE short sentence. This keeps both operators aware of all commits.
6. If `backend/requirements.txt`, `frontend/package.json`/lock file, or any `migrations/` changed in that range: tell the operator exactly which of these to run: `pip install -r requirements.txt`, `npm ci`, `python manage.py migrate`.
// turbo
7. `gh pr list --state open` (if gh available) — list PRs waiting for this operator's review (they are the reviewer when the author is the partner).
// turbo
8. `python scripts/board.py --me` — show the operator's tasks and recommend the next step (`/review-pr N` first if a PR is waiting, then `/next`).
