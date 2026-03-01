-- Create flats table
-- Stores flat/household groups where users share expenses

CREATE TABLE flats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on created_by for faster lookups of flats created by a user
CREATE INDEX idx_flats_created_by ON flats(created_by);

-- Add trigger to automatically update updated_at timestamp
CREATE TRIGGER update_flats_updated_at
  BEFORE UPDATE ON flats
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
