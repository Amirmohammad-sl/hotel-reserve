# DECISIONS (ADR log)
Add new ones with `/decision`. Status: PROPOSED | ACCEPTED | SUPERSEDED.

## D-001 — React SPA + Django JSON views (hybrid) — PROPOSED (alignment email sent on 2026-11-01: P0-06)
- Context: course asks for Django views/urls/templates/forms; we want React + Tailwind.
- Decision: Django owns routing/validation/auth (views, urls, Forms, sessions, managers). React is the UI.
  Django templates: SPA host page + all emails. Django admin for inspection.
- Status update (P0-06): Alignment email sent on 2026-11-01 to `nedasoltanih@gmail.com` (recorded in `docs/blockers/professor_alignment_email.md`).
  If no objection is raised by 2026-11-08 (7 days), proceed as accepted.
- Consequences: we must explain in the report how each Django concept is used. If the professor insists on
  server-rendered pages, **Plan B**: render the main pages with Django templates (+ Tailwind CDN/build) and keep React only for
  interactive widgets (search form, booking quote, calendar). Backend models/managers/forms remain unchanged.

## D-002 — Plain Django views + Forms, no DRF — ACCEPTED
- Reason: matches course vocabulary (views, forms), fewer concepts to explain, smaller surface for the AI to get wrong.

## D-003 — Session cookie auth + CSRF, no JWT — ACCEPTED
- Reason: course requires session & cookie management.

## D-004 — Money as integer Toman, night-based dates — ACCEPTED
- `price_per_night` PositiveBigIntegerField. `check_out` exclusive. Booking confirmed immediately (no payment).

## D-005 — UI language Persian + RTL — PROPOSED (change BEFORE P0-04 if you prefer English)
- Vazirmatn font, Tailwind logical utilities. API field names and code stay English.

## D-006 — Availability = quantity − overlapping confirmed bookings — ACCEPTED
- `RoomType` has `quantity`. No separate Room rows. For date range [in, out) availability =
  `quantity - SUM(rooms_count of CONFIRMED bookings overlapping)`; must be ≥ requested rooms for EVERY night of the stay.
- Overlap condition: `existing.check_in < new.check_out AND existing.check_out > new.check_in`.

## D-007 — Email verification via signed token — ACCEPTED
- `django.core.signing.TimestampSigner`/`dumps`, 48h expiry. Unverified users can log in but cannot book or create hotels.

## D-008 — Squash merge, merge-main-into-branch (no rebase), no force push — PARTIALLY SUPERSEDED by D-010 (merge methods)
- Reason: two beginners, linear `main`, one commit per task.

## D-009 — Bonus selection (priority) — ACCEPTED
1. Must-do bonuses (cheap, in course list): Permissions, Pagination, Fetch/AJAX, per-role dashboards.
2. Then hotel-specific: booking confirmation email, reviews & ratings.
3. Then optional: map, calendar, recommendations. SMS verification is skipped.

## D-010 — Phase-branch model (stacked long-lived branches) — ACCEPTED
- Context: we want to finish early but deliver each phase on its own deadline.
- Decision: `phase/2`, `phase/3`, `phase/4` are long-lived, stacked (each contains the previous). Task PRs squash into their phase branch;
  upstream→downstream "propagate" PRs and delivery PRs (`phase/N`→`main`) use MERGE COMMITS. `main` only receives deliveries. Tags `phase-N`.
- Consequences: daily `/propagate` discipline; dependencies are per-task (not "after the gate"); schema changes go to the earliest possible phase;
  GitHub: merge commits + squash enabled, auto-delete head branches OFF, branch protection on `main` and `phase/*`.
