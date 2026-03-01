# Design Document: Sharesense Expense Tracking

## Overview

Sharesense is a web application that enables flatmates to track shared expenses and manage bill splitting. The system provides functionality for recording expenses, calculating debt obligations, and tracking settlements between flat members.

### Key Design Goals

1. **Accurate Debt Calculation**: Ensure precise calculation of who owes whom, with proper aggregation and netting of mutual debts
2. **Flexible Expense Sharing**: Support various sharing configurations (all flatmates, subset of flatmates, or personal)
3. **Multi-Flat Support**: Allow users to participate in multiple flats simultaneously
4. **Data Integrity**: Maintain consistency between expenses, debts, and settlements
5. **Auditability**: Preserve complete expense history for review and reporting

### Technology Stack

- **Frontend**: React-based single-page application
- **Backend**: RESTful API (Node.js/Express or similar)
- **Database**: Relational database (PostgreSQL) for transactional consistency
- **Authentication**: JWT-based authentication with secure password hashing

## Architecture

### System Architecture

The application follows a three-tier architecture:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (React SPA - User Interface)           │
└─────────────────┬───────────────────────┘
                  │ HTTPS/REST API
┌─────────────────▼───────────────────────┐
│         Application Layer               │
│  - Authentication Service               │
│  - Expense Management Service           │
│  - Debt Calculation Service             │
│  - Settlement Service                   │
│  - Reporting Service                    │
└─────────────────┬───────────────────────┘
                  │ SQL Queries
┌─────────────────▼───────────────────────┐
│         Data Layer                      │
│  (PostgreSQL Database)                  │
└─────────────────────────────────────────┘
```

### Component Responsibilities

**Authentication Service**
- User registration and login
- JWT token generation and validation
- Session management

**Expense Management Service**
- Create, read, update, delete expenses
- Validate expense data
- Determine expense type (shared vs personal)

**Debt Calculation Service**
- Calculate individual shares for shared expenses
- Aggregate debts between flat members
- Compute net debt positions (offsetting mutual obligations)

**Settlement Service**
- Record settlement confirmations
- Update debt balances after settlement
- Track settlement history

**Reporting Service**
- Generate expense history views
- Filter and aggregate expense data
- Calculate spending summaries

## Components and Interfaces

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Authenticate user and return JWT
- `POST /api/auth/logout` - Invalidate session

#### Flat Management
- `POST /api/flats` - Create new flat
- `GET /api/flats` - List user's flats
- `POST /api/flats/:flatId/members` - Add member to flat
- `GET /api/flats/:flatId/members` - List flat members

#### Expense Management
- `POST /api/expenses` - Create new expense
- `GET /api/expenses` - List expenses (with filters)
- `GET /api/expenses/:expenseId` - Get expense details
- `PUT /api/expenses/:expenseId` - Update expense
- `DELETE /api/expenses/:expenseId` - Delete expense

#### Debt Tracking
- `GET /api/flats/:flatId/debts` - Get debt summary for flat
- `GET /api/users/me/debts` - Get current user's debt positions

#### Settlement
- `POST /api/settlements` - Propose settlement
- `PUT /api/settlements/:settlementId/confirm` - Confirm settlement
- `GET /api/settlements` - List settlement history

#### Reporting
- `GET /api/reports/expenses` - Get expense history with filters
- `GET /api/reports/spending-summary` - Get spending totals

### Service Interfaces

#### DebtCalculationService

```typescript
interface DebtCalculationService {
  calculateExpenseShares(expense: Expense): Share[];
  aggregateDebts(flatId: string): DebtSummary;
  calculateNetDebts(flatId: string): NetDebt[];
}

interface Share {
  flatMemberId: string;
  amount: number;
  expenseId: string;
}

interface DebtSummary {
  flatId: string;
  debts: Debt[];
}

interface Debt {
  debtorId: string;
  creditorId: string;
  amount: number;
}

