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
## Frontend quick start  (filled in P0-04)
## Demo accounts / seed data (filled in P2-10)
