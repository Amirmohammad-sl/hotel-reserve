---
description: Run all checks for the current task and walk the DoD with evidence
---
# /verify
Never claim a pass without real output. Report each item as PASS / FAIL / NOT-RUN with the evidence.

1. Identify the task from the branch name; load its DoD: `python scripts/board.py --task <ID>`.
2. Backend (if `backend/manage.py` exists), from `backend/`:
   - `python manage.py check`
   - `python manage.py makemigrations --check --dry-run`
   - `python manage.py test` (all tests; if slow, run the touched app first then all)
3. Frontend (if `frontend/package.json` exists), from `frontend/`: `npm run lint --if-present`, `npm run build`.
4. Contract check: every endpoint/field touched matches docs/API_CONTRACT.md and docs/DATA_MODEL.md (diff mentally and list mismatches). Mismatch → fix code, or STOP for `/pair-contract`.
5. After Phase 3: confirm each touched view/module has `logger = logging.getLogger(__name__)` and logs the events listed in the task.
6. Manual smoke: give the operator a short Persian click/curl script for the task and ask them to run it (or run it yourself with curl/the browser tool if available), then record the result.
7. Walk the DoD checkboxes one by one with evidence. Finish with a table: item → status → evidence. If anything is FAIL, fix and re-run; don't proceed to `/task-pr`.
