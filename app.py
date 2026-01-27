"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

import os
from flask import Flask, request, send_from_directory, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from models import db
from routes import register_blueprints
from config import config

csrf = CSRFProtect()


def get_locale():
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')


def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load config
    env_config = os.environ.get('FLASK_CONFIG', config_name)
    app.config.from_object(config.get(env_config, config['default']))

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

    # Security: Talisman (CSP, HSTS, etc.)
    csp = {
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
            "cdn.tailwindcss.com",
            "unpkg.com",
            "www.googletagmanager.com",
            "www.google-analytics.com",
            "www.gstatic.com",
            "api.mapbox.com"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "fonts.googleapis.com",
            "unpkg.com",
            "cdn.tailwindcss.com"
        ],
        'font-src': [
            "'self'",
            "fonts.gstatic.com",
            "data:"
        ],
        'img-src': [
            "'self'",
            "data:",
            "blob:",
            "tile.openstreetmap.org",
            "unpkg.com",
            "*.openstreetmap.org"
        ],
        'connect-src': [
            "'self'",
            "www.google-analytics.com",
            "www.googletagmanager.com"
        ]
    }

    # Disable force_https in dev/test if needed, based on config
    force_https = app.config.get('SESSION_COOKIE_SECURE', True)

    Talisman(app,
             content_security_policy=csp,
             force_https=force_https)

    # Security: Rate Limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["2000 per day", "200 per hour"],
        storage_uri="memory://"
    )
    
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
    register_error_handlers(app)
    
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

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_title="Page non trouvée", error_message="La page que vous recherchez n'existe pas ou a été déplacée."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_title="Erreur serveur", error_message="Une erreur inattendue est survenue. Nos équipes ont été notifiées."), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', error_title="Accès refusé", error_message="Vous n'avez pas les droits nécessaires pour accéder à cette page."), 403

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template('error.html', error_title="Trop de requêtes", error_message="Vous avez effectué trop de requêtes en peu de temps. Veuillez réessayer plus tard."), 429
