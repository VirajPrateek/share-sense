# Sharesense Database Schema

This directory contains the database schema for the Sharesense expense tracking application.

## Overview

The database is designed for PostgreSQL and implements a relational schema to support:
- User account management
- Flat (household) creation and membership
- Expense recording and sharing
- Debt calculation and tracking
- Settlement management
- Expense duration/period management

## Files

- `schema.sql` - Complete database schema (all tables, indexes, and triggers)
- `migrations/` - Individual migration files for incremental schema updates

## Schema Structure

### Core Tables

#### users
Stores user account information for authentication and profile management.
- Primary key: `id` (UUID)
- Unique constraint: `email`
- Includes password hash, name, and timestamps

#### flats
Stores flat/household groups where users share expenses.
- Primary key: `id` (UUID)
- Foreign key: `created_by` → `users(id)`
- Tracks flat name and creation metadata

#### flat_members
Many-to-many relationship between users and flats.
- Primary key: `id` (UUID)
- Foreign keys: `flat_id` → `flats(id)`, `user_id` → `users(id)`
- Unique constraint: `(flat_id, user_id)` - prevents duplicate memberships
- Cascade delete: removes memberships when flat or user is deleted

#### expenses
Stores all expense records (both shared and personal).
- Primary key: `id` (UUID)
- Foreign keys: `payer_id` → `users(id)`, `flat_id` → `flats(id)`
- Check constraint: `amount > 0`
- Check constraint: `expense_type IN ('shared', 'personal')`
- Indexed on: payer_id, flat_id, timestamp, expense_type

#### expense_shares
Stores calculated share amounts for each person sharing an expense.
- Primary key: `id` (UUID)
- Foreign keys: `expense_id` → `expenses(id)`, `sharer_id` → `users(id)`
- Cascade delete: removes shares when expense is deleted
- Used to calculate debts between flat members

#### settlements
Stores settlement records for debt payments made outside the application.
- Primary key: `id` (UUID)
- Foreign keys: `flat_id` → `flats(id)`, `debtor_id` → `users(id)`, `creditor_id` → `users(id)`, `proposed_by` → `users(id)`
- Check constraint: `status IN ('pending', 'confirmed')`
- Tracks settlement amount and confirmation status

#### settlement_confirmations
Stores individual confirmations from users for settlement records.
- Primary key: `id` (UUID)
- Foreign keys: `settlement_id` → `settlements(id)`, `confirmed_by` → `users(id)`
- Unique constraint: `(settlement_id, confirmed_by)` - prevents duplicate confirmations
- Cascade delete: removes confirmations when settlement is deleted

#### expense_durations
Stores time periods for organizing and archiving expenses.
- Primary key: `id` (UUID)
- Foreign key: `flat_id` → `flats(id)`
- Check constraint: `status IN ('open', 'closed')`
- Supports expense period management and archival

## Key Design Decisions

### UUID Primary Keys
All tables use UUID primary keys for:
- Global uniqueness across distributed systems
- Security (non-sequential, harder to guess)
- Future scalability

### Cascade Deletes
- `flat_members`: Cascade on both flat and user deletion
- `expenses`: Cascade on flat deletion
- `expense_shares`: Cascade on expense deletion
- `settlement_confirmations`: Cascade on settlement deletion

This ensures referential integrity and prevents orphaned records.

### Decimal Precision
All monetary amounts use `DECIMAL(10, 2)` for:
- Exact decimal arithmetic (no floating-point errors)
- Support for amounts up to 99,999,999.99
- Two decimal places for currency precision

### Indexes
Strategic indexes on:
- Foreign keys (for join performance)
- Frequently queried columns (email, timestamp, status)
- Columns used in WHERE clauses and ORDER BY

### Timestamps
- `created_at`: Automatically set on record creation
- `updated_at`: Automatically updated via trigger on record modification
- `timestamp`: User-specified expense date/time
- `joined_at`, `confirmed_at`, `closed_at`: Event-specific timestamps

### Constraints
- Unique constraints prevent duplicate data (email, flat membership, settlement confirmations)
- Check constraints enforce business rules (positive amounts, valid enum values)
- Foreign key constraints maintain referential integrity

## Setup Instructions

### Option 1: Complete Schema
Run the complete schema file to set up all tables at once:

```bash
psql -U your_username -d sharesense -f schema.sql
```

### Option 2: Incremental Migrations
Run migrations in order for version-controlled schema updates:

```bash
psql -U your_username -d sharesense -f migrations/001_create_users_table.sql
psql -U your_username -d sharesense -f migrations/002_create_flats_table.sql
psql -U your_username -d sharesense -f migrations/003_create_flat_members_table.sql
psql -U your_username -d sharesense -f migrations/004_create_expenses_table.sql
psql -U your_username -d sharesense -f migrations/005_create_expense_shares_table.sql
psql -U your_username -d sharesense -f migrations/006_create_settlements_table.sql
psql -U your_username -d sharesense -f migrations/007_create_settlement_confirmations_table.sql
psql -U your_username -d sharesense -f migrations/008_create_expense_durations_table.sql
```

## Database Relationships

```
users
  ├─→ flats (created_by)
  ├─→ flat_members (user_id)
  ├─→ expenses (payer_id)
  ├─→ expense_shares (sharer_id)
  ├─→ settlements (debtor_id, creditor_id, proposed_by)
  └─→ settlement_confirmations (confirmed_by)

flats
  ├─→ flat_members (flat_id)
  ├─→ expenses (flat_id)
  ├─→ settlements (flat_id)
  └─→ expense_durations (flat_id)

expenses
  └─→ expense_shares (expense_id)

settlements
  └─→ settlement_confirmations (settlement_id)
```

## Data Integrity Rules

1. **User Deletion**: When a user is deleted, their flat memberships are removed (cascade)
2. **Flat Deletion**: When a flat is deleted, all associated memberships, expenses, settlements, and durations are removed (cascade)
3. **Expense Deletion**: When an expense is deleted, all associated shares are removed (cascade)
4. **Settlement Deletion**: When a settlement is deleted, all confirmations are removed (cascade)
5. **Unique Memberships**: A user can only be a member of a flat once
6. **Unique Confirmations**: A user can only confirm a settlement once
7. **Positive Amounts**: All expense and settlement amounts must be positive
8. **Valid Types**: Expense types must be 'shared' or 'personal', statuses must be valid enum values

## Performance Considerations

- Indexes on foreign keys optimize JOIN operations
- Indexes on timestamp enable efficient date range queries
- Indexes on status fields speed up filtering by state
- Composite unique indexes prevent duplicate data while enabling fast lookups

## Future Enhancements

Potential schema extensions:
- Add `expense_categories` table for expense categorization
- Add `flat_invitations` table for invitation workflow
- Add `audit_log` table for tracking changes
- Add `user_preferences` table for user settings
- Add support for custom split ratios (not just equal splits)
