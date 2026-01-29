"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Modele pour les parametres du site
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from models import db

_settings_cache = None

def get_all_settings_dict():
    global _settings_cache
    if _settings_cache is None:
        settings_list = SiteSetting.query.all()
        _settings_cache = {s.key: s.value for s in settings_list}
    return _settings_cache

def invalidate_settings_cache():
    global _settings_cache
    _settings_cache = None


class SiteSetting(db.Model):
    __tablename__ = 'site_settings_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')
    category = db.Column(db.String(50), default='general')
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    updated_by = db.Column(db.String(100))
    
    CATEGORIES = ['general', 'seo', 'email', 'security', 'appearance', 'integrations']
    
    @staticmethod
    def get(key, default=None):
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            if setting.value_type == 'boolean':
                return setting.value.lower() in ('true', '1', 'yes', 'on')
            elif setting.value_type == 'integer':
                return int(setting.value) if setting.value else default
            elif setting.value_type == 'json':
                import json
                return json.loads(setting.value) if setting.value else default
            return setting.value
        return default
    
    @staticmethod
    def set(key, value, value_type='string', category='general', description=None, updated_by=None):
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            if value_type == 'json':
                import json
                setting.value = json.dumps(value)
            else:
                setting.value = str(value)
            setting.value_type = value_type
            if description:
                setting.description = description
            setting.updated_by = updated_by
        else:
            if value_type == 'json':
                import json
                value = json.dumps(value)
            setting = SiteSetting(
                key=key,
                value=str(value),
                value_type=value_type,
                category=category,
                description=description,
                updated_by=updated_by
            )
            db.session.add(setting)
        db.session.commit()
        invalidate_settings_cache()
        return setting
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'category': self.category,
            'description': self.description,
            'is_public': self.is_public,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


DEFAULT_SETTINGS = {
    'site_name': {'value': 'DISPARUS.ORG', 'type': 'string', 'category': 'general'},
    'site_description': {'value': 'Plateforme citoyenne pour les personnes disparues en Afrique', 'type': 'string', 'category': 'general'},
    'contact_email': {'value': 'contact@disparus.org', 'type': 'string', 'category': 'general'},
    
    'seo_title': {'value': 'DISPARUS.ORG - Retrouver les personnes disparues', 'type': 'string', 'category': 'seo'},
    'seo_description': {'value': 'Plateforme humanitaire citoyenne pour signaler et rechercher les personnes disparues en Afrique', 'type': 'string', 'category': 'seo'},
    'seo_keywords': {'value': 'disparus, personnes disparues, Afrique, recherche, signalement', 'type': 'string', 'category': 'seo'},
    'seo_og_image': {'value': '', 'type': 'string', 'category': 'seo'},
    'seo_twitter_handle': {'value': '', 'type': 'string', 'category': 'seo'},
    'seo_head_scripts': {'value': '', 'type': 'text', 'category': 'seo'},
    'seo_body_scripts': {'value': '', 'type': 'text', 'category': 'seo'},
    'seo_robots': {'value': 'index, follow', 'type': 'string', 'category': 'seo'},
    'seo_canonical_url': {'value': '', 'type': 'string', 'category': 'seo'},
    'seo_google_analytics': {'value': '', 'type': 'string', 'category': 'seo'},
    'seo_google_tag_manager': {'value': '', 'type': 'string', 'category': 'seo'},
    
    'require_contribution_validation': {'value': 'true', 'type': 'boolean', 'category': 'general'},
    'allow_anonymous_reports': {'value': 'true', 'type': 'boolean', 'category': 'general'},
    'max_upload_size_mb': {'value': '5', 'type': 'integer', 'category': 'general'},
    
    'enable_rate_limiting': {'value': 'true', 'type': 'boolean', 'category': 'security'},
    'rate_limit_per_minute': {'value': '60', 'type': 'integer', 'category': 'security'},
    'blocked_ips': {'value': '[]', 'type': 'json', 'category': 'security'},
    'enable_ip_logging': {'value': 'true', 'type': 'boolean', 'category': 'security'},

    'default_search_filter': {'value': 'all', 'type': 'string', 'category': 'appearance'},
    'moderator_whatsapp_number': {'value': '', 'type': 'string', 'category': 'integrations'},
}


def init_default_settings():
    for key, config in DEFAULT_SETTINGS.items():
        existing = SiteSetting.query.filter_by(key=key).first()
        if not existing:
            SiteSetting.set(
                key=key,
                value=config['value'],
                value_type=config['type'],
                category=config['category'],
                updated_by='system'
            )


DEFAULT_ROLES = [
    {
        'name': 'admin',
        'display_name': 'Administrateur',
        'description': 'Acces complet a toutes les fonctionnalites',
        'permissions': {
            'manage_users': True,
            'manage_roles': True,
            'manage_settings': True,
            'manage_reports': True,
            'manage_contributions': True,
            'view_logs': True,
            'view_downloads': True,
            'moderate_content': True,
            'delete_content': True,
            'export_data': True,
        },
        'menu_access': ['dashboard', 'reports', 'moderation', 'contributions', 'statistics', 'map', 'users', 'roles', 'logs', 'downloads', 'settings'],
        'is_system': True,
    },
    {
        'name': 'moderator',
        'display_name': 'Moderateur',
        'description': 'Peut moderer le contenu et valider les contributions',
        'permissions': {
            'manage_reports': True,
            'manage_contributions': True,
            'moderate_content': True,
            'view_logs': False,
            'view_downloads': False,
        },
        'menu_access': ['dashboard', 'reports', 'moderation', 'contributions', 'map'],
        'is_system': True,
    },
    {
        'name': 'ngo',
        'display_name': 'ONG',
        'description': 'Organisation non gouvernementale partenaire',
        'permissions': {
            'manage_reports': True,
            'manage_contributions': False,
            'view_logs': False,
            'export_data': True,
        },
        'menu_access': ['dashboard', 'reports', 'statistics', 'map'],
        'is_system': True,
    },
    {
        'name': 'secours',
        'display_name': 'Services de Secours',
        'description': 'Services de secours et urgences',
        'permissions': {
            'manage_reports': True,
            'view_logs': False,
            'export_data': True,
        },
        'menu_access': ['dashboard', 'reports', 'map'],
        'is_system': True,
    },
    {
        'name': 'user',
        'display_name': 'Utilisateur',
        'description': 'Utilisateur standard',
        'permissions': {},
        'menu_access': [],
        'is_system': True,
    },
]


def init_default_roles():
    from models.user import Role
    for role_data in DEFAULT_ROLES:
        existing = Role.query.filter_by(name=role_data['name']).first()
        if not existing:
            role = Role(
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description'],
                permissions=role_data['permissions'],
                menu_access=role_data['menu_access'],
                is_system=role_data['is_system'],
            )
            db.session.add(role)
    db.session.commit()
