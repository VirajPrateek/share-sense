-- Add join code and status to groups
-- join_code: 6-char alphanumeric code for inviting members without email
-- status: 'active' or 'archived' for soft-delete/archive

ALTER TABLE groups ADD COLUMN IF NOT EXISTS join_code VARCHAR(8) UNIQUE;
ALTER TABLE groups ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- Generate join codes for existing groups
UPDATE groups SET join_code = UPPER(SUBSTR(MD5(RANDOM()::TEXT), 1, 6)) WHERE join_code IS NULL;

-- Make join_code NOT NULL after backfill
ALTER TABLE groups ALTER COLUMN join_code SET NOT NULL;

CREATE INDEX idx_groups_join_code ON groups(join_code);
CREATE INDEX idx_groups_status ON groups(status);
