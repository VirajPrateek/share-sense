# ShareSense - Requirements Document

## 1. Project Overview
**Name:** ShareSense
**Purpose:** A lightweight web application for groups (flatmates, friends, travelers) to track shared expenses, scan receipts, and settle debts.
**Platform:** Web Application (Mobile-first, PWA installable)

## 2. Core Features

### 2.1 User Authentication
- Email/password registration and login
- JWT-based session management
- Future: Google OAuth for one-tap sign-in

### 2.2 Group Management
- Create groups for any context (flats, trips, dinners, etc.)
- Add members via email
- Remove members
- Groups are generic — the name provides context ("Flat 502", "Goa Trip", "Friday Dinner")

### 2.3 Expense Tracking
- Add expenses with description and amount
- Payer is always the logged-in user (prevents duplicate entries)
- Flexible splitting: select which members share each expense
- Deselect yourself to log expenses paid on behalf of others
- Personal expense tracking (select only yourself — invisible to others)
- AI-powered category inference (no manual category selection)

### 2.4 Receipt Scanning (AI)
- Upload receipt photo or screenshot (BigBasket, Zepto, Blinkit, etc.)
- Gemini AI extracts line items with prices and categories
- Client-side image resizing (1024px max) before upload
- Editable item table with per-item split assignment
- Items grouped by split pattern → submitted as separate expenses
- Full-screen loading overlay during AI processing

### 2.5 Balances & Settlement
- Net balance dashboard (who owes whom, how much)
- Debt simplification algorithm (minimize number of transfers)
- Settlement proposal + confirmation flow
- Suggested settlements based on current balances

### 2.6 Activity Timeline
- Unified chronological feed of expenses and settlements
- Date separators for readability
- Filterable by date range and member
- Shows full split details (who paid, who shares, amount per person)

### 2.7 Privacy
- Users only see expenses they're involved in (as payer or sharer)
- Personal expenses are invisible to other group members
- Only the payer can delete their own expenses

## 3. User Experience
- Mobile-first responsive design
- PWA: installable on home screen, offline viewing of cached data
- Minimal friction: no category picker (AI handles it), no payer dropdown (always you)
- Receipt scan → edit items → assign splits → confirm — one flow

## 4. Performance
- Pre-built Tailwind CSS (26KB vs 419KB CDN runtime)
- Font preconnect hints
- Tab switching uses cached data (no redundant API calls)
- Service worker caches app shell + API responses
- Client-side image compression before AI upload
- Lighthouse: 100/100/100 (Accessibility, Best Practices, SEO)

## 5. Infrastructure
- Vercel (serverless hosting, auto-deploy from Git)
- Supabase PostgreSQL (free tier)
- Gemini AI free tier (receipt parsing)
- Vercel Analytics + Speed Insights
- Zero-cost at small scale
