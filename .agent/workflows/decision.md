---
description: Record an architecture/tooling decision (ADR) via a small docs PR the partner approves
---
# /decision <short title>
1. Discuss options with the operator in Persian: context, options (≥2), recommendation, consequences. Check conflicts with AGENTS.md hard rules and existing decisions in docs/DECISIONS.md.
2. Branch `docs/decision-<NNN>-<slug>`; append `## D-<NNN> — <title> — PROPOSED` using the existing format; if it supersedes another, mark that one SUPERSEDED.
3. Commit `docs(decisions): D-<NNN> <title>`, push, open PR with label `decision`, reviewer = partner. A decision becomes ACCEPTED only after the partner approves the PR (change status in the same PR).
4. If the decision adds a dependency, list the exact package and version policy in the decision text. Implementation happens in a normal task afterward.