interface NetDebt {
  fromUserId: string;
  toUserId: string;
  netAmount: number;
}
```

## Data Models

### User
```typescript
interface User {
  id: string;              // UUID
  email: string;           // Unique
  passwordHash: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### Flat
```typescript
interface Flat {
  id: string;              // UUID
  name: string;
  createdBy: string;       // User ID
  createdAt: Date;
  updatedAt: Date;
}
```

### FlatMember
```typescript
interface FlatMember {
  id: string;              // UUID
  flatId: string;          // Foreign key to Flat
  userId: string;          // Foreign key to User
  joinedAt: Date;
}
```

### Expense
```typescript
interface Expense {
  id: string;              // UUID
  amount: number;          // Positive decimal (2 decimal places)
  description: string;
  payerId: string;         // User ID who paid
  flatId: string | null;   // Null for personal expenses
  expenseType: 'shared' | 'personal';
  timestamp: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

### ExpenseShare
```typescript
interface ExpenseShare {
  id: string;              // UUID
  expenseId: string;       // Foreign key to Expense
  sharerId: string;        // User ID who shares the expense
  shareAmount: number;     // Calculated share (2 decimal places)
  createdAt: Date;
}
```

### Settlement
```typescript
interface Settlement {
  id: string;              // UUID
  flatId: string;
  debtorId: string;        // User ID who owes
  creditorId: string;      // User ID who is owed
  amount: number;
  status: 'pending' | 'confirmed';
  proposedBy: string;      // User ID
  confirmedBy: string[];   // Array of User IDs
  createdAt: Date;
  confirmedAt: Date | null;
}
```

### ExpenseDuration
```typescript
interface ExpenseDuration {
  id: string;              // UUID
  flatId: string;
  startDate: Date;
  endDate: Date | null;    // Null for current/open duration
  status: 'open' | 'closed';
  createdAt: Date;
  closedAt: Date | null;
}
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flats table
CREATE TABLE flats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flat members table
CREATE TABLE flat_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(flat_id, user_id)
);

-- Expenses table
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
  description TEXT NOT NULL,
  payer_id UUID REFERENCES users(id),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  expense_type VARCHAR(20) NOT NULL CHECK (expense_type IN ('shared', 'personal')),
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expense shares table
CREATE TABLE expense_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  expense_id UUID REFERENCES expenses(id) ON DELETE CASCADE,
  sharer_id UUID REFERENCES users(id),
  share_amount DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settlements table
CREATE TABLE settlements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  debtor_id UUID REFERENCES users(id),
  creditor_id UUID REFERENCES users(id),
  amount DECIMAL(10, 2) NOT NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed')),
  proposed_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  confirmed_at TIMESTAMP
);

-- Settlement confirmations table
CREATE TABLE settlement_confirmations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  settlement_id UUID REFERENCES settlements(id) ON DELETE CASCADE,
  confirmed_by UUID REFERENCES users(id),
  confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(settlement_id, confirmed_by)
);

-- Expense durations table
CREATE TABLE expense_durations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP,
  status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'closed')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  closed_at TIMESTAMP
);
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User Account Creation with Unique Identifiers

*For any* set of user registration requests, each successfully created user account should have a unique identifier, and retrieving the user should return the same profile information that was provided during registration.

**Validates: Requirements 1.1, 1.3**

### Property 2: Authentication Required for Access

*For any* request to access expense data without valid authentication credentials, the system should reject the request and deny access.

**Validates: Requirements 1.2**

### Property 3: Flat Creation and Membership

*For any* valid flat creation request, the system should successfully create the flat, and the creating user should appear in the flat's member list.

**Validates: Requirements 2.1, 2.3**

### Property 4: Flat Membership Addition

*For any* user and existing flat, when the user joins the flat, querying the flat's member list should include that user.

**Validates: Requirements 2.2, 2.3**

### Property 5: Multi-Flat Membership

*For any* user and multiple flats, the user should be able to join all flats and appear in each flat's member list simultaneously.

**Validates: Requirements 2.4**

### Property 6: Expense Data Persistence Round-Trip

*For any* expense with valid amount, description, payer, and timestamp, creating the expense and then retrieving it should return an expense with identical field values.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 7: Positive Amount Validation

*For any* expense creation request with a non-positive or non-numeric amount, the system should reject the request and not create the expense.

**Validates: Requirements 3.5**

### Property 8: Custom Sharer Selection

*For any* subset of flat members, creating a shared expense with exactly those members as sharers should result in expense shares being created for precisely that subset.

**Validates: Requirements 4.1**

### Property 9: Default Sharing Among All Members

*For any* expense created without specifying sharers, the system should automatically create shares for all flat members equally.

**Validates: Requirements 4.2**

### Property 10: Personal Expense Classification

*For any* expense created with an empty sharers list, the system should classify the expense as type 'personal' and not create any expense shares.

**Validates: Requirements 4.3**

### Property 11: Payer Inclusion Flexibility

*For any* shared expense, the system should allow creating the expense with the payer either included or excluded from the list of sharers, and the resulting shares should reflect this choice.

**Validates: Requirements 4.4**

### Property 12: Equal Share Calculation and Debt Creation

*For any* shared expense with amount A and N sharers, each sharer should have a share amount equal to A/N (rounded to 2 decimal places), and each sharer except the payer should have a debt to the payer equal to their share amount.

