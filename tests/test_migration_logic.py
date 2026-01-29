
import os
import unittest
from sqlalchemy import text, inspect

# Set dummy env vars BEFORE importing app/init_db to avoid errors
# NOTE: We use in-memory SQLite for testing to ensure isolation and speed.
# This does NOT affect the production environment which uses PostgreSQL.
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test-secret'

from app import create_app
from models import db, Role
import init_db

class TestMigrationLogic(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all() # This creates ALL tables with ALL columns

        # We need to simulate a state where columns are MISSING.
        # So we will drop the table and recreate it with FEWER columns.
        db.session.execute(text("DROP TABLE roles_flask"))

        # Create table with only 'id' and 'name'
        # SQLite syntax
        db.session.execute(text("""
            CREATE TABLE roles_flask (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sync_schema_adds_missing_columns(self):
        """Test that sync_schema_columns adds missing columns to an existing table."""

        inspector = inspect(db.engine)
        columns_before = [c['name'] for c in inspector.get_columns('roles_flask')]
        self.assertIn('name', columns_before)
        self.assertNotIn('display_name', columns_before)
        self.assertNotIn('permissions', columns_before)

        print(f"\nColumns before migration: {columns_before}")

        # Run the migration logic
        # Note: init_db.sync_schema_columns uses the global 'db' which we are using here too
        init_db.sync_schema_columns()

        inspector = inspect(db.engine)
        columns_after = [c['name'] for c in inspector.get_columns('roles_flask')]

        print(f"Columns after migration: {columns_after}")

        # Verify columns were added
        self.assertIn('display_name', columns_after)
        self.assertIn('description', columns_after)
        self.assertIn('permissions', columns_after)
        self.assertIn('is_system', columns_after)

        # Verify we can insert data into new columns
        # This confirms the schema change was successful and valid
        db.session.execute(text("""
            INSERT INTO roles_flask (name, display_name, is_system)
            VALUES ('test_role', 'Test Role', 1)
        """))
        db.session.commit()

        role = Role.query.filter_by(name='test_role').first()
        self.assertIsNotNone(role)
        self.assertEqual(role.display_name, 'Test Role')
        # Check default values if applicable (is_system might have defaulted to False/0 if not provided, but we provided 1)

    def test_sync_schema_idempotency(self):
        """Test that running sync_schema_columns twice doesn't break anything."""
        init_db.sync_schema_columns()
        init_db.sync_schema_columns() # Should be safe

        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('roles_flask')]
        self.assertIn('display_name', columns)

if __name__ == '__main__':
    unittest.main()
