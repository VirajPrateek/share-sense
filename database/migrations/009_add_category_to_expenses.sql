-- Add category column to expenses table
-- Stores the expense category (groceries, rent, utilities, fun, food, transport, other)

ALTER TABLE expenses ADD COLUMN category VARCHAR(50) DEFAULT 'other';

-- Create index for filtering by category
CREATE INDEX idx_expenses_category ON expenses(category);
