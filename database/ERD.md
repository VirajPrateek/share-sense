# Entity Relationship Diagram

## Visual Schema Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SHARESENSE DATABASE SCHEMA                       │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│      users       │
├──────────────────┤
│ id (PK)          │◄─────────┐
│ email (UNIQUE)   │          │
│ password_hash    │          │
│ name             │          │
│ created_at       │          │
│ updated_at       │          │
└──────────────────┘          │
         │                    │
         │ created_by         │
         ▼                    │
┌──────────────────┐          │
│      flats       │          │
├──────────────────┤          │
│ id (PK)          │◄─────┐   │
│ name             │      │   │
│ created_by (FK)  │      │   │
│ created_at       │      │   │
│ updated_at       │      │   │
└──────────────────┘      │   │
         │                │   │
         │                │   │
         ▼                │   │
┌──────────────────┐      │   │
│  flat_members    │      │   │
├──────────────────┤      │   │
│ id (PK)          │      │   │
│ flat_id (FK)     │──────┘   │
│ user_id (FK)     │──────────┘
│ joined_at        │
└──────────────────┘
         │
         │ (members can create expenses)
         │
         ▼
┌──────────────────┐
│    expenses      │
├──────────────────┤
│ id (PK)          │◄─────┐
│ amount           │      │
│ description      │      │
│ payer_id (FK)    │──────┼───► users
│ flat_id (FK)     │──────┼───► flats (nullable for personal expenses)
│ expense_type     │      │
│ timestamp        │      │
│ created_at       │      │
│ updated_at       │      │
└──────────────────┘      │
         │                │
         │                │
         ▼                │
┌──────────────────┐      │
│ expense_shares   │      │
├──────────────────┤      │
│ id (PK)          │      │
│ expense_id (FK)  │──────┘
│ sharer_id (FK)   │──────────► users
│ share_amount     │
│ created_at       │
└──────────────────┘


┌──────────────────┐
│   settlements    │
├──────────────────┤
│ id (PK)          │◄─────┐
│ flat_id (FK)     │──────┼───► flats
│ debtor_id (FK)   │──────┼───► users
│ creditor_id (FK) │──────┼───► users
│ amount           │      │
│ status           │      │
│ proposed_by (FK) │──────┼───► users
│ created_at       │      │
│ confirmed_at     │      │
└──────────────────┘      │
         │                │
         │                │
         ▼                │
┌──────────────────────┐  │
│ settlement_          │  │
│ confirmations        │  │
├──────────────────────┤  │
│ id (PK)              │  │
│ settlement_id (FK)   │──┘
│ confirmed_by (FK)    │──────► users
│ confirmed_at         │
└──────────────────────┘


┌──────────────────────┐
│ expense_durations    │
├──────────────────────┤
│ id (PK)              │
│ flat_id (FK)         │──────► flats
│ start_date           │
│ end_date             │
│ status               │
│ created_at           │
│ closed_at            │
└──────────────────────┘
```

## Relationship Types

### One-to-Many Relationships

1. **users → flats** (created_by)
   - One user can create many flats
   - Each flat is created by one user

2. **users → expenses** (payer_id)
   - One user can pay for many expenses
   - Each expense has one payer

3. **flats → expenses** (flat_id)
   - One flat can have many expenses
   - Each shared expense belongs to one flat
   - Personal expenses have null flat_id

4. **expenses → expense_shares** (expense_id)
   - One expense can be shared by many users
   - Each share belongs to one expense

5. **flats → settlements** (flat_id)
   - One flat can have many settlements
   - Each settlement belongs to one flat

6. **settlements → settlement_confirmations** (settlement_id)
   - One settlement can have many confirmations
   - Each confirmation belongs to one settlement

7. **flats → expense_durations** (flat_id)
   - One flat can have many expense durations
   - Each duration belongs to one flat

### Many-to-Many Relationships

1. **users ↔ flats** (through flat_members)
   - One user can belong to many flats
   - One flat can have many users
   - Junction table: flat_members

2. **users ↔ expenses** (through expense_shares)
   - One user can share many expenses
   - One expense can be shared by many users
   - Junction table: expense_shares

## Cardinality Notation

```
users (1) ──────< (N) flats
  One user creates many flats

users (1) ──────< (N) flat_members >────── (1) flats
  Many-to-many: Users belong to many flats, flats have many users

users (1) ──────< (N) expenses
  One user pays for many expenses

flats (1) ──────< (N) expenses
  One flat has many expenses (nullable for personal expenses)

expenses (1) ──────< (N) expense_shares >────── (1) users
  Many-to-many: Expenses shared by many users, users share many expenses

flats (1) ──────< (N) settlements
  One flat has many settlements

users (1) ──────< (N) settlements (as debtor)
users (1) ──────< (N) settlements (as creditor)
users (1) ──────< (N) settlements (as proposer)
  One user can be involved in many settlements in different roles

settlements (1) ──────< (N) settlement_confirmations >────── (1) users
  One settlement has many confirmations, one user confirms many settlements

flats (1) ──────< (N) expense_durations
  One flat has many expense durations
```

## Key Constraints

### Primary Keys (PK)
All tables use UUID primary keys for global uniqueness and security.

### Foreign Keys (FK)
- **flat_members**: flat_id → flats(id), user_id → users(id)
- **expenses**: payer_id → users(id), flat_id → flats(id)
- **expense_shares**: expense_id → expenses(id), sharer_id → users(id)
- **settlements**: flat_id → flats(id), debtor_id → users(id), creditor_id → users(id), proposed_by → users(id)
- **settlement_confirmations**: settlement_id → settlements(id), confirmed_by → users(id)
- **expense_durations**: flat_id → flats(id)

### Unique Constraints
- **users**: email (UNIQUE)
- **flat_members**: (flat_id, user_id) - prevents duplicate memberships
- **settlement_confirmations**: (settlement_id, confirmed_by) - prevents duplicate confirmations

### Check Constraints
- **expenses**: amount > 0, expense_type IN ('shared', 'personal')
- **settlements**: status IN ('pending', 'confirmed')
- **expense_durations**: status IN ('open', 'closed')

### Cascade Rules
- **flat_members**: ON DELETE CASCADE (both flat_id and user_id)
- **expenses**: ON DELETE CASCADE (flat_id)
- **expense_shares**: ON DELETE CASCADE (expense_id)
- **settlements**: ON DELETE CASCADE (flat_id)
- **settlement_confirmations**: ON DELETE CASCADE (settlement_id)
- **expense_durations**: ON DELETE CASCADE (flat_id)

## Data Flow Examples

### Creating a Shared Expense
1. User creates expense record in `expenses` table
2. System splits among selected members (user can deselect themselves)
3. System creates records in `expense_shares` for each selected sharer
4. Debts are calculated from expense_shares (sharer owes payer their share amount)
5. If payer deselects themselves, the full amount is owed by the selected members
6. Users can only log expenses they paid for — prevents duplicate entries

### Settlement Process
1. User proposes settlement in `settlements` table (status: 'pending')
2. Debtor and creditor confirm via `settlement_confirmations` table
3. When both confirm, settlement status changes to 'confirmed'
4. Debt balances are updated (calculated from expense_shares minus settlements)

### Flat Membership
1. User creates flat in `flats` table
2. Creator automatically added to `flat_members` table
3. Other users join via `flat_members` table
4. All members can create expenses for the flat

### Personal Expense
1. User creates expense with flat_id = NULL
2. expense_type = 'personal'
3. No records created in `expense_shares`
4. No debts calculated
