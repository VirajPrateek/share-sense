# ShareSense Database Schema

## Overview

PostgreSQL schema on Supabase supporting:
- User accounts and authentication
- Group creation and membership (flats, trips, dinners, etc.)
- Expense recording with flexible splitting
- AI-categorized expenses
- Settlement management with confirmation flow
- Activity timeline queries

## Tables

| Table | Purpose |
|---|---|
| `users` | User accounts (email, password hash, name) |
| `groups` | Groups where users share expenses |
| `group_members` | Many-to-many: users ↔ groups |
| `expenses` | Expense records with category and split info |
| `expense_shares` | Per-person share amounts for each expense |
| `settlements` | Debt payment records between members |
| `settlement_confirmations` | Per-user confirmations for settlements |
| `expense_durations` | Time periods for organizing expenses |

## Setup

### Fresh install
Run `schema.sql` in Supabase SQL Editor.

### Incremental updates
Run migrations in `migrations/` in order (001, 002, ...).

### Key migrations
- `009_add_category_to_expenses.sql` — Adds AI category column
- `010_rename_flats_to_groups.sql` — Renames flats → groups for generic use

## Relationships

```
users
  ├─→ groups (created_by)
  ├─→ group_members (user_id)
  ├─→ expenses (payer_id)
  ├─→ expense_shares (sharer_id)
  ├─→ settlements (debtor_id, creditor_id, proposed_by)
  └─→ settlement_confirmations (confirmed_by)

groups
  ├─→ group_members (group_id)
  ├─→ expenses (group_id)
  ├─→ settlements (group_id)
  └─→ expense_durations (group_id)

expenses → expense_shares (expense_id)
settlements → settlement_confirmations (settlement_id)
```

## Design Decisions

- UUID primary keys for security and scalability
- DECIMAL(10,2) for monetary amounts (no floating-point errors)
- CASCADE deletes maintain referential integrity
- Category column defaults to 'other' (manual) — AI sets specific values
- Visibility: expense queries filter by payer_id OR sharer_id
