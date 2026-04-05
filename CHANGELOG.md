# ShareSense Changelog

## Current State (April 2026)

### Core Features
- **Groups** (renamed from Flats) — generic expense splitting for flats, trips, dinners, etc.
- **Expense tracking** — flexible splitting, select who shares each expense
- **Receipt scanning** — Gemini AI parses receipt photos/screenshots into itemized entries with per-item split assignment
- **Settlements** — simplified "I paid someone" flow with one-tap confirmation
- **Activity timeline** — filterable by date and member, lazy-loaded
- **PWA** — installable, offline viewing of cached data

### Architecture
- Backend: Python/Flask on Vercel serverless
- Database: PostgreSQL on Supabase
- Frontend: Single HTML file, pre-built Tailwind CSS v3
- AI: Google Gemini 2.5 Flash for receipt parsing + auto-categorization
- Auth: JWT (email/password)

### Key Design Decisions
- **Payer = logged-in user** — you can only log expenses you paid for (prevents duplicates)
- **Category is AI-only** — no manual picker. `other` = manual entry, anything else = AI-inferred from receipt
- **Visibility filtering** — you only see expenses/settlements you're involved in
- **Join codes** — 6-char codes for inviting members (no email sharing needed)
- **Admin controls** — group creator can add/remove members, archive/delete group
- **Settlement auto-confirm** — proposer's side is auto-confirmed, only the other person needs to confirm

### Performance Optimizations
- Pre-built Tailwind CSS (26KB vs 419KB CDN runtime)
- Parallel API fetching (group + members + balances + settlements in one Promise.all)
- Tab switching uses cached data
- Lazy-loaded activity timeline
- Client-side image resizing before Gemini upload (1024px max)
- Material Symbols font lazy-loaded (non-render-blocking)
- Service worker caches app shell + API responses
- Lighthouse: 100/100/100

### Database Tables
- `users` — accounts
- `groups` — groups with join_code and status (active/archived)
- `group_members` — many-to-many
- `expenses` — with category column
- `expense_shares` — per-person split amounts
- `settlements` — with confirmation flow
- `settlement_confirmations` — per-user confirmations
- `expense_durations` — time periods (unused currently)

### Migrations Applied
1. 001-008: Initial schema (users, flats, members, expenses, shares, settlements, confirmations, durations)
2. 009: Added `category` column to expenses
3. 010: Renamed flats → groups, flat_id → group_id everywhere
4. 011: Added `join_code` and `status` columns to groups

### Environment Variables (Vercel)
- `DATABASE_URL` — Supabase Postgres connection string
- `JWT_SECRET` — JWT signing key
- `GEMINI_API_KEY` — Google Gemini API key (enables receipt scanning)
- `GEMINI_MODEL` — defaults to `gemini-2.5-flash`

### File Structure
```
sharesense/
├── app.py                # Flask app + entry point
├── auth.py               # JWT + password hashing
├── config.py             # Env config (DATABASE_URL required)
├── database.py           # Postgres-only connection + schema init
├── routes_auth.py        # Register, login, me
├── routes_groups.py      # Groups CRUD, members, join codes, archive
├── routes_expenses.py    # Expenses, balances, activity timeline
├── routes_settlements.py # Simplified settlement flow
├── routes_receipt.py     # Gemini receipt parsing
├── static/
│   ├── manifest.json     # PWA manifest
│   ├── sw.js             # Service worker (v2)
│   ├── style.css         # Pre-built Tailwind (rebuild: npm run build:css)
│   ├── input.css         # Tailwind source
│   └── icon-*.png        # PWA icons
└── templates/
    └── base.html         # Entire frontend SPA
```

### Common Tasks
- **Add Tailwind classes**: edit base.html, run `npm run build:css`, commit style.css
- **New DB migration**: create in `database/migrations/`, run on Supabase SQL Editor
- **Change Gemini model**: update `GEMINI_MODEL` env var in Vercel
- **Debug locally**: `py sharesense/app.py` (needs DATABASE_URL in .env)

### Known Limitations / Future Work
- No Google OAuth yet (email/password only)
- No push notifications (planned — needs VAPID keys + pywebpush)
- No dark mode (attempted, reverted — needs proper design system work)
- No guest users (need account to join groups)
- expense_durations table exists but isn't used in the UI
- Receipt scanning depends on Gemini free tier quota
