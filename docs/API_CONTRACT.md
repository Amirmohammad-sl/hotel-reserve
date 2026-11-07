# API CONTRACT (draft v0 — change only via /pair-contract)

Conventions: JSON; base `/api/`; session cookie + `X-CSRFToken` on POST/PUT/DELETE; dates `YYYY-MM-DD`.
Success `{"data": ...}` · Error `{"message": "...", "errors": {"field": ["msg"]}}`.
Lists accept `?page=&page_size=` after P4-09 and return `pagination`. Roles: P=public, G=guest, M=manager, A=any logged-in.

## Auth (owner A)
| Method | Path | Role | Body / Query | Returns |
|---|---|---|---|---|
| GET | /api/auth/csrf/ | P | – | sets csrftoken cookie |
| POST | /api/auth/register/ | P | username,email,password,password2,role(guest/manager),phone? | user |
| POST | /api/auth/login/ | P | username_or_email,password,remember_me? | user |
| POST | /api/auth/logout/ | A | – | – |
| GET | /api/auth/me/ | P | – | user or `{"data": null}` |
| POST | /api/auth/verify-email/ | P | token | user |
| POST | /api/auth/resend-verification/ | A | – | – |
`user` = `{id, username, email, role, email_verified}`

## Public / guest browsing (owner B; models by A)
| Method | Path | Role | Notes |
|---|---|---|---|
| GET | /api/cities/ | P | distinct cities of active hotels |
| GET | /api/hotels/ | P | filters: city, check_in, check_out, guests, min_price, max_price, q; returns hotels with `min_price`, `available` flag when dates given; sets `last_city` cookie |
| GET | /api/hotels/recent/ | P | returns recently viewed active hotels from session in viewing order (with `min_price`) |
| GET | /api/hotels/{id}/ | P | hotel + room types (records hotel id in session recent list) |
| GET | /api/hotels/{id}/rooms/ | P | room types with `available_count` for `check_in`,`check_out`,`guests` |
| GET | /api/rooms/{id}/ | P | room type detail (+ hotel summary, amenities) |

## Booking (owner B)
| Method | Path | Role | Body | Returns |
|---|---|---|---|---|
| POST | /api/bookings/quote/ | G | room_type,check_in,check_out,rooms_count,guests_count,discount_code? | `{nights, subtotal, discount_amount, total_price, available}` |
| POST | /api/discounts/validate/ | G | hotel,code | `{valid, percent, message}` |
| POST | /api/bookings/ | G (verified after P4-01) | same as quote | booking (201) · 409 if not available |
| GET | /api/bookings/mine/ | G | – | list |
| POST | /api/bookings/{id}/cancel/ | G | – | booking |

## Manager (owner A; bookings/availability views read bookings models of B)
| Method | Path | Notes |
|---|---|---|
| GET/POST | /api/manager/hotels/ | list own / create |
| GET/PUT/DELETE | /api/manager/hotels/{id}/ | own only |
| GET/POST | /api/manager/hotels/{id}/room-types/ | |
| PUT/DELETE | /api/manager/room-types/{id}/ | own only |
| GET | /api/manager/hotels/{id}/bookings/ | made bookings (filters: status, date range) |
| GET | /api/manager/hotels/{id}/availability/?date_from&date_to | per room type per day: total, reserved, free |
| GET/POST | /api/manager/hotels/{id}/discounts/ | |
| PUT/DELETE | /api/manager/discounts/{id}/ | |
| GET | /api/amenities/ | list for forms |

## Bonus (later)
`GET/POST /api/hotels/{id}/reviews/` · `GET /api/manager/dashboard/` · `GET /api/guest/dashboard/` · `GET /api/hotels/recommended/`

## Health
`GET /api/health/` → `{"data": {"status": "ok"}}`
