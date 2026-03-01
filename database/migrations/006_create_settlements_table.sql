-- Create settlements table
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

-- Create indexes for faster queries
CREATE INDEX idx_settlements_flat_id ON settlements(flat_id);
CREATE INDEX idx_settlements_debtor_id ON settlements(debtor_id);
CREATE INDEX idx_settlements_creditor_id ON settlements(creditor_id);
CREATE INDEX idx_settlements_status ON settlements(status);
