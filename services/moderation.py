import os
import requests
import json
from flask import current_app, request
from models import db, ContentModerationLog

class ContentModerator:
    def __init__(self):
        self.nudity_api_key = os.environ.get('NUDITY_DETECTION_API_KEY')
        self.violence_api_key = os.environ.get('VIOLENCE_DETECTION_API_KEY')
        self.geo_api_key = os.environ.get('GEO_API_KEY')

        self.nudity_api_url = "https://api.apilayer.com/nudity_detection/upload"
        self.violence_api_url = "https://api.apilayer.com/violence_detection/upload"
        self.geo_api_url = "https://api.apilayer.com/geo/ip"

    def _call_api(self, url, api_key, file_content):
        if not api_key:
            current_app.logger.warning(f"API key not found for {url}. Content moderation skipped.")
            return None

        headers = {
            "apikey": api_key
        }

        try:
            files = {'image': file_content}
            # Timeout increased slightly for larger images
            response = requests.post(url, headers=headers, files=files, timeout=15)

            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Moderation API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Moderation API exception: {str(e)}")
            return None

    def get_location_info(self, ip_address):
        """
        Get location info from IP address using APILayer Geo API.
        Returns (country, city)
        """
        # Skip for local loopback or private IPs if desired, but for now we try
        if ip_address in ['127.0.0.1', '::1', 'localhost']:
             # Try to get real IP if behind proxy, though usually handled by request.remote_addr setup
             return "Localhost", "Localhost"

        if not self.geo_api_key:
            current_app.logger.warning("GEO_API_KEY not set. Skipping location lookup.")
            return "Unknown", "Unknown"

        try:
            headers = {"apikey": self.geo_api_key}
            # Geo API expects 'ip' query parameter
            url = f"{self.geo_api_url}?ip={ip_address}"

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                # APILayer Geo API response structure:
                # { "city": "...", "country_name": "...", ... }
                country = data.get('country_name', 'Unknown')
                city = data.get('city', 'Unknown')
                return country, city
            else:
                 current_app.logger.warning(f"Geo API error: {response.status_code} - {response.text}")

        except Exception as e:
            current_app.logger.warning(f"GeoIP lookup failed: {e}")

        return "Unknown", "Unknown"

    def check_image(self, file_storage):
        """
        Checks an image for nudity and violence.
        Returns (is_safe, reason, log_entry)
        """
        # If no keys are configured, we default to safe to avoid blocking legit users due to config error
        # unless strict mode is required. Here we allow.
        if not self.nudity_api_key and not self.violence_api_key:
            return True, None, None

        # Read file content
        file_content = file_storage.read()
        # Rewind for subsequent use
        file_storage.seek(0)

        ip_address = request.remote_addr
        # Handle proxy headers if configured (e.g. X-Forwarded-For) - optional but good for VPS
        if request.headers.getlist("X-Forwarded-For"):
             ip_address = request.headers.getlist("X-Forwarded-For")[0]

        user_agent = request.headers.get('User-Agent', '')[:500]

        # Check Nudity
        if self.nudity_api_key:
            nudity_result = self._call_api(self.nudity_api_url, self.nudity_api_key, file_content)
            # Rewind
            file_storage.seek(0)

            if nudity_result:
                # APILayer Nudity often returns 'confidence' (0-1) or 'value'.
                # We check for high confidence.
                # Example response: {"confidence": 0.9, "safe": 0.1, ...} or similar depending on exact endpoint version
                # Let's handle generic 'confidence' or specific fields.

                # Assuming standard response where high confidence = unsafe
                confidence = nudity_result.get('confidence', 0)

                # If confidence > 60% it is likely nudity
                if confidence > 0.6:
                    return self._handle_unsafe(ip_address, user_agent, 'nudity', confidence, nudity_result)

        # Check Violence
        if self.violence_api_key:
            violence_result = self._call_api(self.violence_api_url, self.violence_api_key, file_content)

            if violence_result:
                # Violence API usually returns similar structure
                confidence = violence_result.get('confidence', 0)

                if confidence > 0.6:
                     return self._handle_unsafe(ip_address, user_agent, 'violence', confidence, violence_result)

        return True, None, None

    def _handle_unsafe(self, ip, user_agent, detection_type, score, details):
        country, city = self.get_location_info(ip)

        log = ContentModerationLog(
            ip_address=ip,
            user_agent=user_agent,
            country=country,
            city=city,
            detection_type=detection_type,
            score=float(score),
            details=json.dumps(details), # Store as string
            metadata_json=json.dumps(details)
        )

        try:
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to save moderation log: {e}")
            db.session.rollback()

        reason = "Contenu pornographique détecté." if detection_type == 'nudity' else "Contenu violent détecté."
        return False, reason, log

def check_image_content(file_storage):
    """
    Wrapper function to check image content.
    Returns (is_safe, reason, log_entry)
    """
    moderator = ContentModerator()
    return moderator.check_image(file_storage)

def get_geo_info(ip_address):
    """
    Wrapper to get location info
    """
    moderator = ContentModerator()
    return moderator.get_location_info(ip_address)
