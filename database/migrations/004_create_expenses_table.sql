-- Create expenses table
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

-- Create indexes for faster queries
CREATE INDEX idx_expenses_payer_id ON expenses(payer_id);
CREATE INDEX idx_expenses_flat_id ON expenses(flat_id);
CREATE INDEX idx_expenses_timestamp ON expenses(timestamp);
CREATE INDEX idx_expenses_expense_type ON expenses(expense_type);

-- Add trigger to automatically update updated_at timestamp
CREATE TRIGGER update_expenses_updated_at
  BEFORE UPDATE ON expenses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
