# Phase 2 — views, urls, templates, forms, test data

### P2-01 · Core helpers, decorators, error handling
- Owner: A
- Depends: P1-10
- Size: M
- Priority: must
- Status: DONE
- Goal: Shared building blocks used by every view.
- Deliverables:
  - `apps/core/http.py` (final), `decorators.py` (`login_required_json`, `role_required`), `forms.py` helper `form_errors(form)`.
  - JSON 404/500 handlers for `/api/` paths; CSRF endpoint `/api/auth/csrf/`.
- DoD:
  - [x] Unit tests for helpers/decorators (401/403/ok) pass.

### P2-02 · Auth: forms + views (register, login, logout, me)
- Owner: A
- Depends: P2-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Session authentication per API_CONTRACT.
- Deliverables:
  - `RegisterForm` (password confirmation, unique email/username, role guest|manager), `LoginForm` (username or email), views + urls.
- DoD:
  - [x] Register→login→me→logout works with curl/Postman using cookies + CSRF; wrong password gives 400 with field errors.

### P2-03 · Manager: hotel & room-type forms/views
- Owner: A
- Depends: P2-02
- Size: M
- Priority: must
- Status: DONE
- Goal: Managers CRUD their hotels and room types.
- Deliverables:
  - `HotelForm`, `RoomTypeForm` (amenities), `/api/manager/hotels/...`, `/api/manager/room-types/...`, `/api/amenities/`.
  - Ownership enforced (404 for others' objects).
- DoD:
  - [x] Manager A cannot read/edit Manager B's hotel (checked manually, test added).

### P2-04 · Manager: bookings, availability, discount codes
- Owner: A
- Depends: P2-03, P1-05
- Size: L
- Priority: must
- Status: DONE
- Goal: The remaining manager features of the spec.
- Deliverables:
  - `DiscountCodeForm` (valid dates, percent range, unique code per hotel) + CRUD endpoints.
  - Bookings list for own hotels (simple ORM; managers come in Phase 3).
  - Availability endpoint: for each room type and day → total, reserved, free.
- DoD:
  - [x] Availability numbers match hand-computed example with 3 overlapping bookings (in journal).

### P2-05 · Public hotel search & detail views
- Owner: B
- Depends: P2-01, P1-10
- Size: M
- Priority: must
- Status: DONE
- Goal: Guests can search by city, dates, capacity and see details.
- Deliverables:
  - `/api/cities/`, `/api/hotels/`, `/api/hotels/{id}/`, `/api/hotels/{id}/rooms/`, `/api/rooms/{id}/` with a `SearchForm` validating query params
    (check_in < check_out, not in the past, guests ≥ 1).
- DoD:
  - [x] Searching with dates excludes hotels with no room type available (verified with seed-like data).

### P2-06 · Booking: quote, discount validate, create, mine, cancel
- Owner: B
- Depends: P2-05, P2-02
- Size: L
- Priority: must
- Status: DONE
- Goal: Complete guest booking flow on the backend.
- Deliverables:
  - `BookingForm`, `quote`, `discounts/validate`, `bookings/`, `bookings/mine/`, `bookings/{id}/cancel/` with rules from DATA_MODEL.md
    (capacity, availability, discount validity, used_count, cancellation rule).
- DoD:
  - [x] Booking when full returns 409; cancelling frees the rooms; discount counter changes correctly (shown in shell).

### P2-07 · React: auth pages, AuthContext, route guards
- Owner: B
- Depends: P2-02
- Size: M
- Priority: must
- Status: DONE
- Goal: Users can register/login/logout in the UI.
- Deliverables:
  - Login/Register pages (field errors), `AuthContext`, `RequireAuth`, `RequireRole`, Navbar by role.
- DoD:
  - [x] Full register→login→logout in browser; refresh keeps session; guest cannot open /manager.

### P2-08 · React: guest pages
- Owner: B
- Depends: P2-05, P2-06, P2-07
- Size: L
- Priority: must
- Status: DONE
- Goal: Search → details → book → my bookings in the UI.
- Deliverables:
  - Home with search form (city select, dates, guests), hotel list, hotel detail with room types, room detail, booking form with discount code + price summary, My bookings with cancel.
- DoD:
  - [x] Whole guest story clickable; loading/error/empty states exist; responsive at 375px and desktop.

### P2-09 · React: manager pages
- Owner: A
- Depends: P2-03, P2-04, P2-07
- Size: L
- Priority: must
- Status: DONE
- Goal: Manager UI for all manager features.
- Deliverables:
  - My hotels (list/create/edit), room types (CRUD with amenities), bookings table, availability table (per room type/day), discount codes (CRUD).
- DoD:
  - [x] Whole manager story clickable; a manager sees only own data.

### P2-10 · Test data: `seed_demo` command + fixtures
- Owner: A
- Depends: P2-04
- Size: M
- Priority: must
- Status: DONE
- Goal: Course-required "test data entry".
- Deliverables:
  - `python manage.py seed_demo` (idempotent, `--reset` option): 2 managers, 5 guests, ≥ 6 hotels in ≥ 3 cities, 2–4 room types each, discounts, ~20 bookings (past, current, future, cancelled). Known demo passwords listed in README.
- DoD:
  - [x] Running twice doesn't duplicate; `--reset` rebuilds; demo accounts documented.

### P2-11 · SPA host template + production build served by Django
- Owner: B
- Depends: P2-07
- Size: M
- Priority: must
- Status: DONE
- Goal: One command builds the UI and Django serves it (this is our "template").
- Deliverables:
  - Vite output with fixed names (`assets/app.js`, `assets/app.css`); Django `templates/index.html` + catch-all view for non-`/api` paths; staticfiles config.
- DoD:
  - [x] `npm run build` + `runserver` on :8000 shows the app, deep link `/hotels/3` reloads fine.

### P2-12 · PHASE 2 GATE (joint)
- Owner: AB
- Depends: P2-08, P2-09, P2-10, P2-11
- Size: S
- Priority: must
- Status: TODO
- Goal: Deliver Phase 2.
- Flow: do `/phase-close 2` inside this task (on a task branch cut from `phase/2`), merge it into `phase/2`; on delivery day run `/phase-deliver 2` (PR `phase/2` → `main`, merge commit, tag `phase-2`).
- Deliverables:
  - Update API_CONTRACT.md to what exists; `/phase-close 2` (fresh DB → migrate → seed → demo script, DB dump, tag `phase-2`).
- DoD:
  - [ ] Each operator can demo the other's half end-to-end and explain the view → form → model path.

## Exit checklist (Phase 2)
- [ ] views/urls/forms for all spec features · templates (SPA host) · seed data · DB backup · tag.
