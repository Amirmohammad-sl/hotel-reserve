# ARCHITECTURE

```
Browser (React SPA, Tailwind) --fetch /api/*--> Django (views + Forms + managers) --ORM--> PostgreSQL
        ^                                           |
        | index.html (Django template, prod)        +--> sessions (DB), logging (files), emails (templates)
```
- Dev: `npm run dev` (5173) proxies `/api` to Django (8000). Prod-like: `npm run build` → Django serves `index.html` + assets.
- Auth: Django session cookie (HttpOnly) + CSRF cookie `csrftoken` echoed in `X-CSRFToken` header.

## Django apps (finalised in P1-01, refined later)
| App | Package | Owner | Responsibility & Boundaries | Key models | Mounted URLs |
|---|---|---|---|---|---|
| `core` | `apps.core` | A | Standardized JSON helpers (`json_ok`, `json_error`, `parse_json`), shared decorators, logging middleware, error handling, SPA host view. | – | `/api/health/` |
| `accounts` | `apps.accounts` | A | User identity, custom `User` model, role enforcement (Guest vs Manager), session-based authentication forms/views, email verification token logic. | `User` | `/api/auth/*` |
| `hotels` | `apps.hotels` | A | Hotel catalog, amenity tags, room types definitions; hotel manager CRUD operations; public search & catalog discovery endpoints. | `Hotel`, `Amenity`, `RoomType` | `/api/hotels/*`, `/api/cities/`, `/api/rooms/*`, `/api/manager/hotels/*`, `/api/amenities/` |
| `bookings` | `apps.bookings` | B | Reservation workflows, date availability calculation, discount codes validation & application, guest booking management, manager booking overviews. | `Booking`, `DiscountCode` | `/api/bookings/*`, `/api/discounts/*`, `/api/manager/hotels/{id}/bookings/`, `/api/manager/hotels/{id}/availability/` |
| `reviews` | `apps.reviews` | B | Hotel ratings, feedback text, user-hotel uniqueness constraints for reviews (bonus scope). | `Review` | `/api/hotels/{id}/reviews/` |

### App Dependency & Boundary Rules
1. **No Circular Imports**: `core` depends on nothing. `accounts` depends only on `core`. `hotels` depends on `core` and `accounts`. `bookings` depends on `core`, `accounts`, and `hotels` (referencing `RoomType`). `reviews` depends on `hotels` and `accounts`.
2. **Data Integrity**: Cross-app mutations (e.g., creating a booking while validating room availability) occur via manager methods within atomic transactions (`transaction.atomic`).
3. **Response Envelope**: All JSON endpoints across apps must conform to standard envelope formats (`{"data": ...}` on success, `{"message": "...", "errors": {...}}` on failure) via `apps.core.http`.

## Request lifecycle example (guest books a room)
1. React `BookingForm` → `POST /api/bookings/` with JSON + CSRF header.
2. `core.middleware.RequestLogMiddleware` logs request → `SessionMiddleware` loads session → view.
3. `bookings.views.CreateBookingView` → `BookingForm.is_valid()` → availability check via managers → `transaction.atomic` create.
4. JSON `{data: {...}}` back → React updates UI; email sent (P4-02).

(Update this file whenever structure changes. It feeds report sections 1–2.)
