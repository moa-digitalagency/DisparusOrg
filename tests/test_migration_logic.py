
import os
import sys
import sqlite3
from sqlalchemy import text

# Setup environment for testing
test_db_path = os.path.abspath("test_migration.db")
test_db_uri = f"sqlite:///{test_db_path}"
os.environ['DATABASE_URL'] = test_db_uri
os.environ['SESSION_SECRET'] = 'test-secret'

# Cleanup previous run
if os.path.exists("test_migration.db"):
    os.remove("test_migration.db")

# Add root to path
sys.path.append(os.getcwd())

# Import AFTER env vars are set
import init_db
from models import db

def setup_broken_schema():
    """Manually create a table with missing columns"""
    print(f"Setting up broken schema in {test_db_path}...")
    conn = sqlite3.connect("test_migration.db")
    cursor = conn.cursor()

    # Create 'roles_flask' table with ONLY id and name
    cursor.execute("""
        CREATE TABLE roles_flask (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Create 'users_flask' table with just id and username
    cursor.execute("""
        CREATE TABLE users_flask (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) NOT NULL UNIQUE
        );
    """)

    conn.commit()
    conn.close()

def test_migration():
    setup_broken_schema()

    print("Running migration logic...")
    # Run the migration function inside the app context
    with init_db.app.app_context():
        # Verify initial state (broken)
        with sqlite3.connect("test_migration.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(roles_flask)")
            columns = [info[1] for info in cursor.fetchall()]
            print(f"Initial roles_flask columns: {columns}")
            assert 'display_name' not in columns

        # Run the sync
        init_db.sync_schema_columns()

        # Verify final state
        with sqlite3.connect("test_migration.db") as conn:
            cursor = conn.cursor()

            # Check Role table
            cursor.execute("PRAGMA table_info(roles_flask)")
            role_columns = [info[1] for info in cursor.fetchall()]
            print(f"Final roles_flask columns: {role_columns}")

            missing_role_cols = ['display_name', 'description', 'permissions', 'menu_access', 'is_system']
            for col in missing_role_cols:
                if col not in role_columns:
                    print(f"FAILED: Column 'roles_flask.{col}' was not added.")
                    sys.exit(1)

            # Check User table
            cursor.execute("PRAGMA table_info(users_flask)")
            user_columns = [info[1] for info in cursor.fetchall()]
            print(f"Final users_flask columns: {user_columns}")

            if 'email' not in user_columns:
                 print(f"FAILED: Column 'users_flask.email' was not added.")
                 sys.exit(1)

    print("\nSUCCESS: Migration logic correctly added missing columns!")

if __name__ == "__main__":
    try:
        test_migration()
    finally:
        # Cleanup
        if os.path.exists("test_migration.db"):
            os.remove("test_migration.db")
