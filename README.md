# Hotel Booking — Web Programming Course Project

Django + PostgreSQL backend, React + Vite + Tailwind frontend. Built by two operators with AI agents (Antigravity).

## Start here
1. Read `docs/USAGE_GUIDE_FA.md` (Persian guide to the kit and the command cycle).
2. Open this folder in Antigravity. Run `/bootstrap`, then `/sync`, then `/next`.
3. Project plan: `docs/PLAN.md` · tasks: `docs/tasks/` · board: `python scripts/board.py --me`.

## Backend quick start

1. **Prerequisites**: Python 3.12+ and PostgreSQL 16+ running locally or via Docker (`docker compose up -d`).
2. **Environment configuration**:
   ```bash
   cp .env.example backend/.env
   # Edit backend/.env if your PostgreSQL credentials differ
   ```
3. **Virtual environment & dependencies**:
   ```bash
   cd backend
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```
4. **Database migration & verification**:
   ```bash
   python manage.py check
   python manage.py migrate
   python manage.py test
   ```
5. **Run development server**:
   ```bash
   python manage.py runserver
   # Health check: curl http://localhost:8000/api/health/
   ```
## Frontend quick start

1. **Prerequisites**: Node.js 20+ and npm.
2. **Install dependencies**:
   ```bash
   cd frontend
   npm install  # or npm ci
   ```
3. **Run development server**:
   ```bash
   npm run dev
   # Server starts at http://localhost:5173 (proxies /api -> http://localhost:8000)
   ```
4. **Lint and build verification**:
   ```bash
   npm run lint
   npm run build
   ```
## Demo accounts / seed data (P2-10)

Populate the database with course-required test fixtures (2 managers, 5 guests, 7 hotels in 4 cities, 17 room types, discount codes, 21 bookings):

```bash
# From backend directory with venv activated:
python manage.py seed_demo

# To wipe existing demo records and reseed from scratch:
python manage.py seed_demo --reset
```

### Pre-configured Demo Users

| Username | Email | Password | Role | Description |
|---|---|---|---|---|
| `manager1` | `manager1@hotel.com` | `Manager123!` | Manager | Owns 4 hotels in Tehran and Isfahan |
| `manager2` | `manager2@hotel.com` | `Manager123!` | Manager | Owns 3 hotels in Shiraz and Yazd |
| `guest1` | `guest1@test.com` | `Guest123!` | Guest | Verified guest user with past/current/future bookings |
| `guest2` | `guest2@test.com` | `Guest123!` | Guest | Verified guest user with past/current/future bookings |
| `guest3` | `guest3@test.com` | `Guest123!` | Guest | Verified guest user with past/current/future bookings |
| `guest4` | `guest4@test.com` | `Guest123!` | Guest | Verified guest user with past/current/future bookings |
| `guest5` | `guest5@test.com` | `Guest123!` | Guest | Verified guest user with past/current/future bookings |

### Demo Hotels & Cities

- **Tehran**: هتل اسپیناس پالاس (5★), هتل پارسیان آزادی (5★)
- **Isfahan**: هتل عباسی (5★), هتل بین‌المللی کوثر (5★)
- **Shiraz**: هتل بزرگ چمران (5★), هتل سنتی زندیه (5★)
- **Yazd**: هتل داد یزد (4★)


## Branch model
See `docs/PHASE_BRANCHES.md` (stacked phase branches; `main` = delivered phases only).
