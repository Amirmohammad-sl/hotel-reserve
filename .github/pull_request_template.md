## Task
`[TASK-ID]` — title

## What & why
<!-- 2-4 sentences -->

## How to test (reviewer: do this)
1.
2.

## Screenshots / output
<!-- UI screenshot or terminal output of /verify -->

## Checklist
- [ ] Matches task DoD and docs/API_CONTRACT.md / docs/DATA_MODEL.md
- [ ] `/verify` passed (check, makemigrations --check, tests, lint, build)
- [ ] Logging added where behaviour changed
- [ ] Docs updated (if contract/model changed)
- [ ] `docs/journal/<TASK-ID>.md` written
- [ ] Task `Status: DONE` set in docs/tasks/phase-N.md
- [ ] Author can explain every changed file; reviewer will be asked to as well
- [ ] PR base is the task's phase branch (phase/N), not main (propagate PRs: merge commit; task PRs: squash)
