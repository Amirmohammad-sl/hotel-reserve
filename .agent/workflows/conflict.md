---
description: Resolve merge conflicts safely (task branch ← base, propagate PRs) and explain them in Persian
---
# /conflict
1. `git status` — list conflicted files and which merge caused it (task branch ← `origin/<BASE>` or `chore/propagate-*` ← upstream phase). Never use `--ours/--theirs`, `-X ours/theirs`, `reset --hard`, or delete files to make it disappear.
2. For each file: show both sides, explain in Persian what each side intended (`git log -p -3 -- <file>`, journals of both tasks), ask which behaviour is desired; prefer combining.
3. Stacked-phase specifics:
   - Later-phase code often REFACTORS what an earlier phase later fixes (e.g. views vs managers). Keep the later phase's structure and re-apply the earlier fix's intent on top.
   - Migrations: two leaves in one app → `python manage.py makemigrations --merge`; never delete/renumber merged migrations.
   - `docs/tasks/phase-*.md`: keep both Status changes. `docs/API_CONTRACT.md`, `DATA_MODEL.md`: merge both and re-check against code.
4. Remove markers, run `/verify` quick checks (check, makemigrations --check, relevant tests, lint/build), `git add <files>`, `git commit` (default merge message).
5. Tell the partner (Persian message) if their code was affected.
