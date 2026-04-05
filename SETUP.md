# ShareSense Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+ (for Tailwind CSS build)
- Supabase account (free tier works)
- Gemini API key (optional, for receipt scanning)

## Setup

### 1. Install dependencies

```bash
py -m pip install -r requirements.txt
npm install
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres
JWT_SECRET=your-secret-key
GEMINI_API_KEY=your-gemini-key    # optional
GEMINI_MODEL=gemini-2.5-flash     # optional, defaults to gemini-2.5-flash
```

### 3. Set up database

Run the schema on your Supabase SQL Editor:
- Either run `database/schema.sql` for a fresh setup
- Or run migrations in `database/migrations/` in order for incremental updates

### 4. Build CSS

```bash
npm run build:css
```

This generates `sharesense/static/style.css` from Tailwind. Run this after any HTML template changes.

### 5. Run locally

```bash
py sharesense/app.py
```

Open http://localhost:3000

## Deploying to Vercel

The app is configured for Vercel deployment:

1. Push to GitHub
2. Connect repo in Vercel dashboard
3. Add environment variables: `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY`
4. Enable Analytics and Speed Insights in Vercel dashboard
5. Deploy — `npm run build` runs automatically via `vercel.json`

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | Supabase PostgreSQL connection string |
| `JWT_SECRET` | Yes | dev-secret-change-me | JWT signing key |
| `JWT_EXPIRES_HOURS` | No | 168 (7 days) | Token expiry |
| `PORT` | No | 3000 | Server port |
| `GEMINI_API_KEY` | No | — | Enables receipt scanning |
| `GEMINI_MODEL` | No | gemini-2.5-flash | Gemini model for parsing |

## Tailwind CSS

The app uses pre-built Tailwind CSS (not the CDN). After editing HTML templates:

```bash
npm run build:css
```

This scans `sharesense/templates/**/*.html` for used classes and generates a minified CSS file (~26KB vs 419KB CDN runtime).

On Vercel, this runs automatically during deployment.

## Troubleshooting

### "DATABASE_URL environment variable is required"
You need a Supabase database. Create one at supabase.com and add the connection string to `.env`.

### "Receipt scanning is not configured"
Add `GEMINI_API_KEY` to your `.env` (local) or Vercel environment variables (production).

### "AI quota exceeded"
Your Gemini free tier is exhausted. Wait for daily reset or create a new API key in a different Google Cloud project at aistudio.google.com/apikey.

### CSS looks broken after template changes
Run `npm run build:css` to regenerate the Tailwind CSS file.
