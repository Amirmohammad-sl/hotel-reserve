# 02 — Backend (Django) conventions

## Structure
- Project package `backend/config/`. Apps in `backend/apps/<name>/` with `AppConfig.name = "apps.<name>"`.
- Settings read from environment (`django-environ`, file `backend/.env`). Never hardcode secrets.
- `AUTH_USER_MODEL = "accounts.User"` is set BEFORE the first `migrate` (P0-03). Never change it later.
- Database: PostgreSQL only. Money = integer Toman (`PositiveBigIntegerField`). Dates = `DateField`; stay is
  **night-based**: `check_out` is exclusive; nights = `(check_out - check_in).days` ≥ 1.

## Views (no DRF)
- Every API view returns JSON via helpers in `apps/core/http.py`:
  `json_ok(data, status=200, **extra)` → `{"data": ...}` ;  `json_error(message, errors=None, status=400)` → `{"message":..., "errors": {...}}`.
- Read JSON body with `parse_json(request)` (returns dict; invalid JSON → 400).
- Validate EVERY input with a Django Form (`forms.Form` / `ModelForm`). Convert `form.errors` to `{field: [messages]}`.
- Use class-based views (`View` with `get/post/put/delete`) or function views with `@require_http_methods`.
- Access control through decorators in `apps/core/decorators.py`: `@login_required_json`, `@role_required("manager")`,
  `@verified_required` (P4-01). Managers may only touch THEIR hotels → filter by `owner=request.user`, return 404 (not 403) for others' objects.
- Status codes: 200/201 ok · 400 validation · 401 not logged in · 403 wrong role/unverified · 404 · 409 conflict (no availability).
- Never put business rules in views if a manager/queryset/service function can hold them (from Phase 3).

## Models
- Always: `__str__`, `Meta.ordering`, `verbose_name`, explicit `related_name`, deliberate `on_delete`.
- Add DB constraints for invariants (`CheckConstraint`, `UniqueConstraint`) and indexes for search fields (city, dates).
- Owner of each app edits its models (see 04). Other operator proposes changes via PR/`/pair-contract`.

## Managers / QuerySets (Phase 3)
- Custom `QuerySet` classes with `as_manager()` or `Manager.from_queryset()`. Chainable methods with docstrings
  explaining WHY (the report needs the reason for every manager).
- Required set: `UserManager`, `HotelQuerySet`, `RoomTypeQuerySet.with_availability()`, `BookingQuerySet`, `DiscountCodeManager`.

## Sessions & cookies (Phase 3)
- DB sessions; `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`, `CSRF_COOKIE_SAMESITE="Lax"`;
  secure flags on when `DEBUG=False`. "Remember me" controls expiry. Custom cookie `last_city` (preferences).

## Logging (Phase 3, mandatory afterwards)
- Each module: `logger = logging.getLogger(__name__)`. Levels: DEBUG details · INFO business events
  (login, booking created/cancelled, discount used, hotel created) · WARNING suspicious (failed login, forbidden access, invalid discount) · ERROR exceptions.
- Files in `backend/logs/` (rotating) + console. Never log secrets/PII beyond user id.

## Tests (Phase 4, but write tests earlier when cheap)
- `apps/<name>/tests/test_*.py`, helper builders in `apps/core/tests/helpers.py`.
- Test: availability edge cases (same-day turnover, overlap), discount rules, permissions, validation errors, email verification.
- Use `assertNumQueries` on list endpoints after optimization (P4-06).

## Email (Phase 4)
- Email verification link = `django.core.signing` signed token (no extra model). Emails rendered from Django templates
  (`templates/emails/*.html` + `.txt`). Dev backend = console.
