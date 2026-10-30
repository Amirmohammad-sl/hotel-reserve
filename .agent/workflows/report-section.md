---
description: Generate a final-report section from the real code (Persian), verified against the repo
---
# /report-section <overall-diagram | process-per-app | models | managers | views | testing | bonuses>
Course report needs: process diagram · process explanation per web app · models & relations · Managers and why · Views.
1. Gather facts from code, not memory: models → read `models.py` of each app; managers → `managers.py`/`querysets` + docstrings; views → each app's `views.py` and `urls.py`; diagrams → docs/PROCESS_DIAGRAMS.md.
2. Write `docs/report/<section>.md` in clear Persian (technical terms in English):
   - models: per model purpose, fields table, relations with type (FK/M2M), `on_delete` reason, constraints.
   - managers: per manager/queryset method → what, why it was defined, where used.
   - views: table: URL · method · role · Form used · Manager used · response · short description.
   - process-per-app: for each Django app, step-by-step flows for each user type.
3. Every statement must be checkable in code. List anything you couldn't verify under "Needs check".
4. The OTHER operator proofreads (this is a normal PR through `/task-pr`).
