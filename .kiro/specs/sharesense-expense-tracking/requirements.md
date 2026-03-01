# Requirements Document

## Introduction

Sharesense is a web application that enables flatmates to track shared expenses and manage bill splitting. The system allows users to record expenses, specify cost-sharing arrangements among flat members, and track debt settlements. The application also supports personal expense tracking for individual users who choose not to share expenses.

## Glossary

- **User**: An individual person who has an account in the Sharesense system
- **Flat**: A group of Users who share living expenses
- **Flat_Member**: A User who belongs to a specific Flat
- **Expense**: A financial transaction record containing amount, description, payer, and sharing details
- **Shared_Expense**: An Expense that is split among multiple Flat_Members
- **Personal_Expense**: An Expense that is not shared with any other User
- **Debt**: The amount one Flat_Member owes to another Flat_Member based on Shared_Expenses
- **Settlement**: The process of marking Debts as paid outside the application
- **Expense_Duration**: A time period during which Expenses are tracked before Settlement

## Requirements

### Requirement 1: User Account Management

**User Story:** As a user, I want to create and manage my account, so that I can access the expense tracking system.

#### Acceptance Criteria

1. THE Sharesense_System SHALL allow Users to create accounts with unique identifiers
2. THE Sharesense_System SHALL authenticate Users before granting access to expense data
3. THE Sharesense_System SHALL maintain User profile information

### Requirement 2: Flat Creation and Management

**User Story:** As a user, I want to create or join a flat, so that I can share expenses with my flatmates.

#### Acceptance Criteria

1. THE Sharesense_System SHALL allow Users to create new Flats
2. THE Sharesense_System SHALL allow Users to join existing Flats
3. THE Sharesense_System SHALL maintain a list of Flat_Members for each Flat
4. THE Sharesense_System SHALL allow Users to belong to multiple Flats

### Requirement 3: Expense Recording

**User Story:** As a flat member, I want to record expenses I've paid, so that I can track my spending and share costs with flatmates.

#### Acceptance Criteria

1. WHEN a Flat_Member records an Expense, THE Sharesense_System SHALL capture the amount paid
2. WHEN a Flat_Member records an Expense, THE Sharesense_System SHALL capture a description of the Expense
3. WHEN a Flat_Member records an Expense, THE Sharesense_System SHALL record the Flat_Member as the payer
4. WHEN a Flat_Member records an Expense, THE Sharesense_System SHALL record the timestamp of the Expense
5. THE Sharesense_System SHALL validate that Expense amounts are positive numeric values

### Requirement 4: Expense Sharing Configuration

**User Story:** As a flat member, I want to specify who shares an expense, so that costs are split appropriately among the right people.

#### Acceptance Criteria

1. WHEN a Flat_Member records an Expense, THE Sharesense_System SHALL allow the Flat_Member to select which Flat_Members share the Expense
2. WHEN a Flat_Member records an Expense without selecting specific sharers, THE Sharesense_System SHALL default to sharing the Expense equally among all Flat_Members
3. WHEN a Flat_Member records an Expense without selecting any sharers, THE Sharesense_System SHALL record the Expense as a Personal_Expense
4. THE Sharesense_System SHALL allow the payer to be included or excluded from the list of sharers

### Requirement 5: Expense Splitting Calculation

**User Story:** As a flat member, I want the system to calculate how much each person owes, so that I know who needs to pay whom.

#### Acceptance Criteria

1. WHEN a Shared_Expense is recorded, THE Sharesense_System SHALL calculate each sharer's portion by dividing the total amount equally among all sharers
2. WHEN a Shared_Expense is recorded, THE Sharesense_System SHALL calculate the Debt each sharer owes to the payer
3. THE Sharesense_System SHALL exclude the payer from owing themselves when the payer is included as a sharer
4. THE Sharesense_System SHALL aggregate Debts between the same pair of Flat_Members across multiple Expenses

### Requirement 6: Debt Tracking and Display

**User Story:** As a flat member, I want to see who owes me money and whom I owe, so that I can settle debts appropriately.

#### Acceptance Criteria

1. THE Sharesense_System SHALL display the total amount each Flat_Member owes to the current User
2. THE Sharesense_System SHALL display the total amount the current User owes to each Flat_Member
3. THE Sharesense_System SHALL calculate net Debts by offsetting mutual obligations between Flat_Members
4. THE Sharesense_System SHALL display Debt balances with currency precision to two decimal places

### Requirement 7: Personal Expense Tracking

**User Story:** As a user, I want to track personal expenses that I don't share with anyone, so that I can monitor my individual spending.

#### Acceptance Criteria

1. THE Sharesense_System SHALL allow Users to record Personal_Expenses without associating them with a Flat
2. THE Sharesense_System SHALL display Personal_Expenses separately from Shared_Expenses
3. THE Sharesense_System SHALL exclude Personal_Expenses from Debt calculations

### Requirement 8: Debt Settlement Process

**User Story:** As a flat member, I want to mark debts as settled after paying outside the app, so that my balance reflects actual payments made.

#### Acceptance Criteria

1. WHEN Flat_Members agree that a Debt has been paid externally, THE Sharesense_System SHALL allow all involved parties to confirm the Settlement
2. WHEN a Settlement is confirmed by all parties, THE Sharesense_System SHALL mark the Debt as settled
3. WHEN a Settlement is confirmed, THE Sharesense_System SHALL update the Debt balances to reflect the Settlement
4. THE Sharesense_System SHALL require confirmation from both the debtor and creditor before marking a Debt as settled

### Requirement 9: Expense Duration Management

**User Story:** As a flat member, I want to close or carry forward expense periods, so that I can organize expenses by time periods.

#### Acceptance Criteria

1. THE Sharesense_System SHALL allow Flat_Members to close an Expense_Duration
2. WHEN an Expense_Duration is closed with outstanding Debts, THE Sharesense_System SHALL allow Flat_Members to carry forward unsettled Debts to the next Expense_Duration
3. WHEN an Expense_Duration is closed, THE Sharesense_System SHALL archive Expenses from that duration
4. THE Sharesense_System SHALL allow Flat_Members to view historical Expense_Durations and their associated Expenses

### Requirement 10: Expense History and Reporting

**User Story:** As a flat member, I want to view my expense history, so that I can review past transactions and spending patterns.

#### Acceptance Criteria

1. THE Sharesense_System SHALL display a chronological list of all Expenses for a Flat_Member
2. THE Sharesense_System SHALL allow Flat_Members to filter Expenses by date range
3. THE Sharesense_System SHALL allow Flat_Members to filter Expenses by type (Shared_Expense or Personal_Expense)
4. THE Sharesense_System SHALL display the total amount spent by a Flat_Member within a selected time period
