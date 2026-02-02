import unittest
import os
import io
from app import create_app
from models import db, User, Role, Disparu
from datetime import datetime

class TestStatsExport(unittest.TestCase):
    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(basedir, 'instance', 'test_stats.db')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        os.environ['DATABASE_URL'] = 'sqlite:///' + self.db_path
        os.environ['ADMIN_PASSWORD'] = 'admin_password'
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', display_name='Administrator', permissions={'all': True}, menu_access=[])
            db.session.add(admin_role)
            db.session.commit()

        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', email='admin@test.com', role_id=admin_role.id)
            user.set_password('admin_password')
            db.session.add(user)

        # Add some sample data with all required fields
        d1 = Disparu(
            public_id='TEST01',
            first_name='John',
            last_name='Doe',
            person_type='adult',
            status='missing',
            country='Gabon',
            city='Libreville',
            disappearance_date=datetime.now(),
            physical_description='Test description',
            circumstances='Test circumstances',
            age=30,
            sex='male',
            clothing='Test clothing',
            objects='Test objects'
        )
        db.session.add(d1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def login(self):
        return self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin_password'
        }, follow_redirects=True)

    def test_export_stats_pdf(self):
        self.login()
        response = self.client.get('/admin/statistics/export/pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertTrue(len(response.data) > 0)
        self.assertIn(b'%PDF', response.data)

if __name__ == '__main__':
    unittest.main()
