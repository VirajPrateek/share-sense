-- Sharesense Database Schema Rollback
-- Drops all tables and functions in reverse order of dependencies
-- Use with caution in production environments

DROP TRIGGER IF EXISTS update_expenses_updated_at ON expenses;
DROP TRIGGER IF EXISTS update_groups_updated_at ON groups;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

DROP TABLE IF EXISTS expense_durations CASCADE;
DROP TABLE IF EXISTS settlement_confirmations CASCADE;
DROP TABLE IF EXISTS settlements CASCADE;
DROP TABLE IF EXISTS expense_shares CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS group_members CASCADE;
DROP TABLE IF EXISTS groups CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP FUNCTION IF EXISTS update_updated_at_column();
