import unittest
import os
import json
from flask import Flask, session
from unittest.mock import patch, MagicMock

# Set env before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test_secret'

try:
    from app import create_app
    from models import db
    from models.settings import SiteSetting, init_default_settings, get_all_settings_dict, invalidate_settings_cache
    from security.rate_limit import rate_limit, get_blocked_ips, get_whitelisted_ips, request_counts
except ImportError:
    pass

class TestRateLimitNew(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        # self.app.config['PROPAGATE_EXCEPTIONS'] = True
        # Let's disable propagation to check 429 status code directly
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            init_default_settings()

            # Create a test route dynamically
            @self.app.route('/test-limit')
            @rate_limit(max_requests=1, window=60)
            def test_limit():
                return "OK"

        request_counts.clear()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        request_counts.clear()

    def test_get_blocked_ips_newlines(self):
        with self.app.app_context():
            s = SiteSetting.query.filter_by(key='blocked_ips').first()
            s.value = "1.1.1.1\n2.2.2.2, 3.3.3.3"
            db.session.commit()
            invalidate_settings_cache()

            ips = get_blocked_ips()
            self.assertIn('1.1.1.1', ips)
            self.assertIn('2.2.2.2', ips)
            self.assertIn('3.3.3.3', ips)

    def test_get_whitelisted_ips_newlines(self):
        with self.app.app_context():
            s = SiteSetting.query.filter_by(key='whitelisted_ips').first()
            s.value = "10.0.0.1\n10.0.0.2"
            db.session.commit()
            invalidate_settings_cache()

            ips = get_whitelisted_ips()
            self.assertIn('10.0.0.1', ips)
            self.assertIn('10.0.0.2', ips)

    def test_admin_bypass(self):
        request_counts.clear()

        res1 = self.client.get('/test-limit')
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.get('/test-limit')
        if res2.status_code != 429:
             print(f"Status: {res2.status_code}")
             print(f"Request counts: {request_counts}")

        self.assertEqual(res2.status_code, 429)

        # 2. Admin user bypasses limit
        with self.client.session_transaction() as sess:
            sess['admin_logged_in'] = True

        res3 = self.client.get('/test-limit')
        self.assertEqual(res3.status_code, 200)

        res4 = self.client.get('/test-limit')
        self.assertEqual(res4.status_code, 200)

    def test_whitelist_bypass(self):
        request_counts.clear()

        with self.app.app_context():
            s = SiteSetting.query.filter_by(key='blocked_ips').first()
            s.value = "127.0.0.1"
            db.session.commit()
            invalidate_settings_cache()

        res = self.client.get('/test-limit')
        self.assertEqual(res.status_code, 403)

        with self.app.app_context():
            s = SiteSetting.query.filter_by(key='whitelisted_ips').first()
            s.value = "127.0.0.1"
            db.session.commit()
            invalidate_settings_cache()

        res = self.client.get('/test-limit')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/test-limit')
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
