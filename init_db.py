#!/usr/bin/env python3
"""
Database initialization script for DISPARUS.ORG
Creates all tables and initializes default data (roles, settings)
"""

import os
import sys

from app import create_app
from models import db, User, Role, Disparu, Contribution, ModerationReport, ActivityLog, Download, SiteSetting
from werkzeug.security import generate_password_hash

app = create_app()


def init_default_roles():
    """Initialize default system roles"""
    default_roles = [
        {
            'name': 'admin',
            'display_name': 'Administrateur',
            'description': 'Acces complet a toutes les fonctionnalites',
            'permissions': {'all': True},
            'menu_access': ['dashboard', 'reports', 'moderation', 'contributions', 'statistics', 'map', 'users', 'roles', 'logs', 'downloads', 'settings'],
            'is_system': True
        },
        {
            'name': 'moderator',
            'display_name': 'Moderateur',
            'description': 'Gestion du contenu et moderation',
            'permissions': {'moderation': True, 'contributions': True, 'reports': True},
            'menu_access': ['dashboard', 'reports', 'moderation', 'contributions'],
            'is_system': True
        },
        {
            'name': 'ngo',
            'display_name': 'ONG',
            'description': 'Rapports et statistiques',
            'permissions': {'reports': True, 'statistics': True, 'exports': True},
            'menu_access': ['dashboard', 'reports', 'statistics'],
            'is_system': True
        },
        {
            'name': 'secours',
            'display_name': 'Services de secours',
            'description': 'Rapports et carte interactive',
            'permissions': {'reports': True, 'map': True},
            'menu_access': ['dashboard', 'reports', 'map'],
            'is_system': True
        }
    ]
    
    for role_data in default_roles:
        existing = Role.query.filter_by(name=role_data['name']).first()
        if not existing:
            role = Role(**role_data)
            db.session.add(role)
            print(f"  Created role: {role_data['name']}")
        else:
            print(f"  Role already exists: {role_data['name']}")
    
    db.session.commit()


def init_default_settings():
    """Initialize default site settings"""
    default_settings = [
        ('site_name', 'DISPARUS.ORG', 'string', 'general'),
        ('site_tagline', 'Plateforme citoyenne de signalement', 'string', 'general'),
        ('contact_email', 'contact@disparus.org', 'string', 'general'),
        ('seo_meta_title', 'DISPARUS.ORG - Personnes disparues en Afrique', 'string', 'seo'),
        ('seo_meta_description', 'Plateforme citoyenne pour signaler et rechercher les personnes disparues en Afrique', 'text', 'seo'),
        ('seo_meta_keywords', 'disparus, personnes disparues, afrique, recherche, signalement', 'string', 'seo'),
        ('footer_description', 'DISPARUS.ORG est une plateforme humanitaire citoyenne dediee a la recherche des personnes disparues en Afrique.', 'text', 'footer'),
        ('footer_col2_title', 'Liens utiles', 'string', 'footer'),
        ('footer_col2_links', '[{"text_fr": "Accueil", "text_en": "Home", "url": "/"}, {"text_fr": "Rechercher", "text_en": "Search", "url": "/recherche"}, {"text_fr": "Signaler", "text_en": "Report", "url": "/signaler"}]', 'text', 'footer'),
        ('footer_col3_title', 'Suivez-nous', 'string', 'footer'),
        ('footer_copyright', '2024 DISPARUS.ORG. Tous droits reserves.', 'string', 'footer'),
        ('enable_rate_limiting', 'true', 'boolean', 'security'),
        ('rate_limit_per_minute', '60', 'string', 'security'),
        ('enable_ip_logging', 'true', 'boolean', 'security'),
        ('max_upload_size_mb', '5', 'string', 'security'),
    ]
    
    for key, value, value_type, category in default_settings:
        existing = SiteSetting.query.filter_by(key=key).first()
        if not existing:
            setting = SiteSetting(
                key=key,
                value=value,
                value_type=value_type,
                category=category,
                updated_by='system'
            )
            db.session.add(setting)
            print(f"  Created setting: {key}")
        else:
            print(f"  Setting already exists: {key}")
    
    db.session.commit()


def init_admin_user():
    """Initialize default admin user if ADMIN_PASSWORD is set"""
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        print("  ADMIN_PASSWORD not set, skipping admin user creation")
        return
    
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("  Admin role not found, skipping admin user creation")
        return
    
    existing = User.query.filter_by(username='admin').first()
    if not existing:
        admin = User(
            username='admin',
            email='admin@disparus.org',
            password_hash=generate_password_hash(admin_password),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("  Created admin user")
    else:
        print("  Admin user already exists")


def init_database():
    """Main initialization function"""
    print("\n=== DISPARUS.ORG Database Initialization ===\n")
    
    with app.app_context():
        print("1. Creating database tables...")
        db.create_all()
        print("   Tables created successfully!\n")
        
        print("2. Initializing default roles...")
        init_default_roles()
        print("   Roles initialized!\n")
        
        print("3. Initializing default settings...")
        init_default_settings()
        print("   Settings initialized!\n")
        
        print("4. Checking admin user...")
        init_admin_user()
        print("   Admin check complete!\n")
        
        print("=== Database initialization complete! ===\n")


if __name__ == '__main__':
    init_database()
