---
description: Finish a task: journal, status DONE, docs, push and open the PR against the task's phase branch
---
# /task-pr
1. Preconditions: on a task branch; `/verify` fully PASS in this session (else run it).
2. BASE = `python scripts/board.py --base <ID>`.
3. Create `docs/journal/<ID>.md` from `docs/journal/_TEMPLATE.md` (honest; Viva Q&A in Persian, 3–5).
4. In `docs/tasks/phase-N.md` set this task `Status: DONE` (true once merged).
5. Update affected docs (API_CONTRACT, DATA_MODEL, ARCHITECTURE, README). Commit `docs(<scope>): journal and status for <ID> [<ID>]`.
6. `git fetch`; `git merge origin/<BASE>`; if something came in, rerun quick checks; conflicts → `/conflict`.
7. `git push -u origin HEAD`.
8. `gh pr create --base <BASE> --title "[<ID>] <title>" --body-file <filled template>` with `--reviewer <partner-github-username>` (docs/TEAM.md). No `gh` → print title/body/compare URL. The PR body must state `Base: <BASE>`.
9. Tell the operator (Persian): PR link + a ready message for the partner ("PR #N (<ID>, base <BASE>) ready — run `/review-pr N`"). Then `/next`.
