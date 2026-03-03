import unittest
from app import create_app
from models import db
import re

class CriticalPathsTestCase(unittest.TestCase):
    def setUp(self):
        import os
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        os.environ['SESSION_SECRET'] = 'test-secret'

        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page_loads(self):
        """1. Chargement de la page d'accueil (Code 200)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DISPARUS.ORG', response.data)

    def test_report_submission(self):
        """2. Soumission d'un signalement valide (Redirection ou Code 200/201)"""
        # We need the CSRF token to submit the form
        response = self.client.get('/signaler')
        self.assertEqual(response.status_code, 200)

        # Extract CSRF token using regex to avoid external dependencies like bs4
        match = re.search(b'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match, "CSRF token non trouve dans la page /signaler")
        csrf_token = match.group(1).decode('utf-8')

        data = {
            'csrf_token': csrf_token,
            'person_type': 'adult',
            'sex': 'male',
            'first_name': 'John',
            'last_name': 'Doe',
            'country': 'France',
            'city': 'Paris',
            'physical_description': 'Test description',
            'clothing': 'Test clothing',
            'disappearance_date': '2023-10-27T10:00',
            'contact_name_0': 'Jane Doe',
            'contact_phone_0': '0123456789',
            'consent': 'on'
        }
        post_response = self.client.post('/signaler', data=data)

        # Check for successful redirection to details page
        self.assertEqual(post_response.status_code, 302)
        self.assertIn('/disparu/', post_response.headers.get('Location'))

    def test_admin_access_without_session(self):
        """3. Tentative d'accès à l'admin sans session (Redirection 302 vers /login)"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.headers.get('Location'))

if __name__ == '__main__':
    unittest.main()
