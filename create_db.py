import sqlite3

conn = sqlite3.connect("complaints.db")
c = conn.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    mobile TEXT PRIMARY KEY
)
""")

# Complaints table
c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    department TEXT,
    status TEXT,
    response TEXT
)
""")

# Optional: Add a sample user
c.execute("INSERT OR IGNORE INTO users (name,mobile) VALUES (?,?)", ("Alice","9876543210"))

conn.commit()
conn.close()
print("Database created successfully!")