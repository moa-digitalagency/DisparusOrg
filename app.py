import os
from flask import Flask, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel

from models import db
from routes import register_blueprints
from config import config


def get_locale():
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')


def create_app(config_name='default'):
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'statics/uploads'
    
    db.init_app(app)
    
    babel = Babel(app, locale_selector=get_locale)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    app.jinja_env.globals['get_locale'] = get_locale
    
    register_blueprints(app)
    
    register_utility_routes(app)
    
    return app


def register_utility_routes(app):
    
    @app.route('/moderation')
    def moderation():
        from flask import render_template
        from models import Disparu, Contribution, ModerationReport
        
        reports = ModerationReport.query.filter_by(status='pending').order_by(ModerationReport.created_at.desc()).all()
        flagged = Disparu.query.filter_by(is_flagged=True).all()
        stats = {
            'pending': len(reports),
            'flagged': len(flagged),
            'total_disparus': Disparu.query.count(),
            'total_contributions': Contribution.query.count(),
        }
        return render_template('moderation.html', reports=reports, flagged_disparus=flagged, stats=stats)
    
    @app.route('/moderation/<int:report_id>/resolve', methods=['POST'])
    def resolve_report(report_id):
        from flask import redirect, url_for, request
        from datetime import datetime
        from models import Disparu, ModerationReport
        
        report = ModerationReport.query.get_or_404(report_id)
        
        report.status = 'resolved'
        report.reviewed_by = 'admin'
        report.reviewed_at = datetime.utcnow()
        
        action = request.form.get('action')
        
        if action == 'remove':
            if report.target_type == 'disparu':
                disparu = Disparu.query.get(report.target_id)
                if disparu:
                    db.session.delete(disparu)
        elif action == 'unflag':
            if report.target_type == 'disparu':
                disparu = Disparu.query.get(report.target_id)
                if disparu:
                    disparu.is_flagged = False
        
        db.session.commit()
        return redirect(url_for('moderation'))
    
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
