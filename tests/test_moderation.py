import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO
import asyncio
from services.moderation import ContentModerator
from app import create_app
from models import db

class TestContentModerator(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
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
        # Also mock geo api key for log saving
        self.moderator.geo_api_key = "test_key"

    async def asyncTearDown(self):
        db.session.remove()
        db.drop_all()
        self.request_context.pop()
        self.app_context.pop()

    @patch('aiohttp.ClientSession')
    async def test_clean_image(self, mock_session_cls):
        # Setup mocks
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        async def session_enter(*args, **kwargs): return mock_session
        mock_session.__aenter__.side_effect = session_enter
        mock_session.__aexit__.return_value = None

        mock_post_cm = MagicMock()
        mock_session.post.return_value = mock_post_cm

        # Responses
        nudity_response = AsyncMock()
        nudity_response.status = 200
        nudity_response.json.return_value = {"confidence": 0.1, "description": "Safe"}

        violence_response = AsyncMock()
        violence_response.status = 200
        violence_response.json.return_value = {"confidence": 0.1, "description": "Safe"}

        # Side effect for post context manager enter
        # Note: check_image calls post 2 times.
        responses = [nudity_response, violence_response]
        async def post_enter(*args, **kwargs):
            if responses:
                return responses.pop(0)
            return MagicMock()

        mock_post_cm.__aenter__.side_effect = post_enter
        mock_post_cm.__aexit__.return_value = None

        file_mock = BytesIO(b"fake image data")
        is_safe, reason, log = await self.moderator.check_image(file_mock)

        self.assertTrue(is_safe)
        self.assertIsNone(reason)

    @patch('aiohttp.ClientSession')
    async def test_nudity_detected(self, mock_session_cls):
        # Setup mocks
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        async def session_enter(*args, **kwargs): return mock_session
        mock_session.__aenter__.side_effect = session_enter
        mock_session.__aexit__.return_value = None

        mock_post_cm = MagicMock()
        mock_session.post.return_value = mock_post_cm
        mock_get_cm = MagicMock() # For geo info
        mock_session.get.return_value = mock_get_cm

        # Responses
        nudity_response = AsyncMock()
        nudity_response.status = 200
        nudity_response.json.return_value = {"confidence": 0.9, "description": "Nude"}

        geo_response = AsyncMock()
        geo_response.status = 200
        geo_response.json.return_value = {"country_name": "Test", "city": "TestCity"}

        # post call for nudity
        async def post_enter(*args, **kwargs):
            return nudity_response
        mock_post_cm.__aenter__.side_effect = post_enter
        mock_post_cm.__aexit__.return_value = None

        # get call for geo
        async def get_enter(*args, **kwargs):
            return geo_response
        mock_get_cm.__aenter__.side_effect = get_enter
        mock_get_cm.__aexit__.return_value = None

        file_mock = BytesIO(b"fake image data")
        is_safe, reason, log = await self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("pornographique", reason)
        # Verify post called at least once
        self.assertTrue(mock_session.post.called)

    @patch('aiohttp.ClientSession')
    async def test_violence_detected(self, mock_session_cls):
        # Setup mocks
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        async def session_enter(*args, **kwargs): return mock_session
        mock_session.__aenter__.side_effect = session_enter
        mock_session.__aexit__.return_value = None

        mock_post_cm = MagicMock()
        mock_session.post.return_value = mock_post_cm
        mock_get_cm = MagicMock()
        mock_session.get.return_value = mock_get_cm

        # Responses
        nudity_response = AsyncMock()
        nudity_response.status = 200
        nudity_response.json.return_value = {"confidence": 0.1}

        violence_response = AsyncMock()
        violence_response.status = 200
        violence_response.json.return_value = {"confidence": 0.9, "description": "Violence"}

        geo_response = AsyncMock()
        geo_response.status = 200
        geo_response.json.return_value = {"country_name": "Test", "city": "TestCity"}

        responses = [nudity_response, violence_response]
        async def post_enter(*args, **kwargs):
            if responses:
                return responses.pop(0)
            return MagicMock()

        mock_post_cm.__aenter__.side_effect = post_enter
        mock_post_cm.__aexit__.return_value = None

        async def get_enter(*args, **kwargs):
            return geo_response
        mock_get_cm.__aenter__.side_effect = get_enter
        mock_get_cm.__aexit__.return_value = None

        file_mock = BytesIO(b"fake image data")
        is_safe, reason, log = await self.moderator.check_image(file_mock)

        self.assertFalse(is_safe)
        self.assertIn("violent", reason)

    async def test_no_api_key(self):
        self.moderator.nudity_api_key = None
        self.moderator.violence_api_key = None
        file_mock = BytesIO(b"fake image data")
        is_safe, reason, log = await self.moderator.check_image(file_mock)
        self.assertTrue(is_safe) # Default safe if no key

if __name__ == '__main__':
    unittest.main()
