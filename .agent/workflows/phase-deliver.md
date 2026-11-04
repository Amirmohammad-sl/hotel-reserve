---
description: Delivery day: merge phase/N into main with a merge commit, tag it, and prepare the presentation
---
# /phase-deliver <N>
Run together, on delivery day (or the day before). The only way code reaches `main`.
// turbo
1. `git fetch --all --prune --tags`.
2. Preconditions (stop and explain if any fails):
   - Gate task of phase N is DONE on `origin/phase/<N>` (`python scripts/board.py --task <gate-ID>`), `docs/demo/phase-<N>.md` and `db_backup/hotel_db_phase<N>.sql` exist there.
   - Previous phase delivered: tag `phase-<N-1>` exists and `git merge-base --is-ancestor origin/phase/<N-1> origin/main` is true (phase 2: phase 1 tag exists).
   - `origin/main` contains nothing that `phase/<N>` lacks: `git rev-list --count origin/phase/<N>..origin/main` must be 0 (or only previous delivery merge commits). If main is ahead → `/propagate` first.
   - No open task PRs with base `phase/<N>`; CI green on `phase/<N>`.
3. Show the operators (Persian) exactly what will land on main: `git log --oneline --no-merges origin/main..origin/phase/<N> | wc -l` and `git diff --stat origin/main...origin/phase/<N> | tail -5`.
4. Open the delivery PR: `gh pr create --base main --head phase/<N> --title "Deliver phase <N>" --body "<tasks list, demo script link, DB dump, what's NOT included>" --reviewer <partner>`.
5. Partner approves via `/review-pr` (delivery checklist), then `/merge-pr <PR>` → **merge commit, keep the branch**.
6. Tag: `git fetch && git switch main && git pull --ff-only && git tag -a phase-<N> -m "Phase <N> delivery" && git push origin phase-<N>` (final phase: tag `final`). Confirm on GitHub: main tip == tag, tests/CI green.
7. Optionally send/prepare the submission message with repo link and tag (Phase 1 rule: link one day before the deadline).
8. Presentation prep: print `docs/demo/phase-<N>.md`; run `/viva-drill phase <N>` for both; rehearse the demo from tag `phase-<N>` + dump, NOT from the dev DB.
9. Afterwards: `/propagate` (main → phase/2 → … ) so downstream branches include the delivery merge commit.
