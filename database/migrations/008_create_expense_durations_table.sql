-- Create expense_durations table
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

-- Create indexes for faster queries
CREATE INDEX idx_expense_durations_flat_id ON expense_durations(flat_id);
CREATE INDEX idx_expense_durations_status ON expense_durations(status);
CREATE INDEX idx_expense_durations_start_date ON expense_durations(start_date);
CREATE INDEX idx_expense_durations_end_date ON expense_durations(end_date);
