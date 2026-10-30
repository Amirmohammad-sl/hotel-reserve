---
description: Safe, small commit with conventional message and task id; pushes the feature branch
---
# /commit [optional hint]
// turbo
1. `git branch --show-current` — refuse if it is `main`. Extract TASK-ID from the branch name.
// turbo
2. `git status --short` and `git diff --stat`. Explain to the operator (Persian) what is being committed. Flag: secrets/.env, logs, node_modules, venv, big binaries, files outside the task, debug prints, TODO leftovers. Remove or ask.
3. Run the narrowest quick checks relevant to the changed files: backend → `python manage.py check` (and `makemigrations --check --dry-run` if models changed); frontend → `npm run lint --if-present`. Show output; fix before committing.
4. Stage explicit paths (`git add <paths>`); avoid `git add .` unless status was reviewed and everything belongs together. Keep one logical change per commit (split if needed).
5. Message: `<type>(<scope>): <imperative summary> [<TASK-ID>]` (≤ 72 chars) + optional body bullets (why). Types: feat, fix, docs, chore, test, refactor, wip (wip only for end-of-session).
6. `git commit -m "..."` then `git push -u origin HEAD` (feature branches only).
7. Print the short hash + one-line summary + "next suggested step".
