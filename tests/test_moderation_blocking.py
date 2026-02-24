import unittest
import time
import asyncio
import os
import threading
from unittest.mock import MagicMock, patch, AsyncMock
from services.moderation import ContentModerator
from flask import Flask, request

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['NUDITY_DETECTION_API_KEY'] = 'fake_key'

class TestModerationBlocking(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = Flask(__name__)
        self.ctx = self.app.app_context()
        self.ctx.push()

    async def asyncTearDown(self):
        self.ctx.pop()

    async def test_check_image_blocking_read(self):
        mock_file = MagicMock()
        def slow_read():
            print("DEBUG: Entering slow_read")
            time.sleep(0.5)
            print("DEBUG: Exiting slow_read")
            return b"fake content"
        mock_file.read.side_effect = slow_read
        mock_file.seek.return_value = None

        moderator = ContentModerator()
        moderator.nudity_api_key = 'fake_key'

        async def background():
            print("DEBUG: Starting background task")
            t0 = time.time()
            await asyncio.sleep(0.1)
            t1 = time.time()
            print(f"DEBUG: Finished background task in {t1-t0}s")
            return t1 - t0

        with self.app.test_request_context():
            task = asyncio.create_task(background())

            # Use AsyncMock for async method
            with patch.object(moderator, '_call_api', new_callable=AsyncMock) as mock_api:
                 mock_api.return_value = {'safe': True} # Return dict directly

                 print("DEBUG: Calling check_image")
                 await moderator.check_image(mock_file)
                 print("DEBUG: Finished check_image")

            bg_duration = await task

        # If optimized, bg_duration should be around 0.1s (because read runs in thread)
        # If NOT optimized, bg_duration would be > 0.5s

        if bg_duration > 0.4:
            print("BLOCKING DETECTED")
            self.fail("check_image blocked the event loop")
        else:
            print("NON-BLOCKING")
