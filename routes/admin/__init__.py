from flask import Blueprint, session, request, redirect, url_for
from functools import wraps
from models import db, ActivityLog

admin_bp = Blueprint('admin', __name__)

def log_activity(action, action_type='admin', target_type=None, target_id=None, target_name=None, severity='info', is_security=False):
    """Helper function to log admin activities"""
    try:
        log = ActivityLog()
        log.username = session.get('admin_username', 'system')
        log.action = action
        log.action_type = action_type
        log.target_type = target_type
        log.target_id = str(target_id) if target_id else None
        log.target_name = target_name
        log.ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        log.user_agent = request.headers.get('User-Agent', '')[:500] if request.headers.get('User-Agent') else None
        log.severity = severity
        log.is_security_event = is_security
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        import logging
        logging.error(f"Error logging activity: {e}")
        try:
            db.session.rollback()
        except:
            pass

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

from . import dashboard, management, moderation, export
