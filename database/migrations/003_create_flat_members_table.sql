-- Create flat_members table
-- Stores the many-to-many relationship between users and flats

CREATE TABLE flat_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flat_id UUID REFERENCES flats(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(flat_id, user_id)
);

-- Create indexes for faster lookups
CREATE INDEX idx_flat_members_flat_id ON flat_members(flat_id);
CREATE INDEX idx_flat_members_user_id ON flat_members(user_id);