**Validates: Requirements 5.1, 5.2**

### Property 13: No Self-Debt

*For any* shared expense where the payer is included as a sharer, the system should not create a debt from the payer to themselves.

**Validates: Requirements 5.3**

### Property 14: Debt Aggregation Across Expenses

*For any* sequence of shared expenses between the same pair of flat members, the total debt from member A to member B should equal the sum of all individual debts created by those expenses.

**Validates: Requirements 5.4**

### Property 15: Debt Summary Calculation

*For any* flat member, the debt summary should show that the total amount owed to them equals the sum of all debts where they are the creditor, and the total amount they owe equals the sum of all debts where they are the debtor.

**Validates: Requirements 6.1, 6.2**

### Property 16: Debt Netting

*For any* pair of flat members A and B, if A owes B amount X and B owes A amount Y, the net debt should be a single debt of amount |X - Y| from the member with the larger debt to the other member.

**Validates: Requirements 6.3**

### Property 17: Currency Precision

*For any* debt balance or expense amount displayed by the system, the value should be formatted with exactly two decimal places.

**Validates: Requirements 6.4**

### Property 18: Personal Expense Creation

*For any* expense created with a null flat_id, the system should successfully create the expense as a personal expense.

**Validates: Requirements 7.1**

### Property 19: Expense Type Filtering

*For any* query filtering expenses by type (personal or shared), all returned expenses should have the specified expense_type value.

**Validates: Requirements 7.2, 10.3**

### Property 20: Personal Expenses Excluded from Debts

*For any* personal expense created by a user, the creation should not result in any new debts or changes to existing debt balances.

**Validates: Requirements 7.3**

### Property 21: Settlement Confirmation Mechanism

*For any* proposed settlement between a debtor and creditor, both parties should be able to submit confirmations, and the settlement should only be marked as 'confirmed' after both confirmations are received.

**Validates: Requirements 8.1, 8.2, 8.4**

### Property 22: Settlement Updates Debt Balance

*For any* confirmed settlement of amount A between debtor and creditor, the debt balance from debtor to creditor should be reduced by exactly amount A.

**Validates: Requirements 8.3**

### Property 23: Expense Duration Closure

*For any* open expense duration, closing it should change its status to 'closed' and set the end_date and closed_at timestamps.

**Validates: Requirements 9.1**

### Property 24: Debt Carryover

*For any* expense duration closed with outstanding debts, the system should allow creating a new duration and carrying forward the unsettled debt balances.

**Validates: Requirements 9.2**

### Property 25: Expense Archival

*For any* closed expense duration, all expenses from that duration should remain retrievable and associated with that duration.

**Validates: Requirements 9.3, 9.4**

### Property 26: Chronological Expense Ordering

*For any* query for a flat member's expenses, the returned list should be ordered by timestamp in chronological order.

**Validates: Requirements 10.1**

### Property 27: Date Range Filtering

*For any* query with a date range filter, all returned expenses should have timestamps within the specified range (inclusive).

**Validates: Requirements 10.2**

### Property 28: Spending Total Calculation

*For any* flat member and time period, the displayed spending total should equal the sum of all expense amounts paid by that member within the time period.

**Validates: Requirements 10.4**

## Error Handling

### Input Validation Errors

**Invalid Expense Amount**
- Trigger: Non-positive or non-numeric amount
- Response: HTTP 400 Bad Request with error message "Expense amount must be a positive number"
- System State: No expense created, database unchanged

**Invalid User Credentials**
- Trigger: Incorrect email/password during login
- Response: HTTP 401 Unauthorized with error message "Invalid credentials"
- System State: No session created, no token issued

**Duplicate Email Registration**
- Trigger: Attempt to register with existing email
- Response: HTTP 409 Conflict with error message "Email already registered"
- System State: No new user created

**Invalid Flat Member Selection**
- Trigger: Selecting sharers who are not members of the flat
- Response: HTTP 400 Bad Request with error message "All sharers must be members of the flat"
- System State: No expense created

### Authorization Errors

**Unauthorized Expense Access**
- Trigger: User attempts to view expenses from a flat they don't belong to
- Response: HTTP 403 Forbidden with error message "Access denied"
- System State: No data returned

**Unauthorized Settlement Confirmation**
- Trigger: User who is neither debtor nor creditor attempts to confirm settlement
- Response: HTTP 403 Forbidden with error message "Only involved parties can confirm settlement"
- System State: Settlement status unchanged

### Data Integrity Errors

**Expense Without Payer**
- Trigger: Attempt to create expense with invalid or missing payer_id
- Response: HTTP 400 Bad Request with error message "Valid payer required"
- System State: No expense created

