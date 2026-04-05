# ShareSense - Technical Specifications

## 1. Technology Stack

### 1.1 Frontend
- Single HTML file (`base.html`) with embedded JavaScript
- Tailwind CSS v3 (pre-built via PostCSS, not CDN)
- Google Fonts (Manrope + Inter) with preconnect hints
- Material Symbols Outlined for icons
- No framework — vanilla JS with hash-based routing

### 1.2 Backend
- Python 3.10+ with Flask
- JWT authentication (PyJWT)
- Flask-CORS for cross-origin support
- google-genai SDK for Gemini AI integration

### 1.3 Database
- PostgreSQL via Supabase
- psycopg2 driver with RealDictCursor
- Parameterized queries (? → %s rewriting)
- SSL required for Supabase connections

### 1.4 AI Integration
- Google Gemini 2.5 Flash for receipt parsing
- Multimodal input (image + text prompt)
- Structured JSON output (items, prices, categories)
- Client-side image resizing to 1024px before upload

### 1.5 Hosting & Deployment
- Vercel (serverless Python functions)
- Static files served via Vercel's CDN
- `npm run build` as build command (Tailwind CSS compilation)
- Vercel Analytics + Speed Insights

### 1.6 PWA
- Web App Manifest for installability
- Service Worker with network-first strategy for API, cache-first for shell
- Offline viewing of previously loaded data

## 2. Data Model

### `users`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| email | TEXT | Unique |
| password_hash | TEXT | bcrypt-style hash |
| salt | TEXT | Per-user salt |
| name | TEXT | Display name |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### `groups`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| name | TEXT | Group name (e.g. "Flat 502", "Goa Trip") |
| created_by | TEXT | FK → users |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### `group_members`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| group_id | TEXT | FK → groups (CASCADE) |
| user_id | TEXT | FK → users (CASCADE) |
| joined_at | TIMESTAMP | |
| | | UNIQUE(group_id, user_id) |

### `expenses`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| amount | NUMERIC(10,2) | CHECK > 0 |
| description | TEXT | Item list or manual description |
| payer_id | TEXT | FK → users (always the logged-in user) |
| group_id | TEXT | FK → groups (CASCADE) |
| expense_type | TEXT | 'shared' or 'personal' |
| category | TEXT | AI-inferred or 'other' for manual |
| timestamp | TIMESTAMP | User-specified or auto |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### `expense_shares`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| expense_id | TEXT | FK → expenses (CASCADE) |
| sharer_id | TEXT | FK → users |
| share_amount | NUMERIC(10,2) | Equal split amount |
| created_at | TIMESTAMP | |

### `settlements`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| group_id | TEXT | FK → groups (CASCADE) |
| debtor_id | TEXT | FK → users |
| creditor_id | TEXT | FK → users |
| amount | NUMERIC(10,2) | |
| status | TEXT | 'pending' or 'confirmed' |
| proposed_by | TEXT | FK → users |
| created_at | TIMESTAMP | |
| confirmed_at | TIMESTAMP | |

### `settlement_confirmations`
| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| settlement_id | TEXT | FK → settlements (CASCADE) |
| confirmed_by | TEXT | FK → users |
| confirmed_at | TIMESTAMP | |
| | | UNIQUE(settlement_id, confirmed_by) |

## 3. Key Design Decisions

### Payer = Logged-in User
Users can only log expenses they paid for. This prevents duplicate entries when multiple flatmates use the app.

### Category Inference
No manual category picker in the UI. Manual entries get `other`, receipt scans get AI-categorized. `other` = manual, anything else = AI-inferred.

### Visibility Filtering
GET expenses query filters to only show expenses where the current user is the payer or a sharer. Personal expenses (only yourself selected) are invisible to others.

### Receipt → Multiple Expenses
One receipt scan can produce multiple expenses. Items are grouped by their split pattern (who shares each item) and submitted as separate expense records.

### Debt Simplification
Balance calculation uses a greedy algorithm to minimize the number of transfers needed to settle all debts.

## 4. Performance Optimizations

| Optimization | Impact |
|---|---|
| Pre-built Tailwind CSS | 419KB JS → 26KB CSS (94% reduction) |
| Font preconnect hints | Eliminates DNS/TLS discovery delay |
| Tab switching cache | Saves 2 API calls per tab switch |
| Client-side image resize | ~80% upload size reduction for receipts |
| Service worker | Instant app shell on repeat visits |
| Network-first API caching | Offline viewing of last-loaded data |
| Vercel CDN + compression | Automatic gzip/brotli + edge caching |

### Lighthouse Scores
- Accessibility: 100
- Best Practices: 100
- SEO: 100
- LCP: 372ms (localhost)
