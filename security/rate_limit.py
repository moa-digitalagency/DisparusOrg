"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Gestion de la limitation de debit (Rate Limiting)
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from functools import wraps
from flask import request, jsonify, current_app, abort, session
import time
import re

request_counts = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 60


def get_rate_limit_settings():
    """Get rate limit settings from database"""
    try:
        from models.settings import SiteSetting
        enabled = SiteSetting.query.filter_by(key='enable_rate_limiting').first()
        rate = SiteSetting.query.filter_by(key='rate_limit_per_minute').first()
        
        is_enabled = enabled and enabled.value == 'true'
        max_requests = int(rate.value) if rate and rate.value else 60
        
        return is_enabled, max_requests
    except Exception:
        return True, 60


def get_blocked_ips():
    """Get list of blocked IPs from database"""
    try:
        from models.settings import SiteSetting
        setting = SiteSetting.query.filter_by(key='blocked_ips').first()
        if setting and setting.value:
            ips = re.split(r'[,\n\r]+', setting.value)
            return [ip.strip() for ip in ips if ip.strip()]
        return []
    except Exception:
        return []


def get_whitelisted_ips():
    """Get list of whitelisted IPs from database"""
    try:
        from models.settings import SiteSetting
        setting = SiteSetting.query.filter_by(key='whitelisted_ips').first()
        if setting and setting.value:
            ips = re.split(r'[,\n\r]+', setting.value)
            return [ip.strip() for ip in ips if ip.strip()]
        return []
    except Exception:
        return []


def rate_limit(max_requests=None, window=60):
    """Rate limiting decorator with configurable settings from database"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Bypass rate limit for logged in admins
            if session.get('admin_logged_in'):
                return f(*args, **kwargs)

            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            # Check whitelist
            whitelisted_ips = get_whitelisted_ips()
            if client_ip in whitelisted_ips:
                return f(*args, **kwargs)

            # Check blacklist
            blocked_ips = get_blocked_ips()
            if client_ip in blocked_ips:
                return jsonify({
                    'error': 'Access denied',
                    'message': 'Your IP has been blocked'
                }), 403
            
            is_enabled, db_max_requests = get_rate_limit_settings()
            
            if not is_enabled:
                return f(*args, **kwargs)
            
            effective_max = max_requests if max_requests is not None else db_max_requests
            current_time = time.time()
            
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            request_counts[client_ip] = [
                t for t in request_counts[client_ip]
                if current_time - t < window
            ]
            
            if len(request_counts[client_ip]) >= effective_max:
                if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'error': 'Too many requests',
                        'message': f'Rate limit exceeded. Maximum {effective_max} requests per minute.',
                        'retry_after': window
                    }), 429

                abort(429, description=f'Rate limit exceeded. Maximum {effective_max} requests per minute.')
            
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cleanup_old_requests():
    """Clean up expired request tracking data"""
    current_time = time.time()
    for ip in list(request_counts.keys()):
        request_counts[ip] = [
            t for t in request_counts[ip]
            if current_time - t < RATE_LIMIT_WINDOW
        ]
        if not request_counts[ip]:
            del request_counts[ip]
