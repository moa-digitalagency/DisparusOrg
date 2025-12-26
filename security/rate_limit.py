from functools import wraps
from flask import request, jsonify
import time

request_counts = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 60


def rate_limit(max_requests=60, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            request_counts[client_ip] = [
                t for t in request_counts[client_ip]
                if current_time - t < window
            ]
            
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Too many requests',
                    'retry_after': window
                }), 429
            
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cleanup_old_requests():
    current_time = time.time()
    for ip in list(request_counts.keys()):
        request_counts[ip] = [
            t for t in request_counts[ip]
            if current_time - t < RATE_LIMIT_WINDOW
        ]
        if not request_counts[ip]:
            del request_counts[ip]
