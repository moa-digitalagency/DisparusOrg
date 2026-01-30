import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from services.moderation import ContentModerator

class TestContentModerator(unittest.TestCase):

    def setUp(self):
        self.moderator = ContentModerator()
        # Mock api_key to ensure it tries to call API
        self.moderator.api_key = "test_key"

    @patch('requests.post')
    def test_clean_image(self, mock_post):
        # Mock response for nudity: value 1 (safe)
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"value": 1, "description": "Safe"}

        # Mock response for violence: value 1 (safe)
        mock_violence_response = MagicMock()
        mock_violence_response.status_code = 200
        mock_violence_response.json.return_value = {"value": 1, "description": "Safe"}

        # Configure side_effect to return nudity response first, then violence response
        mock_post.side_effect = [mock_nudity_response, mock_violence_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason = self.moderator.check_image(file_mock)

        self.assertTrue(is_safe)
        self.assertIsNone(reason)

    @patch('requests.post')
    def test_nudity_detected(self, mock_post):
        # Mock response for nudity: value 5 (unsafe)
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"value": 5, "description": "Nude"}

        mock_post.side_effect = [mock_nudity_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason = self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("nudité", reason)
        # Verify violence API was NOT called (fail fast)
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    def test_violence_detected(self, mock_post):
        # Mock response for nudity: value 1 (safe)
        mock_nudity_response = MagicMock()
        mock_nudity_response.status_code = 200
        mock_nudity_response.json.return_value = {"value": 1, "description": "Safe"}

        # Mock response for violence: value 5 (unsafe)
        mock_violence_response = MagicMock()
        mock_violence_response.status_code = 200
        mock_violence_response.json.return_value = {"value": 5, "description": "Violence"}

        mock_post.side_effect = [mock_nudity_response, mock_violence_response]

        file_mock = BytesIO(b"fake image data")

        is_safe, reason = self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("violent", reason)

    def test_no_api_key(self):
        self.moderator.api_key = None
        file_mock = BytesIO(b"fake image data")
        is_safe, reason = self.moderator.check_image(file_mock)
        self.assertTrue(is_safe) # Default safe if no key

if __name__ == '__main__':
    unittest.main()
