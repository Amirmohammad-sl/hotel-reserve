---
description: Explain a file, function, commit, PR or concept in Persian so the operator can answer the professor
---
# /explain <path | path:line | commit-hash | PR-number | concept>
Read-only. Do not change files.
1. Resolve the target: file/function → open it; commit → `git show <hash>`; PR → `gh pr view` + diff; concept → locate where our project uses it.
2. Explain in Persian at three levels: **(1) one sentence** · **(2) step by step** (follow the data/flow; small code excerpts) · **(3) "what the professor may ask"**: 3 likely questions with short model answers (including "why this design / what are alternatives").
3. Connect to course terms: view, url, form, template, model, Manager, session, cookie, logging, migration, etc.
4. End by asking if they want a mini-quiz on it (`/viva-drill`).
