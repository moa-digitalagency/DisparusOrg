"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Fichier de configuration de l'application
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os

class Config:
    # Common settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'fr'
    BABEL_SUPPORTED_LOCALES = ['fr', 'en']
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '243860493345')
    TIDYCAL_URL = os.environ.get('TIDYCAL_URL', 'https://tidycal.com/moamyoneart/consultation-gratuite-15-min')

    # Security / Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Default to False, override in Production

    # Database URL (Load safely, validate in init_app)
    # This is loaded at import time, but can be overridden in init_app from env
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @staticmethod
    def init_app(app):
        # Allow runtime override of DATABASE_URL from environment
        # This is crucial for tests that change os.environ['DATABASE_URL']
        env_db_url = os.environ.get('DATABASE_URL')
        if env_db_url:
            app.config['SQLALCHEMY_DATABASE_URI'] = env_db_url

        # Database URL Validation
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
             raise RuntimeError("DATABASE_URL environment variable is required")

        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    # Fallback key for dev to ensure session stability on reload
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-fallback-key')


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    # In production, if SESSION_SECRET is missing, this is None.
    # We validate this in init_app.
    SECRET_KEY = os.environ.get('SESSION_SECRET')

    @classmethod
    def init_app(cls, app):
        # Call parent init_app (checks DB URL, creates folders)
        Config.init_app(app)

        # Strict Secret Key Validation
        if not app.config.get('SECRET_KEY'):
            raise ValueError("SESSION_SECRET environment variable is required in production")

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
