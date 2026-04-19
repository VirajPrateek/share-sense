-- Migration 014: Enable RLS on list_items table
--
-- list_items was created after migration 012 which enabled RLS on all
-- tables that existed at the time. This migration covers the gap.
--
-- Same pattern as 012: RLS enabled, no policies for anon/authenticated
-- roles → implicit deny for PostgREST. Our postgres superuser bypasses RLS.

ALTER TABLE list_items ENABLE ROW LEVEL SECURITY;
