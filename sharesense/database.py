import psycopg2
import psycopg2.extras
import config


class _PgConn:
    """Wrapper around psycopg2."""
    def __init__(self):
        db_url = config.DATABASE_URL
        if "sslmode" not in db_url:
            sep = "&" if "?" in db_url else "?"
            db_url += sep + "sslmode=require"
        self._conn = psycopg2.connect(db_url)
        self._conn.autocommit = False

    def execute(self, sql, params=None):
        sql = sql.replace("?", "%s")
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    return _PgConn()


def init_db():
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
        CREATE TABLE IF NOT EXISTS groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_by TEXT REFERENCES users(id),
            join_code TEXT UNIQUE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS group_members (
            id TEXT PRIMARY KEY,
            group_id TEXT REFERENCES groups(id) ON DELETE CASCADE,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            joined_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(group_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
            description TEXT NOT NULL,
            payer_id TEXT REFERENCES users(id),
            group_id TEXT REFERENCES groups(id) ON DELETE CASCADE,
            expense_type TEXT NOT NULL CHECK (expense_type IN ('shared', 'personal')),
            category TEXT DEFAULT 'other',
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
            group_id TEXT REFERENCES groups(id) ON DELETE CASCADE,
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
            group_id TEXT REFERENCES groups(id) ON DELETE CASCADE,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP,
            status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
            created_at TIMESTAMP DEFAULT NOW(),
            closed_at TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")
