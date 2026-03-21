import sqlite3
import config

_use_postgres = bool(config.DATABASE_URL)

if _use_postgres:
    import psycopg2
    import psycopg2.extras


class _SqliteConn:
    """Wrapper around sqlite3 to match the interface we use."""
    def __init__(self):
        self._conn = sqlite3.connect(config.DATABASE_PATH)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql, params=None):
        return self._conn.execute(sql, params or ())

    def executescript(self, sql):
        self._conn.executescript(sql)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def fetchone(self, sql, params=None):
        return self._conn.execute(sql, params or ()).fetchone()

    def fetchall(self, sql, params=None):
        return self._conn.execute(sql, params or ()).fetchall()


class _PgConn:
    """Wrapper around psycopg2 to match the same interface."""
    def __init__(self):
        db_url = config.DATABASE_URL
        # Supabase requires SSL
        if "sslmode" not in db_url:
            sep = "&" if "?" in db_url else "?"
            db_url += sep + "sslmode=require"
        self._conn = psycopg2.connect(db_url)
        self._conn.autocommit = False

    def execute(self, sql, params=None):
        sql = _pg_rewrite(sql)
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def _pg_rewrite(sql):
    """Convert SQLite-style ? placeholders to Postgres %s."""
    return sql.replace("?", "%s")


def get_db():
    if _use_postgres:
        return _PgConn()
    return _SqliteConn()


def init_db():
    if _use_postgres:
        _init_postgres()
    else:
        _init_sqlite()


def _init_sqlite():
    conn = get_db()
    conn._conn.executescript("""
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
    print("SQLite database initialized.")


def _init_postgres():
    conn = get_db()
    cur = conn._conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS flats (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_by TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS flat_members (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            joined_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(flat_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
            description TEXT NOT NULL,
            payer_id TEXT REFERENCES users(id),
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            expense_type TEXT NOT NULL CHECK (expense_type IN ('shared', 'personal')),
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS expense_shares (
            id TEXT PRIMARY KEY,
            expense_id TEXT REFERENCES expenses(id) ON DELETE CASCADE,
            sharer_id TEXT REFERENCES users(id),
            share_amount NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS settlements (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            debtor_id TEXT REFERENCES users(id),
            creditor_id TEXT REFERENCES users(id),
            amount NUMERIC(10,2) NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed')),
            proposed_by TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT NOW(),
            confirmed_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settlement_confirmations (
            id TEXT PRIMARY KEY,
            settlement_id TEXT REFERENCES settlements(id) ON DELETE CASCADE,
            confirmed_by TEXT REFERENCES users(id),
            confirmed_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(settlement_id, confirmed_by)
        );
        CREATE TABLE IF NOT EXISTS expense_durations (
            id TEXT PRIMARY KEY,
            flat_id TEXT REFERENCES flats(id) ON DELETE CASCADE,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP,
            status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
            created_at TIMESTAMP DEFAULT NOW(),
            closed_at TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("Postgres database initialized.")
