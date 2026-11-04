# 04 — Two-operator protocol (A and B)

## Who is who
`docs/TEAM.md` maps `git config user.email` → Operator A or B. Every workflow starts by identifying the operator
that way. If the e-mail is unknown → stop and ask.

## Ownership (reduces conflicts)
| Area | Owner |
|---|---|
| backend/apps/accounts, apps/hotels, apps/core, config/settings, logging infra | **A** |
| backend/apps/bookings, apps/reviews, search & booking flow | **B** |
| frontend/ shell, auth UI, guest pages | **B** |
| frontend/ manager pages (src/pages/manager) | **A** |
| docs: A → PROCESS/ARCHITECTURE parts of report ; B → DATA_MODEL ; both → PLAN, DECISIONS | split |
Editing the other owner's area is allowed ONLY if the task block says so, or after telling the partner. Prefer asking
them via PR comment.

## Every task has an author and a reviewer
- Author = task Owner (`Owner:` in the task block). Reviewer = the other operator.
- `Owner: AB` tasks (phase gates) are done together: both run the commands, both confirm.
- The reviewer uses `/review-pr`; the agent explains the change in Persian and asks 2 comprehension questions.
  This is how both operators know ALL commits — the professor will ask.

## Journal
- `docs/journal/<TASK-ID>.md` is written by the author in `/task-pr` (what/why/how/gotchas + 3–5 viva Q&A in Persian).
- Phase gates also produce a demo script (who shows what) — both must be able to present everything.

## Communication
- Decisions → `/decision`. Contract changes → `/pair-contract`. Blocking questions → `/blocker`.
- Chat messages are not memory: anything the other operator must know goes into a PR, journal or doc.

## Parallel work
- Before starting a task check `python scripts/board.py --next --me`; don't start a task whose dependencies aren't DONE.
- If you're idle (all yours are blocked): do `/review-pr` for the partner, `/viva-drill`, or docs/report parts.

## Phase branches
- Both operators work on the same stacked phase branches. Whoever merges a PR into `phase/N` is responsible for `/propagate` the same day.
- Delivery (`/phase-deliver`) is done together; both attend; the partner approves the delivery PR.
- Ownership map stays the same; the phase a task belongs to only decides its base branch.
