# ARCHITECTURE

```
Browser (React SPA, Tailwind) --fetch /api/*--> Django (views + Forms + managers) --ORM--> PostgreSQL
        ^                                           |
        | index.html (Django template, prod)        +--> sessions (DB), logging (files), emails (templates)
```
- Dev: `npm run dev` (5173) proxies `/api` to Django (8000). Prod-like: `npm run build` → Django serves `index.html` + assets.
- Auth: Django session cookie (HttpOnly) + CSRF cookie `csrftoken` echoed in `X-CSRFToken` header.

## Django apps (filled in P1-01, refined later)
| App | Responsibility | Key models |
|---|---|---|
| core | JSON helpers, decorators, middleware (request logging), shared utils, SPA host view | – |
| accounts | users, roles, auth views, email verification | User |
| hotels | hotels, amenities, room types; manager CRUD; public search/detail | Hotel, Amenity, RoomType |
| bookings | booking flow, availability, discounts, manager booking views | Booking, DiscountCode |
| reviews | ratings & comments (bonus) | Review |

## Request lifecycle example (guest books a room)
1. React `BookingForm` → `POST /api/bookings/` with JSON + CSRF header.
2. `core.middleware.RequestLogMiddleware` logs request → `SessionMiddleware` loads session → view.
3. `bookings.views.CreateBookingView` → `BookingForm.is_valid()` → availability check via managers → `transaction.atomic` create.
4. JSON `{data: {...}}` back → React updates UI; email sent (P4-02).

(Update this file whenever structure changes. It feeds report sections 1–2.)
