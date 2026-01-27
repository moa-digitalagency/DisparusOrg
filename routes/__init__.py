"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Initialisation du module routes
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint

from routes.public import public_bp
from routes.admin import admin_bp
from routes.api import api_bp


def register_blueprints(app):
    from app import csrf
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    csrf.exempt(api_bp)
