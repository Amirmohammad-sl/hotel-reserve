# 03 — Frontend (React + Vite + Tailwind) conventions

- JavaScript (not TypeScript). Functional components + hooks. React Router for routing.
- Tailwind CSS installed per the CURRENT official "Tailwind with Vite" guide (check docs; don't guess the version syntax).
- UI language Persian, `<html lang="fa" dir="rtl">`. Prefer Tailwind logical utilities (`ms-`, `me-`, `ps-`, `pe-`, `text-start`).
  Font: Vazirmatn via npm `@fontsource/vazirmatn` (works offline). Dates sent to API as ISO `YYYY-MM-DD`;
  displayed with `Intl.DateTimeFormat("fa-IR")`.
- Structure:
  ```
  src/api/client.js     fetch wrapper (credentials: "same-origin", JSON, CSRF header from `csrftoken` cookie, normalized errors)
  src/api/<resource>.js hotels.js, bookings.js, auth.js, manager.js ...
  src/context/AuthContext.jsx   current user + role, login/logout/refresh
  src/routes.jsx        route table + guards (RequireAuth, RequireRole)
  src/pages/public|guest|manager/...
  src/components/       small reusable UI (Button, Input, Card, Spinner, ErrorMessage, Pagination ...)
  ```
- Components never call `fetch` directly — only through `src/api/*`.
- Every data screen has 3 states: **loading**, **error**, **empty**. Forms show server field errors under inputs.
- Auth state comes from `GET /api/auth/me/` on app start. No tokens in localStorage.
- Mobile-first responsive layout. Keep components small (< ~150 lines); extract when bigger.
- Dev: Vite proxy `/api` → `http://localhost:8000` so cookies are same-origin. Production: `npm run build` output is served by
  Django through a template (P2-11): Vite configured with fixed file names (`assets/app.js`, `assets/app.css`).
- Lint must pass (`npm run lint`), build must pass (`npm run build`) before PR.
- Map (bonus): `react-leaflet` + OpenStreetMap tiles. Calendar (bonus): build a simple month grid ourselves (no heavy lib) unless /decision.
