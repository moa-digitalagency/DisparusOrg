import os
import unittest
import json
import io
from datetime import datetime

# Set environment variables before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['ADMIN_USERNAME'] = 'admin'
os.environ['ADMIN_PASSWORD'] = 'password'
os.environ['SESSION_SECRET'] = 'secret'

from app import create_app
from models import db, Disparu

class TestDataRestore(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        # Login as admin
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'password'
        }, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_restore_data(self):
        # 1. Create existing data
        d = Disparu(
            public_id='EXIST1',
            first_name='Existing',
            last_name='User',
            person_type='adult',
            age=30,
            sex='male',
            country='France',
            city='Paris',
            physical_description='Desc',
            disappearance_date=datetime.now(),
            circumstances='Circumstances'
        )
        db.session.add(d)
        db.session.commit()

        # 2. Prepare backup data
        backup_data = {
            'version': '1.0',
            'disparus': [
                {
                    'public_id': 'EXIST1', # Duplicate, should be skipped
                    'first_name': 'Existing',
                    'last_name': 'User',
                    'disappearance_date': datetime.now().isoformat()
                },
                {
                    'public_id': 'NEW1', # New, should be added
                    'first_name': 'New',
                    'last_name': 'User',
                    'person_type': 'adult',
                    'age': 25,
                    'sex': 'female',
                    'country': 'Spain',
                    'city': 'Madrid',
                    'physical_description': 'New Desc',
                    'disappearance_date': datetime.now().isoformat(),
                    'circumstances': 'New Circumstances',
                    'status': 'missing'
                }
            ]
        }

        backup_json = json.dumps(backup_data)
        backup_file = (io.BytesIO(backup_json.encode('utf-8')), 'backup.json')

        # 3. Perform restore
        response = self.client.post('/admin/data/restore', data={
            'backup_file': backup_file
        }, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # 4. Verify results
        all_disparus = Disparu.query.all()
        # Initial 1 + 1 New = 2
        self.assertEqual(len(all_disparus), 2, f"Expected 2 records, found {len(all_disparus)}")

        exist1 = Disparu.query.filter_by(public_id='EXIST1').first()
        self.assertIsNotNone(exist1)
        self.assertEqual(exist1.country, 'France') # Should not be overwritten

        new1 = Disparu.query.filter_by(public_id='NEW1').first()
        self.assertIsNotNone(new1)
        self.assertEqual(new1.country, 'Spain')

    def test_restore_large_batch(self):
        # Test the chunking logic with enough items to trigger it (chunk_size=1000)
        # We'll use 1500 items total: 500 existing, 1000 new
        # So we have 500 existing records in DB.
        # Backup has: 500 existing + 1000 new.

        # Create 500 existing in DB
        for i in range(500):
            d = Disparu(
                public_id=f'EXIST{i}',
                first_name=f'F{i}',
                last_name=f'L{i}',
                person_type='adult',
                age=20,
                sex='m',
                country='C',
                city='C',
                physical_description='D',
                disappearance_date=datetime.now(),
                circumstances='C'
            )
            db.session.add(d)
        db.session.commit()

        # Create backup with 500 existing + 1000 new
        disparus_list = []
        for i in range(500):
             disparus_list.append({
                'public_id': f'EXIST{i}',
                'disappearance_date': datetime.now().isoformat()
            })
        for i in range(1000):
             disparus_list.append({
                'public_id': f'NEW{i}',
                'first_name': f'NF{i}',
                'last_name': f'NL{i}',
                'person_type': 'adult',
                'age': 20,
                'sex': 'f',
                'country': 'NC',
                'city': 'NC',
                'physical_description': 'ND',
                'disappearance_date': datetime.now().isoformat(),
                'circumstances': 'NC',
                'status': 'missing'
            })

        backup_data = {'version': '1.0', 'disparus': disparus_list}
        backup_json = json.dumps(backup_data)
        backup_file = (io.BytesIO(backup_json.encode('utf-8')), 'backup_large.json')

        response = self.client.post('/admin/data/restore', data={
            'backup_file': backup_file
        }, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        total_count = Disparu.query.count()
        # 500 existing + 1000 new = 1500
        self.assertEqual(total_count, 1500, f"Expected 1500 records, found {total_count}")

if __name__ == '__main__':
    unittest.main()
