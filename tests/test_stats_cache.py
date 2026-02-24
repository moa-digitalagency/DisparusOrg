import unittest
from unittest.mock import patch
import time
import json
from datetime import datetime
from app import create_app
from models import db, Disparu
import routes.api

class TestStatsCache(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Clear cache before test
        routes.api._STATS_CACHE = None
        routes.api._STATS_CACHE_TIME = 0

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        # Clear cache after test
        routes.api._STATS_CACHE = None
        routes.api._STATS_CACHE_TIME = 0

    def test_stats_caching(self):
        # Initial request
        response = self.client.get('/api/stats')
        data1 = response.get_json()
        self.assertEqual(data1['total'], 0)

        # Add a record
        d = Disparu(
            public_id='CACHE01',
            first_name='Cache',
            last_name='Test',
            person_type='adult',
            status='missing',
            age=30,
            sex='male',
            country='France',
            city='Paris',
            disappearance_date=datetime.now(),
            physical_description='Desc',
            circumstances='Circumstances'
        )
        db.session.add(d)
        db.session.commit()

        # Request again - should be cached (still 0)
        # Note: We don't need to mock time here because it happens immediately
        response = self.client.get('/api/stats')
        data2 = response.get_json()
        self.assertEqual(data2['total'], 0, "Stats should be cached and not reflect the new record yet")

        # Mock time to move forward past TTL (300s)
        # We need to patch time.time in routes.api
        original_time = time.time()
        with patch('routes.api.time.time') as mock_time:
            mock_time.return_value = original_time + 301

            # Request again - should be fresh (now 1)
            response = self.client.get('/api/stats')
            data3 = response.get_json()
            self.assertEqual(data3['total'], 1, "Stats should update after cache expires")

if __name__ == '__main__':
    unittest.main()
