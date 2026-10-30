---
description: Review the partner's PR: teach the change in Persian, run checks, understanding gate, then approve or request changes
---
# /review-pr <PR-NUMBER>
Goal: a real review AND make the reviewer able to explain the change to the professor.

1. Identify operator. `gh pr view <N> --json author,title,headRefName,body,files`. If the PR author is the same operator → refuse (need the partner).
2. `gh pr checkout <N>`. Read: PR body, `docs/journal/<ID>.md`, the task block (goal + DoD), then the diff: `git diff origin/main...HEAD --stat`, then file by file.
3. **Teach (Persian)**: explain the change as to a classmate: (a) the goal in one sentence, (b) the files and how they connect, (c) follow ONE request/click end-to-end through the code, (d) key Django/React concepts used and why, (e) what could break. Keep it concrete with short code excerpts.
4. Run the checks of `/verify` on this checkout (install deps / migrate a test DB if needed). Record results.
5. Review against checklist: matches DoD + contract · security (auth, ownership, CSRF, no secrets) · validation through Forms · logging (after P3) · tests · naming/readability · migrations sane · UI states (loading/error/empty) · no unrelated changes · docs updated.
6. **Understanding gate**: ask the reviewer operator 2 questions derived from the diff (one "what does this do", one "what happens if…/why not…"). Wait for answers, grade them kindly, correct gaps. Record questions and result in `docs/journal/<ID>.md` under "Reviewer understanding-gate" (commit to the PR branch ONLY if the operator agrees; otherwise paste into the PR comment).
7. Ask the operator for the decision: approve / request changes. Then post: `gh pr review <N> --approve --body "..."` or `--request-changes --body "..."` (specific, kind, actionable comments with file/line).
8. Don't push fixes to the author's branch unless the operator says so. Switch back: `git switch main`.
9. Next: if approved → `/merge-pr <N>`.
