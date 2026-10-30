---
description: Finish a task: journal, status DONE, docs, push and open the PR for the partner's review
---
# /task-pr
1. Preconditions: on a feature branch; `/verify` fully PASS in this session (otherwise run `/verify` now).
2. Create `docs/journal/<ID>.md` from `docs/journal/_TEMPLATE.md`. Fill every section honestly. Viva Q&A must be in Persian (3–5 questions a professor could ask about THIS task, with correct short answers).
3. In `docs/tasks/phase-N.md` set this task's `Status: DONE` (it becomes true when the PR merges).
4. Update docs affected by the change (API_CONTRACT, DATA_MODEL, ARCHITECTURE, README) so docs == code.
5. Commit: `docs(<scope>): journal and status for <ID> [<ID>]`.
6. `git fetch`, `git merge origin/main`; if anything merged in, rerun the quick checks. Conflicts → `/conflict`.
7. `git push -u origin HEAD`.
8. Open the PR: `gh pr create --base main --title "[<ID>] <title>" --body-file <filled .github/pull_request_template.md>` and request review from the partner's GitHub username (docs/TEAM.md): `--reviewer <username>`. If `gh` is unavailable, print the PR title/body for manual creation and the compare URL.
9. Tell the operator (Persian): PR number/link, and a ready-to-send message for the partner: "PR #N for <ID> is ready — please run `/review-pr N`. Key points to look at: …". Remind them to switch to `/next` while waiting.
