"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Configuration principale de l'application Flask
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
from flask import Flask, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect

from models import db
from routes import register_blueprints
from config import config

csrf = CSRFProtect()


def get_locale():
    locale = request.cookies.get('locale')
    print(f"DEBUG: get_locale called. Cookie: {locale}")
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')


def create_app(config_name='default'):
    app = Flask(__name__)
    
    session_secret = os.environ.get('SESSION_SECRET')
    if not session_secret:
        import secrets
        session_secret = secrets.token_hex(32)
        import logging
        logging.warning("SESSION_SECRET not set. Using random secret. Sessions will not persist across restarts.")
    app.config['SECRET_KEY'] = session_secret
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'statics/uploads'
    
    # Secure Session Cookies
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Enable Secure cookie if in production
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True

    db.init_app(app)
    csrf.init_app(app)
    
    babel = Babel(app, locale_selector=get_locale)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
        from models.settings import init_default_settings, init_default_roles
        init_default_settings()
        init_default_roles()
    
    app.jinja_env.globals['get_locale'] = get_locale
    
    @app.context_processor
    def inject_site_settings():
        from models.settings import get_all_settings_dict
        from utils.i18n import get_translation
        import json
        site_settings = get_all_settings_dict()
        
        def parse_json_links(json_str):
            try:
                return json.loads(json_str) if json_str else []
            except:
                return []
        
        def t(key):
            return get_translation(key, get_locale())

        return {
            'site_settings': site_settings,
            'parse_json_links': parse_json_links,
            't': t
        }
    
    register_blueprints(app)
    
    register_utility_routes(app)

    @app.after_request
    def add_security_headers(response):
        # Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy (CSP)
        # Permissive enough for CDNs and inline scripts used in templates
        csp = (
            "default-src 'self' https: data:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: blob:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https: data:; "
            "connect-src 'self' https:;"
        )
        response.headers['Content-Security-Policy'] = csp

        return response
    
    return app


def register_utility_routes(app):
    
    @app.route('/manifest.json')
    def manifest():
        return jsonify({
            "name": "DISPARUS.ORG",
            "short_name": "Disparus",
            "description": "Plateforme citoyenne de signalement de personnes disparues en Afrique",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#b91c1c",
            "icons": [
                {"src": "/statics/img/favicon.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/statics/img/favicon.png", "sizes": "512x512", "type": "image/png"}
            ]
        })
    
    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('statics/js', 'sw.js', mimetype='application/javascript')
    
    @app.route('/statics/<path:filename>')
    def serve_statics(filename):
        return send_from_directory('statics', filename)
