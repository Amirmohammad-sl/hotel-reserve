---
description: Safe, small commit with conventional message and task id; pushes the task branch
---
# /commit [hint]
// turbo
1. `git branch --show-current` — REFUSE if it is `main` or starts with `phase/` (tell the operator to create/switch to a task branch). Extract TASK-ID from the branch name (propagate/fix branches have their own naming).
// turbo
2. `git status --short`, `git diff --stat`; explain in Persian what is committed. Flag secrets/.env, logs, node_modules, venv, big binaries, files outside the task, debug prints.
3. Quick checks for touched areas: backend `python manage.py check` (+ `makemigrations --check --dry-run` if models changed); frontend `npm run lint --if-present`. Fix before committing.
4. Stage explicit paths. One logical change per commit.
5. Message: `<type>(<scope>): <imperative summary> [<TASK-ID>]` (≤ 72 chars) + optional why-bullets.
6. `git commit`, then `git push -u origin HEAD`.
7. Print short hash, one-line summary, next suggested step.
