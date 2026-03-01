-- Create settlement_confirmations table
-- Stores individual confirmations from users for settlement records

CREATE TABLE settlement_confirmations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  settlement_id UUID REFERENCES settlements(id) ON DELETE CASCADE,
  confirmed_by UUID REFERENCES users(id),
  confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(settlement_id, confirmed_by)
);

-- Create indexes for faster queries
CREATE INDEX idx_settlement_confirmations_settlement_id ON settlement_confirmations(settlement_id);
CREATE INDEX idx_settlement_confirmations_confirmed_by ON settlement_confirmations(confirmed_by);
