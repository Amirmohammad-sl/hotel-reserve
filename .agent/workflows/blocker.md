---
description: Handle a blocker: classify, propose options, optionally draft an email to the professor
---
# /blocker <description>
1. Classify (Persian): technical bug · unclear requirement · dependency on partner · environment/tooling · question for professor.
2. Technical: reproduce with the smallest case, show the real error, list 2–3 hypotheses ordered by likelihood, test the cheapest first. Don't change unrelated code. After 3 failed attempts, summarise what was tried and ask the operator.
3. Dependency on partner: identify the exact task/PR needed; draft a short message to the partner; propose what the operator can do meanwhile (`/next`, `/review-pr`, docs).
4. Professor question: draft a short polite Persian email (see docs/PROFESSOR_EMAIL.md style) with a clear numbered question.
5. Record non-trivial blockers in `docs/blockers/<YYYY-MM-DD>-<slug>.md` (what, options, outcome) — commit with the task's next PR.
