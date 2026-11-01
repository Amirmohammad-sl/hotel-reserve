# Phase 1 — Define web apps, design processes, design & define models

### P1-01 · Create Django apps and document responsibilities
- Owner: A
- Depends: P0-03
- Size: S
- Priority: must
- Status: TODO
- Goal: All apps exist and are registered.
- Deliverables:
  - Apps `hotels`, `bookings`, `reviews` in `backend/apps/` (core/accounts exist). Registered in `INSTALLED_APPS`; each with urls.py stub included under `/api/`.
  - docs/ARCHITECTURE.md app table finalised.
- DoD:
  - [ ] `manage.py check` OK; each app has `apps.py` with `name = "apps.<name>"`.

### P1-02 · Process diagrams (overall + per app)
- Owner: B
- Depends: P0-01
- Size: M
- Priority: must
- Status: DONE
- Goal: Course-required diagrams ready for the report.
- Deliverables:
  - docs/PROCESS_DIAGRAMS.md: overall flow, per-app flows (accounts, hotels, bookings, reviews), sequence diagram for "guest books a room", manager "see booked/free rooms".
  - Short Persian explanation under each diagram (what happens, who triggers it).
  - Exported PNG/SVG in docs/report/diagrams/ (use mermaid-cli or the Mermaid live editor).
- DoD:
  - [x] Diagrams render on GitHub; each requirement bullet of the hotel project appears in at least one diagram.
  - [ ] A reviews and confirms flows match what he/she will build.

### P1-03 · User model fields and manager skeleton
- Owner: A
- Depends: P1-01
- Size: S
- Priority: must
- Status: TODO
- Goal: Final `accounts.User` per docs/DATA_MODEL.md.
- Deliverables:
  - Fields `role`, `phone`, `email` (unique, required), `email_verified`; role choices constants; migration.
- DoD:
  - [ ] `makemigrations --check` clean; migration applies; admin can create manager & guest users (admin registered in P1-07).

### P1-04 · Hotel, Amenity, RoomType models
- Owner: A
- Depends: P1-03
- Size: M
- Priority: must
- Status: TODO
- Goal: Hotel-side models with constraints and indexes.
- Deliverables:
  - Models per docs/DATA_MODEL.md (+ migration). `__str__`, ordering, `related_name`, unique (hotel, title), index on `Hotel.city`.
- DoD:
  - [ ] Migration applies on PostgreSQL; shell session creating hotel + room types works (paste in journal).

### P1-05 · Booking and DiscountCode models
- Owner: B
- Depends: P1-04
- Size: M
- Priority: must
- Status: TODO
- Goal: Booking-side models with DB-level invariants.
- Deliverables:
  - Models per DATA_MODEL.md with `CheckConstraint(check_out > check_in)`, percent 1–100, indexes (room_type, check_in, check_out).
  - Model-level helper `Booking.calculate_nights()` (pure function, no query).
- DoD:
  - [ ] Constraint violations raise IntegrityError (shown in shell); migration applies.

### P1-06 · Review model (bonus-ready)
- Owner: B
- Depends: P1-04
- Size: S
- Priority: bonus
- Status: TODO
- Goal: `reviews.Review` exists so later bonus doesn't change the schema.
- Deliverables:
  - Model + unique (hotel, user) + rating validators + migration.
- DoD:
  - [ ] Applies cleanly; documented in DATA_MODEL.md.

### P1-07 · Django admin for all models
- Owner: A
- Depends: P1-05
- Size: S
- Priority: must
- Status: TODO
- Goal: Admin usable for inspecting/entering data (also helps the demo).
- Deliverables:
  - ModelAdmin with list_display, search_fields, list_filter for every model; inlines for RoomType in Hotel.
- DoD:
  - [ ] Superuser created; all models visible and editable.

### P1-08 · Finalise DATA_MODEL.md and ER diagram
- Owner: B
- Depends: P1-06, P1-07
- Size: S
- Priority: must
- Status: TODO
- Goal: Documentation exactly equals the code (needed for report section 3).
- Deliverables:
  - DATA_MODEL.md updated from real models (fields, relations, on_delete reasons); ER diagram exported.
  - Persian paragraph explaining each relationship and why that `on_delete` was chosen.
- DoD:
  - [ ] A checks docs against `models.py` and approves; mismatches fixed.

### P1-09 · Database backup scripts + first dump
- Owner: A
- Depends: P1-07
- Size: S
- Priority: must
- Status: TODO
- Goal: Course-required DB backup in the repo.
- Deliverables:
  - Run `scripts/backup_db.sh phase1` → `db_backup/hotel_db_phase1.sql`; verify restore into an empty DB with `scripts/restore_db.sh`.
- DoD:
  - [ ] Restore test succeeded (output pasted in journal).

### P1-10 · PHASE 1 GATE (joint)
- Owner: AB
- Depends: P1-02, P1-08, P1-09
- Size: S
- Priority: must
- Status: TODO
- Goal: Deliver Phase 1.
- Deliverables:
  - `/phase-close 1`: clean-clone test, tag `phase-1`, demo script, repo link e-mail sent ONE DAY BEFORE the deadline (calendar!).
- DoD:
  - [ ] Both can explain every model, relation, and diagram without looking.

## Exit checklist (Phase 1)
- [ ] Apps defined · diagrams done · models + migrations + admin · DB backup committed · tag `phase-1` · link e-mailed.
