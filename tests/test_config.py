import unittest
import os
from unittest.mock import patch
from app import create_app
from config import Config, DevelopmentConfig, ProductionConfig

class TestConfig(unittest.TestCase):

    def setUp(self):
        # Patch the configuration classes to ensure DATABASE_URL is set
        # because the class attributes are evaluated at import time.
        self.original_db_uri = Config.SQLALCHEMY_DATABASE_URI
        Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        DevelopmentConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        ProductionConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    def tearDown(self):
        # Restore original values
        Config.SQLALCHEMY_DATABASE_URI = self.original_db_uri
        DevelopmentConfig.SQLALCHEMY_DATABASE_URI = self.original_db_uri
        ProductionConfig.SQLALCHEMY_DATABASE_URI = self.original_db_uri

    def test_production_missing_secret_key(self):
        """Test that production fails without SECRET_KEY"""
        # Patch SECRET_KEY to None on ProductionConfig to simulate missing env var at import time
        with patch.object(ProductionConfig, 'SECRET_KEY', None):
            with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
                if 'SESSION_SECRET' in os.environ:
                    del os.environ['SESSION_SECRET']

                with self.assertRaises(ValueError) as cm:
                    create_app('production')

                self.assertIn("SESSION_SECRET environment variable is required", str(cm.exception))

    def test_development_fallback_key(self):
        """Test that development uses a stable fallback key"""
        # Patch SECRET_KEY to dev-fallback-key if needed (though it defaults there)
        with patch.object(DevelopmentConfig, 'SECRET_KEY', 'dev-fallback-key'):
            with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
                if 'SESSION_SECRET' in os.environ:
                    del os.environ['SESSION_SECRET']

                app1 = create_app('development')
                key1 = app1.config['SECRET_KEY']

                app2 = create_app('development')
                key2 = app2.config['SECRET_KEY']

                self.assertEqual(key1, 'dev-fallback-key')
                self.assertEqual(key1, key2)

    def test_security_headers_dev(self):
        """Test cookie security settings in development"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            app = create_app('development')
            self.assertTrue(app.config['SESSION_COOKIE_HTTPONLY'])
            self.assertEqual(app.config['SESSION_COOKIE_SAMESITE'], 'Lax')
            # Should be False in Dev
            self.assertFalse(app.config['SESSION_COOKIE_SECURE'])

    def test_security_headers_prod(self):
        """Test cookie security settings in production"""
        # Patch SECRET_KEY so validation passes
        with patch.object(ProductionConfig, 'SECRET_KEY', 'test-prod-key'):
            with patch.dict(os.environ, {'FLASK_ENV': 'production', 'SESSION_SECRET': 'test-prod-key'}):
                app = create_app('production')
                self.assertTrue(app.config['SESSION_COOKIE_HTTPONLY'])
                self.assertEqual(app.config['SESSION_COOKIE_SAMESITE'], 'Lax')
                # Should be True in Prod
                self.assertTrue(app.config['SESSION_COOKIE_SECURE'])

if __name__ == '__main__':
    unittest.main()
