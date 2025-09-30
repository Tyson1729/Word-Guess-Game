import sqlite3

# Users and Admins Database
conn = sqlite3.connect("database.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    remaining_attempts INTEGER NOT NULL DEFAULT 3,
    last_played_date TEXT
)
""")
conn.commit()

# Words Database
c.execute("""
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL
)
""")

# Insert 20 sample words
c.execute("SELECT COUNT(*) FROM words")
if c.fetchone()[0] == 0:
    sample_words = [
        "APPLE", "BRAIN", "CRANE", "DELTA", "EAGLE", "FROST", "GRAPE", "HONEY",
        "IGLOO", "JOKER", "KNIFE", "LEMON", "MANGO", "NINJA", "OPERA", "PLANT",
        "MONEY", "SILLY", "SUGAR", "TIGER"
    ]
    c.executemany("INSERT INTO words (word) VALUES (?)", [(w,) for w in sample_words])
    conn.commit()

# Activities Database
c.execute("""
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    guessed_word TEXT NOT NULL,
    correct_word TEXT NOT NULL,
    date TEXT NOT NULL
)
""")
conn.commit()
conn.close()