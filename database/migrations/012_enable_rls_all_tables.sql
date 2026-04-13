-- Migration 012: Enable Row-Level Security on all tables
-- 
-- Our app connects directly to Postgres as the 'postgres' superuser,
-- which bypasses RLS. This migration locks down the PostgREST/public API
-- that Supabase exposes automatically, preventing unauthorized access
-- via the Supabase client URL.
--
-- Policy: deny all access through the anon and authenticated Supabase roles
-- (since we don't use PostgREST at all — our backend handles auth via JWT).

-- ============================================================================
-- ENABLE RLS
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE settlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE settlement_confirmations ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_durations ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES
-- ============================================================================
-- With RLS enabled and NO policies defined for the 'anon' and 'authenticated'
-- roles, Supabase PostgREST requests are denied by default (implicit deny).
--
-- The 'postgres' superuser role used by our backend bypasses RLS entirely,
-- so our app continues to work without any changes.
--
-- If you ever need PostgREST access in the future, add explicit policies here.
