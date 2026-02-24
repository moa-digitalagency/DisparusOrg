import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add repo root to path
sys.path.append(os.getcwd())

from services import data_manager, stats_service, export_manager
from models import Disparu

class TestAdminRefactor(unittest.TestCase):

    @patch('services.stats_service.db.session')
    @patch('services.stats_service.Contribution')
    @patch('services.stats_service.Disparu')
    def test_get_dashboard_stats(self, mock_disparu, mock_contribution, mock_session):
        # Mocking the large aggregation query result
        mock_stats_result = MagicMock()
        mock_stats_result.total = 100
        mock_stats_result.missing = 50
        mock_stats_result.found = 40
        mock_stats_result.deceased = 5
        mock_stats_result.flagged = 2
        mock_stats_result.countries = 10

        # Configure the chain: query().one()
        mock_session.query.return_value.one.return_value = mock_stats_result

        # Mock Contribution count
        mock_contribution.query.count.return_value = 200

        # Mock Recent Disparus
        mock_disparu.query.order_by.return_value.limit.return_value.all.return_value = []

        # Mock Map Data
        # query().filter().order_by().limit().all()
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = stats_service.get_dashboard_stats()

        self.assertEqual(result['stats']['total'], 100)
        self.assertEqual(result['stats']['missing'], 50)
        self.assertIn('recent_disparus', result)
        self.assertIn('map_list', result)

    @patch('services.data_manager.db.session')
    @patch('services.data_manager.Disparu')
    def test_restore_from_json_valid(self, mock_disparu_cls, mock_session):
        # Setup
        valid_data = {
            "version": "1.0",
            "disparus": [
                {
                    "public_id": "TEST01",
                    "first_name": "John",
                    "last_name": "Doe",
                    "age": 30,
                    "sex": "male",
                    "person_type": "adult",
                    "country": "France",
                    "city": "Paris",
                    "disappearance_date": "2023-01-01T12:00:00",
                    "physical_description": "Tall",
                    "status": "missing"
                }
            ]
        }
        json_content = json.dumps(valid_data)

        # Mock query for existing IDs (return empty)
        mock_session.query.return_value.filter.return_value.with_entities.return_value.all.return_value = []

        result = data_manager.restore_from_json(json_content)

        self.assertEqual(result['restored'], 1)
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['skipped'], 0)
        # Verify db.session.add was called
        self.assertTrue(mock_session.add.called)

    @patch('services.data_manager.db.session')
    def test_restore_from_json_invalid_missing_field(self, mock_session):
        # Missing 'last_name'
        invalid_data = {
            "disparus": [
                {
                    "public_id": "TEST02",
                    "first_name": "Jane",
                    # "last_name": "Doe",  <-- Missing
                    "age": 25,
                    "sex": "female",
                    "person_type": "adult",
                    "country": "USA",
                    "city": "NY",
                    "disappearance_date": "2023-01-01",
                    "physical_description": "Short",
                    "status": "missing"
                }
            ]
        }
        json_content = json.dumps(invalid_data)

        # Mock query for existing IDs
        mock_session.query.return_value.filter.return_value.with_entities.return_value.all.return_value = []

        result = data_manager.restore_from_json(json_content)

        self.assertEqual(result['restored'], 0)
        self.assertEqual(result['errors'], 1) # Should fail validation
        self.assertEqual(result['skipped'], 0)

    @patch('services.data_manager.db.session')
    def test_restore_from_json_invalid_type(self, mock_session):
        # Age is a string that cannot be converted to int (e.g. "twenty") or just wrong type test
        # Let's use a non-convertible string for age
        invalid_data = {
            "disparus": [
                {
                    "public_id": "TEST03",
                    "first_name": "Bob",
                    "last_name": "Smith",
                    "age": "unknown", # <-- Invalid type for int field
                    "sex": "male",
                    "person_type": "adult",
                    "country": "UK",
                    "city": "London",
                    "disappearance_date": "2023-01-01",
                    "physical_description": "Average",
                    "status": "missing"
                }
            ]
        }
        json_content = json.dumps(invalid_data)

        # Mock query for existing IDs
        mock_session.query.return_value.filter.return_value.with_entities.return_value.all.return_value = []

        result = data_manager.restore_from_json(json_content)

        self.assertEqual(result['restored'], 0)
        self.assertEqual(result['errors'], 1)

    @patch('services.export_manager.Disparu')
    def test_generate_data_json_stream(self, mock_disparu):
        # Mock yield_per
        mock_d1 = MagicMock()
        # _get_disparu_dict accesses many fields.
        for attr in ['public_id', 'first_name', 'last_name', 'age', 'sex', 'person_type',
                     'country', 'city', 'latitude', 'longitude', 'physical_description',
                     'circumstances', 'contacts', 'status', 'created_at', 'disappearance_date']:
            setattr(mock_d1, attr, "mock_val")

        mock_d1.public_id = "P1"
        mock_d1.first_name = "F1"
        # Dates need isoformat() method
        mock_date = MagicMock()
        mock_date.isoformat.return_value = "2023-01-01"
        mock_d1.created_at = mock_date
        mock_d1.disappearance_date = mock_date

        mock_disparu.query.yield_per.return_value = [mock_d1]

        generator = export_manager.generate_data_json_stream()
        output = "".join(list(generator))

        self.assertTrue(output.startswith("["))
        self.assertTrue(output.endswith("]"))
        self.assertIn('"public_id": "P1"', output)

if __name__ == '__main__':
    unittest.main()
