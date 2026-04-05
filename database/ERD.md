# Entity Relationship Diagram

```
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
│     groups       │          │
├──────────────────┤          │
│ id (PK)          │◄─────┐   │
│ name             │      │   │
│ created_by (FK)  │      │   │
│ created_at       │      │   │
│ updated_at       │      │   │
└──────────────────┘      │   │
         │                │   │
         ▼                │   │
┌──────────────────┐      │   │
│ group_members    │      │   │
├──────────────────┤      │   │
│ id (PK)          │      │   │
│ group_id (FK)    │──────┘   │
│ user_id (FK)     │──────────┘
│ joined_at        │
└──────────────────┘

┌──────────────────┐
│    expenses      │
├──────────────────┤
│ id (PK)          │◄─────┐
│ amount           │      │
│ description      │      │
│ payer_id (FK)    │──────┼───► users
│ group_id (FK)    │──────┼───► groups
│ expense_type     │      │
│ category         │      │    ('other'=manual, else AI-inferred)
│ timestamp        │      │
│ created_at       │      │
│ updated_at       │      │
└──────────────────┘      │
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
│ group_id (FK)    │──────┼───► groups
│ debtor_id (FK)   │──────┼───► users
│ creditor_id (FK) │──────┼───► users
│ amount           │      │
│ status           │      │
│ proposed_by (FK) │──────┼───► users
│ created_at       │      │
│ confirmed_at     │      │
└──────────────────┘      │
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
│ group_id (FK)        │──────► groups
│ start_date           │
│ end_date             │
│ status               │
│ created_at           │
│ closed_at            │
└──────────────────────┘
```

## Key Constraints

- **groups**: name required
- **group_members**: UNIQUE(group_id, user_id)
- **expenses**: amount > 0, expense_type IN ('shared', 'personal'), category defaults to 'other'
- **settlements**: status IN ('pending', 'confirmed')
- **settlement_confirmations**: UNIQUE(settlement_id, confirmed_by)
- All FK relationships use CASCADE deletes

## Data Flows

### Expense Creation
1. User creates expense → payer_id = logged-in user
2. If sharerIds provided, split among those members; otherwise all group members
3. expense_shares records created with equal split amounts
4. Category: 'other' for manual, AI-inferred for receipt scans

### Receipt Scan → Multiple Expenses
1. AI parses receipt into items with prices and categories
2. User assigns per-item splits (toggle members per item)
3. Items grouped by split pattern → separate expense records
4. Each group submitted as one expense with its own sharerIds

### Balance Calculation
1. Sum all amounts paid by each member (from expenses)
2. Subtract all share amounts owed by each member (from expense_shares)
3. Factor in confirmed settlements
4. Greedy algorithm simplifies debts into minimal transfers

### Visibility
- GET expenses filters: WHERE payer_id = user OR sharer_id = user
- Personal expenses (only self selected) invisible to others
