"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

from models import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users_flask.id'), nullable=True)
    username = db.Column(db.String(100))
    
    action = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.String(50))
    target_name = db.Column(db.String(200))
    
    details = db.Column(db.JSON)
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.Text)
    
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    is_security_event = db.Column(db.Boolean, default=False)
    severity = db.Column(db.String(20), default='info')
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    user = db.relationship('User', backref='activities', lazy='select')
    
    ACTION_TYPES = {
        'auth': ['login', 'logout', 'login_failed', 'password_reset'],
        'view': ['page_view', 'search', 'detail_view', 'map_view'],
        'create': ['report_created', 'contribution_added', 'user_created'],
        'update': ['status_changed', 'profile_updated', 'contribution_validated'],
        'delete': ['report_deleted', 'contribution_deleted', 'user_deleted'],
        'download': ['pdf_downloaded', 'image_downloaded', 'export_downloaded'],
        'security': ['suspicious_activity', 'rate_limited', 'blocked_ip'],
        'admin': ['settings_changed', 'role_modified', 'user_role_changed'],
    }
    
    SEVERITY_LEVELS = ['debug', 'info', 'warning', 'error', 'critical']
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'action_type': self.action_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'details': self.details,
            'ip_address': self.ip_address,
            'country': self.country,
            'city': self.city,
            'is_security_event': self.is_security_event,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def log_activity(action, action_type, target_type=None, target_id=None, target_name=None,
                 user_id=None, username=None, details=None, ip_address=None, 
                 user_agent=None, referrer=None, is_security=False, severity='info'):
    log = ActivityLog(
        user_id=user_id,
        username=username or 'Anonymous',
        action=action,
        action_type=action_type,
        target_type=target_type,
        target_id=str(target_id) if target_id else None,
        target_name=target_name,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        is_security_event=is_security,
        severity=severity,
    )
    db.session.add(log)
    db.session.commit()
    return log
