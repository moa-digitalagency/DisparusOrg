import os
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel

db = SQLAlchemy()
babel = Babel()

def get_locale():
    """Get locale from cookie or browser preference."""
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required. Please set it to a valid PostgreSQL connection string.")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['fr', 'en']
    
    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    
    # Make get_locale available in templates
    @app.context_processor
    def inject_locale():
        return {'get_locale': get_locale}
    
    with app.app_context():
        from app import models
        from app import routes
        app.register_blueprint(routes.bp)
        db.create_all()
    
    return app
