---
description: Begin a task: resolve base phase branch, branch off it, read context, plan and wait for approval
---
# /task-start <TASK-ID>
1. Identify operator. Show the task: `python scripts/board.py --task <ID>` and its BASE: `python scripts/board.py --base <ID>` (P2→phase/2, P3→phase/3, P4→phase/4, P0/P1→main).
2. Preconditions — stop and explain in Persian if any fails:
   - Owner is this operator (or `AB`); if it's the partner's task, only with explicit "agreed pairing" noted in the PR.
   - Board state is READY. If UPSTREAM → run `/propagate` first. If BLOCKED → say which tasks block it.
   - No existing remote branch containing this ID. Working tree clean.
3. `git fetch --prune`; confirm `origin/<BASE>` exists; `git switch -c <type>/<ID>-<slug> origin/<BASE>` (slug = 2–4 lowercase words). NEVER branch from main for P2+ tasks, and never work on `main` or `phase/*` directly.
4. Read ONLY: AGENTS.md, the task block, referenced docs (DATA_MODEL, API_CONTRACT, ARCHITECTURE, DECISIONS), journals of its dependencies (`docs/journal/<dep>.md`), and the files you'll change. Unsure about a library → official docs first.
5. Plan in Persian: files in order · 3–6 small commits with messages · tests/checks · risks/questions · contract impact ("none" or "needs /pair-contract" → STOP). Also state: "base branch = <BASE>".
6. **STOP and wait for approval.** No code before it.
7. Implement step by step; after each unit show `git diff --stat`, explain briefly, suggest `/commit`.
