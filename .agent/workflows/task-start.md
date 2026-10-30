---
description: Begin a task: check ownership, create branch, read context, produce a plan and wait for approval
---
# /task-start <TASK-ID>
Argument = task id typed after the command (e.g. `/task-start P1-04`). If missing, run `/next` logic and ask.

1. Identify operator (git email → docs/TEAM.md). Show the task: `python scripts/board.py --task <ID>`.
2. Preconditions — stop and explain in Persian if any fails:
   - Task owner is this operator (or `AB`). If it belongs to the partner, proceed only if the operator explicitly says it's agreed pairing; note it in the PR.
   - All `Depends:` are DONE (board shows READY). No existing remote branch with this ID (else someone started it: switch to it instead).
   - Working tree clean.
3. `git fetch --prune`, `git switch main`, `git pull --ff-only`, then `git switch -c <type>/<ID>-<slug>` (slug = 2–4 lowercase words from the title).
4. Read context ONLY: AGENTS.md (done), the task block, docs it mentions (DATA_MODEL, API_CONTRACT, ARCHITECTURE, DECISIONS), the journal files of its dependencies (`docs/journal/<dep>.md`), and the specific source files you will change. Don't scan the repo.
5. If the task needs a library/tool you're unsure about (Tailwind, Vite, Leaflet…), open the official docs first.
6. Write the plan in Persian and present it:
   - Files to create/modify (with one-line purpose each) in the order you'll do them
   - Commit plan (3–6 small commits with messages)
   - Tests / checks you'll run
   - Risks, assumptions, questions
   - Contract impact: "none" or "needs /pair-contract" (then STOP)
7. **STOP and wait for the operator's approval** ("ok" / changes). Don't write code before that.
8. After approval implement step by step. After each logical unit: show `git diff --stat`, explain briefly in Persian, and suggest `/commit`.
