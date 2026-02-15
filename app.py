"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Configuration principale de l'application Flask
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
from flask import Flask, request, send_from_directory, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect

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
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    app.config['WHATSAPP_NUMBER'] = os.environ.get('WHATSAPP_NUMBER', '243860493345')
    app.config['TIDYCAL_URL'] = os.environ.get('TIDYCAL_URL', 'https://tidycal.com/moamyoneart/consultation-gratuite-15-min')

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
    
    app.jinja_env.globals['get_locale'] = get_locale
    
    @app.context_processor
    def inject_site_settings():
        from models.settings import get_all_settings_dict
        from utils.i18n import get_translation
        import json
        # Use cached settings to avoid DB query on every request
        site_settings = get_all_settings_dict()
        
        def parse_json_links(json_str):
            try:
                return json.loads(json_str) if json_str else []
            except:
                return []
        
        def t(key, **kwargs):
            text = get_translation(key, get_locale())
            if kwargs:
                try:
                    return text.format(**kwargs)
                except:
                    return text
            return text

        return {
            'site_settings': site_settings,
            'parse_json_links': parse_json_links,
            't': t,
            'config': app.config
        }
    
    register_blueprints(app)
    
    register_utility_routes(app)

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Bad Request',
                'message': str(e.description) if hasattr(e, 'description') else 'Bad Request'
            }), 400
        return render_template('400.html', error=e), 400

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Forbidden',
                'message': str(e.description) if hasattr(e, 'description') else 'Forbidden'
            }), 403
        return render_template('403.html', error=e), 403

    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Not Found',
                'message': str(e.description) if hasattr(e, 'description') else 'Not Found'
            }), 404
        return render_template('404.html', error=e), 404

    @app.errorhandler(451)
    def unavailable_for_legal_reasons(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Unavailable For Legal Reasons',
                'message': str(e.description) if hasattr(e, 'description') else 'Unavailable For Legal Reasons'
            }), 451
        return render_template('451.html', error=e), 451

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Too many requests',
                'message': str(e.description) if hasattr(e, 'description') else 'Rate limit exceeded'
            }), 429
        return render_template('429.html', error=e), 429

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
             return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred.'
            }), 500
        return render_template('500.html'), 500

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
        from models import SiteSetting

        # Check if PWA is enabled
        if not SiteSetting.get('pwa_enabled', False):
            return "PWA Not Enabled", 404

        display_mode = SiteSetting.get('pwa_display_mode', 'default')

        # Default values (Fallbacks)
        name = SiteSetting.get('site_name', 'DISPARUS.ORG')
        short_name = "Disparus"
        description = SiteSetting.get('site_description', 'Plateforme citoyenne de signalement de personnes disparues en Afrique')
        theme_color = "#b91c1c"
        background_color = "#ffffff"
        icon_src = "/static/img/favicon.png"

        # Override if custom
        if display_mode == 'custom':
            name = SiteSetting.get('pwa_app_name', name)
            short_name = SiteSetting.get('pwa_short_name', short_name)
            description = SiteSetting.get('pwa_description', description)
            theme_color = SiteSetting.get('pwa_theme_color', theme_color)
            background_color = SiteSetting.get('pwa_background_color', background_color)
            custom_icon = SiteSetting.get('pwa_icon')
            if custom_icon:
                icon_src = custom_icon

        # Ensure values are strings (SiteSetting.get might return None if key missing)
        name = str(name) if name else ""
        short_name = str(short_name) if short_name else ""
        description = str(description) if description else ""
        theme_color = str(theme_color) if theme_color else "#b91c1c"
        background_color = str(background_color) if background_color else "#ffffff"
        icon_src = str(icon_src) if icon_src else "/static/img/favicon.png"

        return jsonify({
            "name": name,
            "short_name": short_name,
            "description": description,
            "start_url": "/",
            "display": "standalone",
            "background_color": background_color,
            "theme_color": theme_color,
            "icons": [
                {"src": icon_src, "sizes": "192x192", "type": "image/png"},
                {"src": icon_src, "sizes": "512x512", "type": "image/png"}
            ]
        })
    
    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('static/js', 'sw.js', mimetype='application/javascript')
