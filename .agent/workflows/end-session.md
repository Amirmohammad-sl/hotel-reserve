---
description: Wrap up a work session: WIP commit, push, handoff notes
---
# /end-session
// turbo
1. `git status -sb`, `git branch --show-current`.
2. Uncommitted work on a feature branch → `/commit` it (use `wip(<ID>): ...` if unfinished). On `main` with changes → stop, move them to a branch first (ask).
3. Push the branch. If the task isn't finished, append a "Progress notes / next steps" section to `docs/journal/<ID>.md` (what's done, what's left, exact next command, open questions) and commit+push.
4. Print a Persian handoff summary: ✔ done · … in progress · ▶ next first step tomorrow (`/sync` then `/task-start <ID>` continues on the same branch) · ❓ open questions. Offer a short message to send the partner.
5. Remind: new day → `/sync`; new task → NEW conversation.
