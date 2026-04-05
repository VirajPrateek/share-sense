-- Rename flats to groups for generic group-based expense splitting
-- This is a cosmetic rename — no logic changes

ALTER TABLE flats RENAME TO groups;
ALTER TABLE flat_members RENAME TO group_members;

-- Rename columns referencing flats
ALTER TABLE group_members RENAME COLUMN flat_id TO group_id;
ALTER TABLE expenses RENAME COLUMN flat_id TO group_id;
ALTER TABLE settlements RENAME COLUMN flat_id TO group_id;
ALTER TABLE expense_durations RENAME COLUMN flat_id TO group_id;

-- Rename indexes (drop old, create new)
DROP INDEX IF EXISTS idx_flats_created_by;
CREATE INDEX idx_groups_created_by ON groups(created_by);

DROP INDEX IF EXISTS idx_flat_members_flat_id;
DROP INDEX IF EXISTS idx_flat_members_user_id;
CREATE INDEX idx_group_members_group_id ON group_members(group_id);
CREATE INDEX idx_group_members_user_id ON group_members(user_id);

DROP INDEX IF EXISTS idx_expenses_flat_id;
CREATE INDEX idx_expenses_group_id ON expenses(group_id);

DROP INDEX IF EXISTS idx_settlements_flat_id;
CREATE INDEX idx_settlements_group_id ON settlements(group_id);

DROP INDEX IF EXISTS idx_expense_durations_flat_id;
CREATE INDEX idx_expense_durations_group_id ON expense_durations(group_id);
