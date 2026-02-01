
import unittest
import os
from app import create_app
from models import db, User, Role
from werkzeug.security import generate_password_hash

class TestAdminPages(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'disparus.db')
        os.environ['ADMIN_PASSWORD'] = 'admin_password'
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier testing
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Ensure admin user exists (it should be there from init_db, but let's be safe)
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
             # If role doesn't exist (e.g. fresh in-memory db), create it
             admin_role = Role(name='admin', permissions={'all': True})
             db.session.add(admin_role)
             db.session.commit()

        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(
                username='admin',
                email='admin@disparus.org',
                role_id=admin_role.id,
                is_active=True
            )
            user.set_password('admin_password')
            db.session.add(user)
            db.session.commit()
        else:
             # Ensure password matches
             user.password_hash = generate_password_hash('admin_password')
             db.session.commit()

    def tearDown(self):
        self.ctx.pop()

    def login(self):
        return self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin_password'
        }, follow_redirects=True)

    def test_admin_dashboard(self):
        self.login()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        # Verify the text update
        self.assertIn(b'Disparitions', response.data)
        self.assertIn(b'Derni\xc3\xa8res disparitions', response.data) # Dernières disparitions

    def test_admin_moderation(self):
        self.login()
        response = self.client.get('/admin/moderation')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Disparitions', response.data)

    def test_admin_map(self):
        self.login()
        response = self.client.get('/admin/map')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Disparition', response.data)

    def test_other_pages_load(self):
        self.login()
        pages = [
            '/admin/contributions',
            '/admin/statistics',
            '/admin/users',
            '/admin/roles',
            '/admin/logs',
            '/admin/blocked-attempts',
            '/admin/data',
            '/admin/downloads'
        ]
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200, f"Failed to load {page}")

if __name__ == '__main__':
    unittest.main()
