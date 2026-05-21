import sqlite3

DATABASE = "loyalty.db"

def init():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT UNIQUE NOT NULL,

            visits INTEGER DEFAULT 0,

            reward TEXT DEFAULT '',

            pending_visit INTEGER DEFAULT 0,

            last_scan TEXT DEFAULT '',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS visit_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            visit_date TEXT,

            approved INTEGER DEFAULT 0,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reward_claims (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            reward TEXT,

            claimed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()

    print("Database initialized successfully.")

if __name__ == "__main__":
    init()