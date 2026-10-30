# 05 — Agent guardrails (the model is fast; keep it on rails)

1. One task per conversation. When the task is finished or the conversation gets long (> ~30 tool calls or the agent
   starts forgetting), the operator opens a NEW conversation and runs `/task-start <ID>` again — state lives in git + docs, not in chat.
2. Plan first, wait for approval, then code. Prefer Planning mode over Fast mode for tasks Size M/L.
3. Read before write: open the file you modify. Search with grep for existing helpers before creating new ones
   (`apps/core/http.py`, `decorators.py`).
4. Keep diffs small. If a task grows beyond its DoD, stop and propose splitting it.
5. After every code change run the narrowest check (`manage.py check`, one test module, `npm run lint`) and show the output.
6. Terminal safety: never run destructive commands (`rm -rf`, `DROP DATABASE`, `git reset --hard`, `git clean`, force push) without
   the operator typing explicit confirmation in chat. Prefer creating a fresh test DB over wiping the dev DB.
7. No guessing about libraries: when installing/using Tailwind/Vite/Django features, read the official docs page first
   (use web search/browser) because versions change.
8. Honesty: report failing tests/errors as they are. "I could not run X because Y" is acceptable; "should work" is not.
9. Teaching duty: whenever the operator asks "why", answer in Persian with a small example. The operators must be able to
   explain everything to the professor — prefer clear simple code over clever code.
10. Don't refactor unrelated code, don't rename public things, don't reformat whole files.
