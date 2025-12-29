from models import db
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    permissions = db.Column(db.JSON, default=dict)
    
    menu_access = db.Column(db.JSON, default=list)
    
    is_system = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    users = db.relationship('User', backref='role_obj', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'permissions': self.permissions,
            'menu_access': self.menu_access,
            'is_system': self.is_system,
        }


class User(db.Model):
    __tablename__ = 'users_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))
    
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    organization = db.Column(db.String(200))
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles_flask.id'))
    role = db.Column(db.String(20), default='user')
    
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email.split('@')[0]
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'organization': self.organization,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ModerationReport(db.Model):
    __tablename__ = 'moderation_reports_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    
    reason = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    reporter_contact = db.Column(db.String(200))
    reporter_ip = db.Column(db.String(50))
    
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.String(100))
    reviewed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
