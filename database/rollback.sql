-- Sharesense Database Schema Rollback
-- This script drops all tables and functions in reverse order of dependencies

-- Drop triggers first
DROP TRIGGER IF EXISTS update_expenses_updated_at ON expenses;
DROP TRIGGER IF EXISTS update_flats_updated_at ON flats;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS expense_durations CASCADE;
DROP TABLE IF EXISTS settlement_confirmations CASCADE;
DROP TABLE IF EXISTS settlements CASCADE;
DROP TABLE IF EXISTS expense_shares CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS flat_members CASCADE;
DROP TABLE IF EXISTS flats CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Note: This script uses CASCADE to automatically drop dependent objects
-- Use with caution in production environments
