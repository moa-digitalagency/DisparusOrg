import os
import requests
from flask import current_app

class ContentModerator:
    def __init__(self):
        self.api_key = os.environ.get('APILAYER_API_KEY')
        self.nudity_api_url = "https://api.apilayer.com/nudity_detection/upload"
        self.violence_api_url = "https://api.apilayer.com/violence_detection/upload"

    def _call_api(self, url, file_content):
        if not self.api_key:
            # If no API key is configured, we default to allowing the content
            # requesting the user to configure it.
            # In production, this should probably log a warning.
            current_app.logger.warning("APILayer API key not found. Content moderation skipped.")
            return None

        headers = {
            "apikey": self.api_key
        }

        try:
            # The API expects the file in the 'image' field
            files = {'image': file_content}
            response = requests.post(url, headers=headers, files=files, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Moderation API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Moderation API exception: {str(e)}")
            return None

    def check_image(self, file_storage):
        """
        Checks an image for nudity and violence.
        Returns (is_safe, reason)
        is_safe: boolean
        reason: string (if not safe)
        """
        if not self.api_key:
            return True, None

        # Read file content
        file_content = file_storage.read()
        # Rewind for subsequent use
        file_storage.seek(0)

        # Check Nudity
        nudity_result = self._call_api(self.nudity_api_url, file_content)
        # Rewind not needed as we passed bytes, but _call_api consumes bytes?
        # requests.post files argument handles bytes directly.

        if nudity_result:
            # Based on docs: value 1-5.
            # We reject if value >= 3 (Possible/Likely/Most Likely)
            # Adjust threshold as needed.
            score = nudity_result.get('value', 0)
            if score >= 3:
                return False, "L'image contient de la nudité ou du contenu pour adultes."

        # Check Violence
        violence_result = self._call_api(self.violence_api_url, file_content)

        if violence_result:
            # Based on docs: value 1-5.
            score = violence_result.get('value', 0)
            if score >= 3:
                return False, "L'image contient du contenu violent."

        return True, None

def check_image_content(file_storage):
    """
    Wrapper function to check image content.
    """
    moderator = ContentModerator()
    return moderator.check_image(file_storage)
