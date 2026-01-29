import unittest
import os
from sqlalchemy import text, inspect
from app import create_app
from models import db, Role
from init_db import sync_schema_columns

class TestMigrationLogic(unittest.TestCase):

    def setUp(self):
        # Configure app for testing with in-memory SQLite
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Ensure clean slate
        db.drop_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sync_schema_columns_adds_missing_columns(self):
        """
        Test that sync_schema_columns correctly adds missing columns.
        """
        table_name = Role.__tablename__

        # Create table with missing columns
        db.session.execute(text(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """))
        db.session.commit()

        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns(table_name)]
        self.assertNotIn('description', columns)

        # Run migration
        sync_schema_columns()

        # Verify columns added
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns(table_name)]
        self.assertIn('description', columns)

    def test_sync_schema_data_preservation(self):
        """
        Test that existing data is preserved during migration.
        """
        table_name = Role.__tablename__

        # Create table with missing columns
        db.session.execute(text(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """))

        # Insert data
        db.session.execute(text(f"INSERT INTO {table_name} (id, name) VALUES (1, 'test_role')"))
        db.session.commit()

        # Verify data exists
        result = db.session.execute(text(f"SELECT * FROM {table_name} WHERE id=1")).fetchone()
        self.assertIsNotNone(result)

        # Run migration
        sync_schema_columns()

        # Verify data still exists
        result = db.session.execute(text(f"SELECT * FROM {table_name} WHERE id=1")).fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'test_role')

        # Verify new columns have default values (or null depending on logic)
        # description is nullable, so it should be None (NULL)
        result = db.session.execute(text(f"SELECT description FROM {table_name} WHERE id=1")).fetchone()
        self.assertIsNone(result.description)

        # display_name is NOT NULL, so it should have a default value (e.g., '')
        result = db.session.execute(text(f"SELECT display_name FROM {table_name} WHERE id=1")).fetchone()
        self.assertEqual(result.display_name, '')

    def test_sync_schema_idempotency(self):
        """
        Test that running migration multiple times is safe.
        """
        table_name = Role.__tablename__

        # Create table with missing columns
        db.session.execute(text(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """))
        db.session.commit()

        # Run migration once
        sync_schema_columns()

        inspector = inspect(db.engine)
        cols_run_1 = [c['name'] for c in inspector.get_columns(table_name)]

        # Run migration again
        try:
            sync_schema_columns()
        except Exception as e:
            self.fail(f"Second migration run raised exception: {e}")

        inspector = inspect(db.engine)
        cols_run_2 = [c['name'] for c in inspector.get_columns(table_name)]

        self.assertEqual(cols_run_1, cols_run_2)

if __name__ == "__main__":
    unittest.main()
