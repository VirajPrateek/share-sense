-- Sharesense Expense Tracking Database Schema
-- Complete database schema for PostgreSQL
-- This file combines all migrations for easy setup

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table
-- Stores user account information for authentication and profile management
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flats table
-- Stores flat/household groups where users share expenses
CREATE TABLE flats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flat members table
-- Stores the many-to-many relationship between users and flats
CREATE TABLE flat_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(flat_id, user_id)
);

-- Expenses table
-- Stores all expense records (both shared and personal)
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
-- Stores the calculated share amounts for each person sharing an expense
CREATE TABLE expense_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  expense_id UUID REFERENCES expenses(id) ON DELETE CASCADE,
  sharer_id UUID REFERENCES users(id),
  share_amount DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settlements table
-- Stores settlement records for debt payments made outside the application
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
-- Stores individual confirmations from users for settlement records
CREATE TABLE settlement_confirmations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  settlement_id UUID REFERENCES settlements(id) ON DELETE CASCADE,
  confirmed_by UUID REFERENCES users(id),
  confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(settlement_id, confirmed_by)
);

-- Expense durations table
-- Stores time periods for organizing and archiving expenses
CREATE TABLE expense_durations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP,
  status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'closed')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  closed_at TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);

-- Flats indexes
CREATE INDEX idx_flats_created_by ON flats(created_by);

-- Flat members indexes
CREATE INDEX idx_flat_members_flat_id ON flat_members(flat_id);
CREATE INDEX idx_flat_members_user_id ON flat_members(user_id);

-- Expenses indexes
CREATE INDEX idx_expenses_payer_id ON expenses(payer_id);
CREATE INDEX idx_expenses_flat_id ON expenses(flat_id);
CREATE INDEX idx_expenses_timestamp ON expenses(timestamp);
CREATE INDEX idx_expenses_expense_type ON expenses(expense_type);

-- Expense shares indexes
CREATE INDEX idx_expense_shares_expense_id ON expense_shares(expense_id);
CREATE INDEX idx_expense_shares_sharer_id ON expense_shares(sharer_id);

-- Settlements indexes
CREATE INDEX idx_settlements_flat_id ON settlements(flat_id);
CREATE INDEX idx_settlements_debtor_id ON settlements(debtor_id);
CREATE INDEX idx_settlements_creditor_id ON settlements(creditor_id);
CREATE INDEX idx_settlements_status ON settlements(status);

-- Settlement confirmations indexes
CREATE INDEX idx_settlement_confirmations_settlement_id ON settlement_confirmations(settlement_id);
CREATE INDEX idx_settlement_confirmations_confirmed_by ON settlement_confirmations(confirmed_by);

-- Expense durations indexes
CREATE INDEX idx_expense_durations_flat_id ON expense_durations(flat_id);
CREATE INDEX idx_expense_durations_status ON expense_durations(status);
CREATE INDEX idx_expense_durations_start_date ON expense_durations(start_date);
CREATE INDEX idx_expense_durations_end_date ON expense_durations(end_date);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for flats table
CREATE TRIGGER update_flats_updated_at
  BEFORE UPDATE ON flats
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for expenses table
CREATE TRIGGER update_expenses_updated_at
  BEFORE UPDATE ON expenses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
