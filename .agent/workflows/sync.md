---
description: Start-of-day sync: update current branch from its base, see partner's commits, check phase-stack health
---
# /sync — start of every session
1. Identify the operator: `git config user.email` → docs/TEAM.md. Unknown → stop and ask.
// turbo
2. `git fetch --all --prune`, then `git status -sb` and `git branch --show-current`.
3. Uncommitted changes → show them and ask whether to `/commit` first. Never stash/discard silently.
4. Update the current branch:
   - On `main` or `phase/N` (you should only be there to read/demo): `git pull --ff-only`.
   - On a task branch `<type>/<ID>-<slug>`: BASE = `python scripts/board.py --base <ID>`; `git merge origin/<BASE>` (merge, never rebase). Conflicts → `/conflict`.
5. Persian summary of what arrived: `git log --oneline --no-merges ORIG_HEAD..HEAD` grouped by author, one short sentence per commit (both operators must know every commit).
6. If requirements.txt / package.json / lock / any `migrations/` changed → tell exactly what to run: `pip install -r requirements.txt`, `npm ci`, `python manage.py migrate`.
// turbo
7. Phase-stack health: for each existing pair (upstream → downstream) in `main → phase/2 → phase/3 → phase/4` run `git rev-list --count origin/<down>..origin/<up>`. If > 0 the downstream is BEHIND → tell the operator to run `/propagate` (say who should: whoever merged the last upstream PR).
// turbo
8. `gh pr list --state open --json number,title,author,baseRefName,headRefName` — show PRs waiting for THIS operator's review (author = partner), with their base branch.
// turbo
9. `python scripts/board.py --me` → recommend next step: `/review-pr N` first, then `/propagate` if needed, then `/next`.