**Settlement Amount Exceeds Debt**
- Trigger: Proposed settlement amount greater than actual debt
- Response: HTTP 400 Bad Request with error message "Settlement amount cannot exceed debt balance"
- System State: No settlement created

**Closed Duration Modification**
- Trigger: Attempt to add expense to closed duration
- Response: HTTP 400 Bad Request with error message "Cannot modify closed expense duration"
- System State: No expense created, duration unchanged

### System Errors

**Database Connection Failure**
- Trigger: Database unavailable or connection timeout
- Response: HTTP 503 Service Unavailable with error message "Service temporarily unavailable"
- System State: Transaction rolled back, no data modified
- Recovery: Retry with exponential backoff

**Calculation Overflow**
- Trigger: Expense amounts or debt totals exceed numeric limits
- Response: HTTP 400 Bad Request with error message "Amount exceeds maximum allowed value"
- System State: No data modified

## Testing Strategy

### Overview

The testing strategy employs a dual approach combining unit tests for specific scenarios and property-based tests for comprehensive validation of system correctness.

### Unit Testing

Unit tests focus on:
- **Specific Examples**: Concrete scenarios that demonstrate correct behavior (e.g., "splitting $100 among 4 people results in $25 each")
- **Edge Cases**: Boundary conditions (e.g., expense with 1 sharer, expense with amount $0.01)
- **Error Conditions**: Invalid inputs and error handling (e.g., negative amounts, unauthorized access)
- **Integration Points**: Interactions between services (e.g., expense creation triggering debt calculation)

**Example Unit Tests**:
- Test that creating an expense with amount $100 and 4 sharers creates 4 shares of $25 each
- Test that attempting to create an expense with amount -50 returns a 400 error
- Test that a user cannot view expenses from a flat they don't belong to
- Test that closing an expense duration sets the status to 'closed'

### Property-Based Testing

Property-based tests validate universal properties across randomized inputs. Each property test should:
- Run a minimum of 100 iterations with randomly generated test data
- Reference the corresponding design document property in a comment
- Use the tag format: `Feature: sharesense-expense-tracking, Property {number}: {property_text}`

**Property Testing Library**: Use `fast-check` (for JavaScript/TypeScript) or `hypothesis` (for Python) for property-based testing implementation.

**Example Property Test Configuration**:
```typescript
// Feature: sharesense-expense-tracking, Property 12: Equal Share Calculation and Debt Creation
fc.assert(
  fc.property(
    fc.float({ min: 0.01, max: 10000 }), // expense amount
    fc.integer({ min: 2, max: 10 }),      // number of sharers
    (amount, numSharers) => {
      const expense = createSharedExpense(amount, numSharers);
      const shares = calculateShares(expense);
      
      // Each share should equal amount / numSharers (rounded to 2 decimals)
      const expectedShare = Math.round((amount / numSharers) * 100) / 100;
      return shares.every(share => share.amount === expectedShare);
    }
  ),
  { numRuns: 100 }
);
```

**Property Test Coverage**:
- All 28 correctness properties defined in this document must have corresponding property-based tests
- Each test should generate diverse random inputs (amounts, user counts, expense configurations)
- Tests should verify both positive cases (valid operations succeed) and negative cases (invalid operations fail)

### Test Data Generation

**Random Data Generators**:
- **User Data**: Random emails, names, passwords
- **Expense Data**: Random amounts (0.01 to 10000), descriptions, timestamps
- **Flat Data**: Random flat names, member counts (1 to 20)
- **Sharer Configurations**: Random subsets of flat members

**Constraints**:
- Amounts: Always positive, max 2 decimal places
- Dates: Valid timestamps within reasonable ranges
- IDs: Valid UUIDs
- Relationships: Maintain referential integrity (e.g., sharers must be flat members)

### Integration Testing

Integration tests verify:
- End-to-end workflows (user registration → flat creation → expense recording → debt calculation)
- API endpoint interactions
- Database transaction consistency
- Authentication and authorization flows

### Performance Testing

Performance tests validate:
- Response times for debt calculation with large numbers of expenses
- Query performance for expense history with date range filters
- Concurrent user operations (multiple users adding expenses simultaneously)
- Database query optimization (proper indexing on foreign keys and timestamps)

### Test Environment

- **Unit Tests**: Run against in-memory database or mocked services
- **Integration Tests**: Run against test database with isolated test data
- **Property Tests**: Run against test database with transaction rollback after each test
- **CI/CD**: All tests run automatically on every commit, with property tests running full 100 iterations

