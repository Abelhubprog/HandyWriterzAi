"""Check the created database tables."""
import sqlite3

conn = sqlite3.connect('handywriterz.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Tables created in the database:")
print("=" * 40)
for table in tables:
    if not table[0].startswith('sqlite_'):  # Skip SQLite internal tables
        print(f"  ✓ {table[0]}")

# Count tables
non_system_tables = [t for t in tables if not t[0].startswith('sqlite_')]
print(f"\nTotal tables: {len(non_system_tables)}")

conn.close()