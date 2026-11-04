---
description: Merge an approved PR with the correct method for its type (squash for tasks, merge-commit for propagate/delivery)
---
# /merge-pr <PR-NUMBER>
Normally run by the REVIEWER after approving.
// turbo
1. `gh pr view <N> --json state,reviewDecision,mergeable,statusCheckRollup,author,headRefName,baseRefName` and `gh pr checks <N>`.
2. Preconditions (else stop and explain): approved by the OTHER operator · checks green · mergeable · (task PR) task block `Status: DONE` + journal exists. Never merge your own PR without partner approval.
3. Choose method by type:
   - Task PR (base `phase/N`): `gh pr merge <N> --squash --delete-branch --subject "[<ID>] <title> (#<N>)"`.
   - Propagate PR (head `chore/propagate-*`): `gh pr merge <N> --merge` (NO squash, keep branch deletion for the chore branch only).
   - Delivery PR (head `phase/N`, base `main`): `gh pr merge <N> --merge` and **never** `--delete-branch`. Then continue with `/phase-deliver` step "tag".
4. `git switch <BASE>` and `git pull --ff-only`; delete the old local task branch.
// turbo
5. `python scripts/board.py --next --me`, `--summary`; tell both operators (Persian) what became READY/UPSTREAM.
6. If a task PR merged into `phase/N` and `phase/N+1` (or later) exists → remind: run `/propagate` today (stack must not drift).
7. Last task of a phase merged → suggest `/phase-close N`.
