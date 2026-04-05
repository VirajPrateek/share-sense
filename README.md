# ShareSense

A lightweight web app for splitting expenses in groups — flats, trips, dinners, anything. AI-powered receipt scanning, smart categorization, and a clean activity trail.

## Tech Stack

- Python + Flask (backend API + server-rendered SPA)
- PostgreSQL via Supabase (database)
- Tailwind CSS v3 (pre-built, not CDN)
- Gemini AI (receipt parsing + auto-categorization)
- Vercel (hosting + serverless)
- PWA (installable, offline-capable)

## Features

- JWT auth (email/password)
- Create and manage groups (flats, trips, dinners)
- Add/remove members via email
- Expense tracking with flexible splitting (select who pays what)
- AI receipt scanning — snap a photo, get itemized entries with per-item split assignment
- Auto-categorization via Gemini (groceries, food, transport, etc.)
- Personal expense tracking (select only yourself)
- Privacy filtering (you only see expenses you're involved in)
- Settlement management with confirmation flow
- Unified activity timeline with date/member filters
- Balance calculation with debt simplification algorithm

## Quick Start

```bash
# Install Python dependencies
py -m pip install -r requirements.txt

# Install Node dependencies (for Tailwind build)
npm install

# Build CSS
npm run build:css

# Set up .env (copy from .env.example, add DATABASE_URL + GEMINI_API_KEY)
cp .env.example .env

# Run
py sharesense/app.py
```

Open http://localhost:3000

## API Endpoints

### Auth
- `POST /api/auth/register` — Register
- `POST /api/auth/login` — Login (returns JWT)
- `GET /api/auth/me` — Current user

### Groups
- `POST /api/groups` — Create a group
- `GET /api/groups` — List your groups
- `GET /api/groups/:id` — Group details
- `GET /api/groups/:id/members` — List members
- `POST /api/groups/:id/members` — Add member
- `DELETE /api/groups/:id/members/:userId` — Remove member

### Expenses
- `POST /api/groups/:id/expenses` — Add expense (with sharerIds for custom splits)
- `GET /api/groups/:id/expenses` — List expenses (filtered to your visibility)
- `DELETE /api/groups/:id/expenses/:expenseId` — Delete (payer only)
- `GET /api/groups/:id/balances` — Net balances + suggested transfers
- `GET /api/groups/:id/activity` — Unified timeline (supports ?from, ?to, ?memberId filters)

### Settlements
- `POST /api/groups/:id/settlements` — Propose settlement
- `GET /api/groups/:id/settlements` — List settlements
- `POST /api/groups/:id/settlements/:sid/confirm` — Confirm

### Receipt Parsing
- `POST /api/parse-receipt` — Parse receipt image via Gemini AI (returns items + categories)

## Performance Optimizations

- Tailwind CSS pre-built (26KB) instead of CDN runtime compiler (419KB JS) — 94% reduction
- Font preconnect hints for Google Fonts
- Client-side image resizing before Gemini upload (1024px max, ~80% size reduction)
- Tab switching caches group/member data (eliminates redundant API calls)
- PWA service worker caches app shell + API responses for offline viewing
- Vercel Analytics + Speed Insights integration
- Lighthouse scores: Accessibility 100, Best Practices 100, SEO 100

## Project Structure

```
sharesense/
├── app.py                # Flask app entry point
├── auth.py               # JWT + password hashing
├── config.py             # Environment config
├── database.py           # PostgreSQL connection + schema init
├── routes_auth.py        # Auth endpoints
├── routes_groups.py      # Group CRUD + members
├── routes_expenses.py    # Expenses, balances, activity
├── routes_settlements.py # Settlement endpoints
├── routes_receipt.py     # Gemini receipt parsing
├── static/
│   ├── manifest.json     # PWA manifest
│   ├── sw.js             # Service worker
│   ├── style.css         # Pre-built Tailwind CSS
│   └── icon-*.png        # PWA icons
└── templates/
    └── base.html         # Single-page app UI
```
