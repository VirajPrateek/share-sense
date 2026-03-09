import sqlite3
import config

def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS flats (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_by TEXT REFERENCES users(id),
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS flat_members (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            joined_at TEXT DEFAULT (datetime('now')),
            UNIQUE(flat_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            amount REAL NOT NULL CHECK (amount > 0),
            description TEXT NOT NULL,
            payer_id TEXT REFERENCES users(id),
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            expense_type TEXT NOT NULL CHECK (expense_type IN ('shared', 'personal')),
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expense_shares (
            id TEXT PRIMARY KEY,
            expense_id TEXT REFERENCES expenses(id) ON DELETE CASCADE,
            sharer_id TEXT REFERENCES users(id),
            share_amount REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settlements (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            debtor_id TEXT REFERENCES users(id),
            creditor_id TEXT REFERENCES users(id),
            amount REAL NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed')),
            proposed_by TEXT REFERENCES users(id),
            created_at TEXT DEFAULT (datetime('now')),
            confirmed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS settlement_confirmations (
            id TEXT PRIMARY KEY,
            settlement_id TEXT REFERENCES settlements(id) ON DELETE CASCADE,
            confirmed_by TEXT REFERENCES users(id),
            confirmed_at TEXT DEFAULT (datetime('now')),
            UNIQUE(settlement_id, confirmed_by)
        );

        CREATE TABLE IF NOT EXISTS expense_durations (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            start_date TEXT NOT NULL,
            end_date TEXT,
            status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
            created_at TEXT DEFAULT (datetime('now')),
            closed_at TEXT
        );
    """)
    conn.close()
    print("Database initialized.")
