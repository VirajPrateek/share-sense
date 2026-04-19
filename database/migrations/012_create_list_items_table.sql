-- Create list_items table for shared group shopping/to-do lists
-- Supports offline-first: items can be created offline and synced later

CREATE TABLE list_items (
  id TEXT PRIMARY KEY,
  group_id TEXT REFERENCES groups(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  is_done BOOLEAN DEFAULT FALSE,
  created_by TEXT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_list_items_group_id ON list_items(group_id);
CREATE INDEX idx_list_items_created_by ON list_items(created_by);
