# Phase 4 — Email verification, tests, optimization, report, bonus

### P4-01 · Email verification (backend + UI)
- Owner: A
- Depends: P2-03, P2-06, P2-07
- Size: L
- Priority: must
- Status: DONE
- Goal: Users verify their e-mail with a link.
- Deliverables:
  - Signed token (48h) via `django.core.signing`; send on register; `/api/auth/verify-email/`, `/api/auth/resend-verification/`.
  - `@verified_required` on booking and hotel-creation endpoints (403 + clear message).
  - React: `/verify-email?token=...` page + banner with "resend" for unverified users (touches B's frontend area — allowed by this task).
- DoD:
  - [x] With console email backend: register → copy link from terminal → verified → can book; expired/invalid token handled.

### P4-02 · Email templates + booking confirmation email
- Owner: A
- Depends: P4-01
- Size: M
- Priority: bonus
- Status: TODO
- Goal: Proper Django email templates; confirmation mail on booking.
- Deliverables:
  - `templates/emails/base.html`, `verify_email.html/.txt`, `booking_confirmation.html/.txt` (multipart); send inside `transaction.on_commit`.
- DoD:
  - [ ] Booking creates a console email with correct dates/price; failure to send is logged and does not break booking.

### P4-03 · Tests: accounts, permissions, email verification
- Owner: A
- Depends: P4-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Project tests part 1.
- Deliverables:
  - Tests for register/login/logout/me, role decorators, ownership (404), verified_required, token expiry.
- DoD:
  - [x] `manage.py test` green; coverage of accounts+hotels ≥ 70%.

### P4-04 · Tests: managers, availability, booking, discounts
- Owner: B
- Depends: P3-02, P3-04, P3-05
- Size: L
- Priority: must
- Status: DONE
- Goal: Project tests part 2 (the business core).
- Deliverables:
  - Tests: overlap edge cases, same-day turnover, capacity, discount rules (expired, max uses, wrong hotel), cancel frees rooms, quote equals booking total, concurrency test if feasible.
- DoD:
  - [x] Green; coverage of bookings ≥ 80%.

### P4-05 · Tests: API integration + frontend smoke
- Owner: B
- Depends: P4-04
- Size: M
- Priority: must
- Status: DONE
- Goal: End-to-end confidence.
- Deliverables:
  - Django test-client flows (guest story, manager story); optional Vitest smoke test for `api/client.js` error normalisation (needs /decision if adding Vitest).
- DoD:
  - [x] CI green; flows documented in docs/report/testing.md.

### P4-06 · Query & template optimisation (backend)
- Owner: A
- Depends: P3-03, P3-04
- Size: M
- Priority: must
- Status: DONE
- Goal: Course-required optimisation.
- Deliverables:
  - `select_related/prefetch_related` on list endpoints; `assertNumQueries` tests; cached template loader in non-debug settings; email templates deduplicated via base template.
- DoD:
  - [x] Before/after query counts for hotel list and manager bookings in journal.

### P4-07 · Frontend optimisation + polish
- Owner: B
- Depends: P2-08, P2-09, P2-11
- Size: M
- Priority: must
- Status: DONE
- Goal: Fast, clean UI.
- Deliverables:
  - Route-level lazy loading, shared components cleanup, consistent loading/error/empty states, responsive pass, accessibility basics (labels, focus), 404 page.
- DoD:
  - [x] `npm run build` bundle size reported before/after; Lighthouse (or manual) check noted.

### P4-08 · Bonus: Django Permissions & role restrictions
- Owner: A
- Depends: P4-01
- Size: M
- Priority: bonus
- Status: TODO
- Goal: Use Django's permission system, not only role checks.
- Deliverables:
  - Groups `HotelManagers`, `Guests` + permissions assigned by data migration/signal; `permission_required`-style decorator; admin restricted accordingly.
- DoD:
  - [ ] Tests prove each role can/can't access each endpoint group.

### P4-09 · Bonus: Pagination
- Owner: B
- Depends: P3-03, P3-04
- Size: M
- Priority: bonus
- Status: TODO
- Goal: Paginated lists.
- Deliverables:
  - Django `Paginator` on hotels, my bookings, manager bookings; `Pagination` React component; contract updated.
- DoD:
  - [ ] 25 seeded hotels paginate; page persists in URL query.

### P4-10 · Bonus: Fetch/AJAX live price quote
- Owner: B
- Depends: P2-06, P2-08
- Size: S
- Priority: bonus
- Status: TODO
- Goal: At least one clearly AJAX feature.
- Deliverables:
  - Booking form updates price/availability live (debounced fetch to `/api/bookings/quote/`) without page reload; discount code check on blur.
- DoD:
  - [ ] Network tab demo; no request spam (debounce).

### P4-11 · Bonus: Dashboards per user type
- Owner: A
- Depends: P4-08
- Size: M
- Priority: bonus
- Status: TODO
- Goal: Dedicated dashboard for manager and guest.
- Deliverables:
  - `/api/manager/dashboard/` (counts, occupancy next 30 days, revenue, latest bookings) and `/api/guest/dashboard/` (upcoming trips, past, total spent); two React pages.
- DoD:
  - [ ] Numbers match seed data.

### P4-12 · Bonus: Reviews & ratings
- Owner: B
- Depends: P3-04
- Size: M
- Priority: bonus
- Status: TODO
- Goal: Guests rate hotels they stayed in.
- Deliverables:
  - Endpoints + form (only guests with a past confirmed booking, one review per hotel); average rating on hotel cards/detail.
- DoD:
  - [ ] Rule enforced in tests; average updates.

### P4-13 · Optional bonus: hotel on map
- Owner: A
- Depends: P4-06
- Size: M
- Priority: optional
- Status: TODO
- Goal: Map with react-leaflet.
- Deliverables:
  - Manager can set lat/lng; hotel detail shows map; (needs /decision for `leaflet`, `react-leaflet`).
- DoD:
  - [ ] Marker shown for seeded hotels.

### P4-14 · Optional bonus: room-status calendar
- Owner: B
- Depends: P4-09
- Size: M
- Priority: optional
- Status: TODO
- Goal: Month calendar of free/booked rooms (manager).
- Deliverables:
  - Uses the availability endpoint; simple custom grid component.
- DoD:
  - [ ] Colours match numbers from availability table.

### P4-15 · Optional bonus: hotel recommendations
- Owner: B
- Depends: P4-12
- Size: M
- Priority: optional
- Status: TODO
- Goal: Suggest hotels by user's favourite city & price range (from past bookings + cookie).
- Deliverables:
  - `GET /api/hotels/recommended/` + Home block.
- DoD:
  - [ ] Different users get different results (demo with seed users).

### P4-16 · Final report part 1 (diagrams, process per app, models)
- Owner: A
- Depends: P3-03, P3-04
- Size: L
- Priority: must
- Status: DONE
- Goal: Report sections 1, 2, 3.
- Deliverables:
  - `/report-section` outputs in docs/report/: overall diagram, per-app process explanation, models & relations — generated from real code, in Persian.
- DoD:
  - [x] B reads and can explain every paragraph; matches code.

### P4-17 · Final report part 2 (managers, views) + testing + bonus list
- Owner: B
- Depends: P3-03, P3-04
- Size: L
- Priority: must
- Status: TODO
- Goal: Report sections 4, 5 (+ tests, bonuses, how to run).
- Deliverables:
  - docs/report/managers.md (each manager + why), views.md (every view: URL, method, role, form, manager used), testing.md, bonuses.md.
- DoD:
  - [ ] A reads and can explain every paragraph; matches code.

### P4-18 · FINAL GATE (joint)
- Owner: AB
- Depends: P4-03, P4-05, P4-06, P4-07, P4-16, P4-17
- Size: M
- Priority: must
- Status: TODO
- Goal: Deliver the project.
- Flow: do `/phase-close 4` inside this task (on a task branch cut from `phase/4`), merge it into `phase/4`; on delivery day run `/phase-deliver 4` (PR `phase/4` → `main`, merge commit, tag `phase-4`).
- Deliverables:
  - Assemble the final report (Word/PDF from docs/report/*.md — use the docx/pdf tooling), final DB dump `final`, tag `final`, clean-clone test, 10-min demo script, `/viva-drill` full rounds (each operator ≥ 2 rounds).
- DoD:
  - [ ] Fresh clone + README commands work on both laptops; both pass the viva-drill with ≥ 80%.

## Exit checklist (Phase 4)
- [ ] Email verification · tests green · optimisation · report · bonuses chosen in D-009 · final backup · tag `final`.
