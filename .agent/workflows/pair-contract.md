---
description: Change the API contract or data model with both operators agreeing BEFORE anyone implements
---
# /pair-contract <what needs to change>
Use whenever an endpoint, field, model, or business rule must differ from docs/API_CONTRACT.md or docs/DATA_MODEL.md.
1. Write in Persian the problem: which task needs it and why the current contract doesn't fit. Check who else is affected (frontend ↔ backend, A's app ↔ B's app).
2. Draft the minimal edit to API_CONTRACT.md / DATA_MODEL.md (diff form). Include request/response examples and migration impact.
3. Branch `docs/contract-<slug>`, commit, push, open PR labelled `contract-change` with the affected task IDs; reviewer = partner. Nobody implements the new shape until it is merged.
4. After merge: affected operators run `/sync`; tasks that depended on the old shape are updated if needed (edit their DoD in the same PR).
