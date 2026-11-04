---
description: Review a PR (task, propagate, or delivery): teach it in Persian, run checks, understanding gate, approve/request changes
---
# /review-pr <PR-NUMBER>
1. Identify operator. `gh pr view <N> --json author,title,headRefName,baseRefName,body,files`. Same author as this operator → refuse.
2. Classify the PR:
   - **Task PR** (head `<type>/<ID>-…`, base `phase/N`): full review below.
   - **Propagate PR** (head `chore/propagate-*`): no new features — review CONFLICT RESOLUTIONS and that build/tests still pass (semantic conflicts hide here). Check migrations (single leaf per app).
   - **Delivery PR** (base `main`, head `phase/N`): check delivery checklist: all phase tasks DONE, CI green, DB dump present, tag plan, demo script `docs/demo/phase-N.md`, previous phase already delivered.
3. `gh pr checkout <N>`. Read PR body, `docs/journal/<ID>.md`, the task block (goal + DoD), then `git diff origin/<BASE>...HEAD --stat` and file by file.
4. **Teach (Persian)**: goal in one sentence · files and how they connect · follow ONE request/click end-to-end · key concepts and why · what could break.
5. Run `/verify` steps on this checkout (deps, migrate on a scratch DB if needed).
6. Checklist: DoD+contract · security (auth, ownership, CSRF, no secrets) · Forms validation · logging (after P3) · tests · readability · migrations · UI states · no unrelated changes · docs updated · PR base is correct.
7. **Understanding gate** (task PRs): 2 questions from the diff (what does it do / what if…). Grade kindly, fix gaps. Record in the journal's "Reviewer understanding-gate" (commit to the PR branch only if the operator agrees; else PR comment).
8. Ask for the decision; post `gh pr review <N> --approve|--request-changes --body "..."`. Don't push to the author's branch unless told.
9. `git switch` back to your task branch or the base. If approved → `/merge-pr <N>`.
