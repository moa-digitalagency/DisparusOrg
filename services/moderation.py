import os
import requests
from flask import current_app, request
from models import db, ContentModerationLog

class ContentModerator:
    def __init__(self):
        self.nudity_api_key = os.environ.get('NUDITY_DETECTION_API_KEY')
        self.violence_api_key = os.environ.get('VIOLENCE_DETECTION_API_KEY')
        # Fallback to general key if specific ones aren't set
        general_key = os.environ.get('APILAYER_API_KEY')
        if not self.nudity_api_key:
            self.nudity_api_key = general_key
        if not self.violence_api_key:
            self.violence_api_key = general_key

        self.nudity_api_url = "https://api.apilayer.com/nudity_detection/upload"
        self.violence_api_url = "https://api.apilayer.com/violence_detection/upload"

    def _call_api(self, url, api_key, file_content):
        if not api_key:
            current_app.logger.warning(f"API key not found for {url}. Content moderation skipped.")
            return None

        headers = {
            "apikey": api_key
        }

        try:
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

    def _get_location_info(self, ip_address):
        """
        Get location info from IP address using a free service (ip-api.com).
        Note: This is for demonstration/dev purposes. In production, use a paid/reliable service or local DB.
        """
        try:
            # Skip for local loopback
            if ip_address in ['127.0.0.1', '::1']:
                return "Unknown", "Unknown"

            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('country', 'Unknown'), data.get('city', 'Unknown')
        except Exception as e:
            current_app.logger.warning(f"GeoIP lookup failed: {e}")
        return "Unknown", "Unknown"

    def check_image(self, file_storage):
        """
        Checks an image for nudity and violence.
        Returns (is_safe, reason, log_entry)
        is_safe: boolean
        reason: string (if not safe)
        log_entry: ContentModerationLog object (if not safe)
        """
        if not self.nudity_api_key and not self.violence_api_key:
            return True, None, None

        # Read file content
        file_content = file_storage.read()
        # Rewind for subsequent use
        file_storage.seek(0)

        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')[:500]

        # Check Nudity
        if self.nudity_api_key:
            nudity_result = self._call_api(self.nudity_api_url, self.nudity_api_key, file_content)
            # Rewind
            file_storage.seek(0) # Not strictly needed as we passed bytes, but good practice if file_storage was used elsewhere

            if nudity_result:
                # Based on docs/previous code: value 1-5 or confidence score.
                # Assuming 'value' is present and >= 3 is bad, OR 'confidence' > 0.6
                # Let's check keys. If unknown, we might default to safe or log warning.
                # Assuming standard APILayer response structure.
                score = nudity_result.get('value', 0)
                confidence = nudity_result.get('confidence', 0)

                # Heuristic: if value is high or confidence is high
                if score >= 3 or confidence > 0.6:
                    return self._handle_unsafe(ip_address, user_agent, 'nudity', score, nudity_result)

        # Check Violence
        if self.violence_api_key:
            violence_result = self._call_api(self.violence_api_url, self.violence_api_key, file_content)

            if violence_result:
                score = violence_result.get('value', 0)
                confidence = violence_result.get('confidence', 0)

                if score >= 3 or confidence > 0.6:
                    return self._handle_unsafe(ip_address, user_agent, 'violence', score, violence_result)

        return True, None, None

    def _handle_unsafe(self, ip, user_agent, detection_type, score, details):
        country, city = self._get_location_info(ip)

        log = ContentModerationLog(
            ip_address=ip,
            user_agent=user_agent,
            country=country,
            city=city,
            detection_type=detection_type,
            score=float(score),
            details=str(details),
            metadata_json=str(details)
        )

        try:
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to save moderation log: {e}")
            db.session.rollback()

        reason = "L'image contient de la nudité ou du contenu pour adultes." if detection_type == 'nudity' else "L'image contient du contenu violent."
        return False, reason, log

def check_image_content(file_storage):
    """
    Wrapper function to check image content.
    Returns (is_safe, reason, log_entry)
    """
    moderator = ContentModerator()
    return moderator.check_image(file_storage)
