---
description: Resolve merge conflicts safely and explain them in Persian
---
# /conflict
1. `git status` — list conflicted files. Never use `git checkout --ours/--theirs`, `-X ours/theirs`, `reset --hard`, or delete files to "make it go away".
2. For each file: show both sides, explain in Persian what each side intended (use `git log -p -3 -- <file>` and the journal of each task), and ask the operator which behaviour is desired. Prefer combining both.
3. Migrations: don't delete migrations. Two heads → `python manage.py makemigrations --merge`. Model edits conflicting → resolve models first, then regenerate only if needed.
4. `docs/tasks/phase-*.md` conflicts: keep both operators' status changes.
5. Remove conflict markers, run `/verify` quick checks (check, tests touching the files, lint), then `git add <files>` and `git commit` (default merge message ok).
6. Tell the partner (Persian message) if their code was affected.
