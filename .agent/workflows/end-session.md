---
description: Wrap up a work session: WIP commit, push, handoff notes
---
# /end-session
// turbo
1. `git status -sb`, `git branch --show-current`.
2. Uncommitted work on a task branch → `/commit` (use `wip(<ID>): ...` if unfinished). If you are on `main` or `phase/*` with changes → STOP: move them to a task branch (ask) — those branches are never edited directly.
3. Push the branch. If unfinished, add "Progress notes / next steps" to `docs/journal/<ID>.md`, commit and push.
4. Check `git rev-list --count origin/<BASE>..HEAD` vs behind-count; if the branch is far behind its base, note "run /sync first thing tomorrow".
5. Persian handoff summary: ✔ done · … in progress · ▶ first step tomorrow (`/sync`, `/task-start <ID>` continues on the same branch) · ❓ questions. Offer a message for the partner. Remind: if you merged an upstream PR today and haven't, run `/propagate`.
