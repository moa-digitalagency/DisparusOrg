import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from services.moderation import ContentModerator
from app import create_app
from models import db

class TestContentModerator(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = self.app.test_request_context()
        self.request_context.push()

        db.create_all()

        self.moderator = ContentModerator()
        # Mock api_key to ensure it tries to call API
        self.moderator.nudity_api_key = "test_key"
        self.moderator.violence_api_key = "test_key"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.request_context.pop()
        self.app_context.pop()

    @patch('requests.post')
    def test_clean_image(self, mock_post):
        # Mock response for nudity: low confidence
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"confidence": 0.1, "description": "Safe"}

        # Mock response for violence: low confidence
        mock_violence_response = MagicMock()
        mock_violence_response.status_code = 200
        mock_violence_response.json.return_value = {"confidence": 0.1, "description": "Safe"}

        # Configure side_effect to return nudity response first, then violence response
        mock_post.side_effect = [mock_nudity_response, mock_violence_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason, log = self.moderator.check_image(file_mock)

        self.assertTrue(is_safe)
        self.assertIsNone(reason)

    @patch('requests.post')
    def test_nudity_detected(self, mock_post):
        # Mock response for nudity: high confidence
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"confidence": 0.9, "description": "Nude"}

        mock_post.side_effect = [mock_nudity_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason, log = self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("pornographique", reason)
        # Verify violence API was NOT called (fail fast)
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    def test_violence_detected(self, mock_post):
        # Mock response for nudity: low confidence
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"confidence": 0.1, "description": "Safe"}

        # Mock response for violence: high confidence
        mock_violence_response = MagicMock()
        mock_violence_response.status_code = 200
        mock_violence_response.json.return_value = {"confidence": 0.9, "description": "Violence"}

        mock_post.side_effect = [mock_nudity_response, mock_violence_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason, log = self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("violent", reason)

    def test_no_api_key(self):
        self.moderator.nudity_api_key = None
        self.moderator.violence_api_key = None
        file_mock = BytesIO(b"fake image data")
        is_safe, reason, log = self.moderator.check_image(file_mock)
        self.assertTrue(is_safe) # Default safe if no key

if __name__ == '__main__':
    unittest.main()
