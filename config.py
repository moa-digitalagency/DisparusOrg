"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is required")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BABEL_DEFAULT_LOCALE = 'fr'
    BABEL_SUPPORTED_LOCALES = ['fr', 'en']
    
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = 'statics/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Security Headers
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
