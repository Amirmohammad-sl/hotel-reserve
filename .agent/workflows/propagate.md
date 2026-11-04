---
description: Carry upstream phase work down the stack (main → phase/2 → phase/3 → phase/4) with merge-commit PRs
---
# /propagate
Why: later phase branches must contain everything earlier phases got, otherwise they drift and the delivery merges explode.
Direction is ALWAYS downward. Never merge downstream into upstream.
// turbo
1. `git fetch --all --prune`. Chain = existing branches among `main → phase/2 → phase/3 → phase/4`.
// turbo
2. For each consecutive pair (up, down): `git rev-list --count origin/<down>..origin/<up>`. Skip pairs with 0. Show the operator a table (Persian) with counts and the commit list: `git log --oneline origin/<down>..origin/<up>`.
3. Handle the FIRST behind pair only (then repeat for the next; the next pair changes after this one merges):
   - `git switch -c chore/propagate-<up>-into-<down> origin/<down>` (use p2/p3/p4 or `main` in the name, e.g. `chore/propagate-p2-into-p3`).
   - `git merge --no-ff origin/<up>` (merge commit, message `chore: propagate <up> into <down>`).
   - Conflicts → follow `/conflict` (extra: two Django migration leaves → `python manage.py makemigrations --merge`; docs/tasks status lines: keep both sides).
   - Run `/verify` (check, makemigrations --check, tests, lint, build). Auto-merged code can still be semantically broken.
4. `git push -u origin HEAD`; `gh pr create --base <down> --title "chore: propagate <up> into <down>" --body "<summary of incoming commits>" --reviewer <partner>`.
5. Tell the partner (Persian message): "propagate PR #N ready; review = conflict resolutions + CI; merge with merge-commit (/merge-pr)".
6. When it is merged, loop to the next pair. Goal: no downstream branch is more than 1 day behind.
