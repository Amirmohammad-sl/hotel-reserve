# 00 — Course requirements (professor's rubric, mapped to our design)

These come from the course PDF. Every task must keep them satisfiable. When in doubt, ask the operator.

## General
- Individual or pairs; in pairs BOTH must attend and contribute to every phase delivery.
- Code + **PostgreSQL backup** on GitHub; final code of each phase pushed BEFORE the phase deadline.
- Repo link emailed ONE DAY BEFORE the Phase 1 deadline.
- PostgreSQL is mandatory. No bank gateway is needed.
- Final report must contain: (1) process diagram, (2) process explanation per web app, (3) models and their
  relations, (4) Managers and why each was defined, (5) the Views we defined.

## Phases
| Phase | Must deliver |
|---|---|
| 1 | Define web apps (Django apps), design processes (diagrams), design & define models |
| 2 | views, urls, templates, forms, test data |
| 3 | Managers, session management + cookies, logging in ALL parts of the project |
| 4 | Email verification, project tests, template optimization, report, finishing earlier phases, bonus items |

## Hotel project functional scope
**Hotel manager**: sign up/login · define hotel · define room types (title, capacity, price, amenities, count) ·
see made bookings · see booked & free rooms · define discount codes.
**Guest**: sign up/login · view hotels & rooms · search rooms by city, check-in/out dates, capacity ·
room details · book a room · use a discount code.
**Bonus (course list)**: hotel on map · room status in calendar · booking confirmation email/SMS ·
rating & review · hotel recommendation by city & price range · SMS verification · Permissions ·
Pagination · Fetch/AJAX in ≥1 feature · dedicated dashboard per user type.

## How we satisfy "Django" expectations with a React frontend
(See docs/DECISIONS.md D-001 — awaiting professor confirmation, task P0-06.)
- **views + urls**: real Django views/urls (JSON responses) — we explain each one in the report.
- **forms**: every write endpoint validates input with a Django `Form`/`ModelForm` (never trust raw JSON).
- **templates**: Django templates host the SPA (`index.html`) and render all emails (HTML + text);
  Django admin is also used for data inspection.
- **session + cookie**: Django sessions (DB-backed) + at least one custom cookie (P3-07).
- **Managers**: custom Manager/QuerySet classes for search, availability, validity (P3-01/02).
- **logging**: `LOGGING` config + middleware + per-module loggers (P3-08..10).
