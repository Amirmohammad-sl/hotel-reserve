# Phase 3 — Managers, sessions & cookies, logging everywhere

### P3-01 · Managers: UserManager, HotelQuerySet
- Owner: A
- Depends: P1-10
- Size: M
- Priority: must
- Status: DONE
- Goal: Reusable, documented query logic for users and hotels.
- Deliverables:
  - `UserManager` (`create_user/create_superuser` with role rules, `.managers()`, `.guests()`).
  - `HotelQuerySet`: `.active()`, `.in_city(city)`, `.owned_by(user)`, `.with_min_price()`, `.priced_between(min,max)`.
  - Docstring per method: WHY it exists (report section 4).
- DoD:
  - [x] Shell demo of each method in journal; manage.py check OK.

### P3-02 · Managers: BookingQuerySet, DiscountCodeManager, room availability
- Owner: B
- Depends: P1-10
- Size: L
- Priority: must
- Status: DONE
- Goal: Move availability/overlap/discount logic out of views.
- Deliverables:
  - `BookingQuerySet`: `.active()`, `.overlapping(check_in, check_out)`, `.for_hotel(hotel)`, `.for_guest(user)`.
  - `DiscountCodeManager`: `.valid_now(hotel)`, `.get_valid(hotel, code)`.
  - `RoomTypeQuerySet.with_availability(check_in, check_out)` annotating `reserved` and `available_count` (touches apps/hotels — allowed by this task).
- DoD:
  - [x] Same-day turnover (out on 5th, in on 5th) is available; overlap cases demonstrated in shell.

### P3-03 · Refactor manager-side views to use managers
- Owner: A
- Depends: P3-01, P3-02, P2-03, P2-04
- Size: M
- Priority: must
- Status: DONE
- Goal: Views become thin.
- Deliverables:
  - accounts/hotels/manager views call manager methods; no duplicated ORM filters.
- DoD:
  - [x] Behaviour unchanged (manual smoke list in PR); fewer lines in views.

### P3-04 · Refactor guest-side views to use managers
- Owner: B
- Depends: P3-01, P3-02, P2-05, P2-06
- Size: M
- Priority: must
- Status: DONE
- Goal: Search/booking views use managers.
- Deliverables:
  - search, rooms, quote, create-booking use `with_availability`, `valid_now`, etc.
- DoD:
  - [x] Behaviour unchanged; smoke list passes.

### P3-05 · Concurrency-safe booking
- Owner: B
- Depends: P3-04
- Size: M
- Priority: must
- Status: TODO
- Goal: Two guests can't overbook the last room.
- Deliverables:
  - `transaction.atomic()` + `select_for_update()` on the RoomType row while checking availability and creating the booking; `used_count` update in same transaction (use `F()`).
- DoD:
  - [ ] Test with two threads/`TransactionTestCase` or documented manual test; explanation in journal.

### P3-06 · Session management
- Owner: A
- Depends: P2-02
- Size: M
- Priority: must
- Status: TODO
- Goal: Course-required session management.
- Deliverables:
  - DB sessions, cookie flags (HttpOnly, SameSite, Secure when not DEBUG), session age; "remember me" (short vs 14 days); logout flushes session; `clearsessions` mention in README.
  - Show "last login time" stored in session on `/api/auth/me/`.
- DoD:
  - [ ] Browser devtools screenshot shows flags; remember-me changes cookie expiry.

### P3-07 · Cookies: last search & recently viewed hotels
- Owner: B
- Depends: P2-05, P2-08
- Size: M
- Priority: must
- Status: DONE
- Goal: Course-required cookie usage with a real feature.
- Deliverables:
  - Cookie `last_city` (set on search; pre-fills search form). Session list of recently viewed hotel ids → `GET /api/hotels/recent/` → block on Home.
- DoD:
  - [x] Works across refreshes; cookie visible in devtools; documented in API_CONTRACT.

### P3-08 · Logging infrastructure
- Owner: A
- Depends: P2-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Central logging config.
- Deliverables:
  - `LOGGING` dict (console + rotating files `logs/app.log`, `logs/error.log`, `logs/security.log`), formatter with time/level/module, `LOG_LEVEL` env.
  - `RequestLogMiddleware` (method, path, status, user id, duration ms).
- DoD:
  - [x] Running a request writes expected lines; logs dir git-ignored.

### P3-09 · Logging coverage: core, accounts, hotels
- Owner: A
- Depends: P3-03, P3-08
- Size: M
- Priority: must
- Status: TODO
- Goal: "Logging in all parts of the project" for A's apps.
- Deliverables:
  - Logger per module; events: register/login success/fail/logout, hotel/room/discount CRUD, forbidden access, form validation failures (WARNING/INFO), unexpected exceptions (ERROR with traceback).
- DoD:
  - [ ] Checklist table (event → file:line → level) in journal; grep shows every view module has a logger.

### P3-10 · Logging coverage: bookings, reviews, managers
- Owner: B
- Depends: P3-04, P3-05, P3-08
- Size: M
- Priority: must
- Status: TODO
- Goal: Same for B's apps.
- Deliverables:
  - Events: quote, booking created/cancelled/conflict, discount applied/rejected, search (DEBUG), manager methods where useful.
- DoD:
  - [ ] Checklist table in journal; no secrets logged.

### P3-11 · PHASE 3 GATE (joint)
- Owner: AB
- Depends: P3-03, P3-06, P3-07, P3-09, P3-10
- Size: S
- Priority: must
- Status: TODO
- Goal: Deliver Phase 3.
- Flow: do `/phase-close 3` inside this task (on a task branch cut from `phase/3`), merge it into `phase/3`; on delivery day run `/phase-deliver 3` (PR `phase/3` → `main`, merge commit, tag `phase-3`).
- Deliverables:
  - `/phase-close 3` (fresh DB → seed → demo → dump → tag `phase-3`). Managers list with reasons drafted in docs/report/managers.md.
- DoD:
  - [ ] Both can explain every manager, the session/cookie flow, and show logs for a booking.

## Exit checklist (Phase 3)
- [ ] Managers + reasons · sessions · cookies · logging in every app · DB backup · tag.
