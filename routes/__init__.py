from flask import Blueprint

from routes.public import public_bp
from routes.admin import admin_bp
from routes.api import api_bp


def register_blueprints(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
