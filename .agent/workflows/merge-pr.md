---
description: Merge an approved PR (squash), update local main and see what became unblocked
---
# /merge-pr <PR-NUMBER>
Normally run by the REVIEWER after approving.
// turbo
1. `gh pr view <N> --json state,reviewDecision,mergeable,statusCheckRollup,author` and `gh pr checks <N>`.
2. Preconditions (stop and explain if not): approved by the other operator · checks green · mergeable · task block says `Status: DONE` · journal exists. Never merge your own PR without the partner's approval.
3. `gh pr merge <N> --squash --delete-branch --subject "[<ID>] <title> (#<N>)"`.
4. `git switch main && git pull --ff-only`. Delete the local branch.
// turbo
5. `python scripts/board.py --next --me` and `python scripts/board.py --summary`; tell both operators (Persian) which tasks became READY and for whom. Mention if install/migrate is needed (see `/sync` step 6).
6. If the merged task ends a phase's last task → suggest `/phase-close <N>`.
