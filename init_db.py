"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

#!/usr/bin/env python3
"""
Database initialization script for DISPARUS.ORG
Creates all tables and initializes default data (roles, settings)
Includes migration support for VPS deployments
"""

import os
import sys
from datetime import datetime

from app import create_app
from models import db, User, Role, Disparu, Contribution, ModerationReport, ActivityLog, Download, SiteSetting
from werkzeug.security import generate_password_hash
from sqlalchemy import text, inspect

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


def create_missing_tables():
    """Create any missing tables for VPS deployments"""
    print("Checking for missing tables...")
    
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = [
        'disparus_flask',
        'contributions_flask', 
        'moderation_reports_flask',
        'users_flask',
        'roles_flask',
        'activity_logs_flask',
        'downloads_flask',
        'site_settings_flask'
    ]
    
    missing_tables = [t for t in required_tables if t not in existing_tables]
    
    if missing_tables:
        print(f"  Missing tables: {', '.join(missing_tables)}")
        print("  Creating all tables...")
        db.create_all()
        print("  Tables created successfully!")
    else:
        print("  All tables exist")
    
    return missing_tables


def run_migrations():
    """Run database migrations for VPS deployments"""
    print("Running migrations...")
    
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    migrations_applied = 0
    
    if 'disparus_flask' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('disparus_flask')]
        
        if 'view_count' not in columns:
            try:
                db.session.execute(text('ALTER TABLE disparus_flask ADD COLUMN view_count INTEGER DEFAULT 0'))
                db.session.commit()
                print("  + Added column: disparus_flask.view_count")
                migrations_applied += 1
            except Exception as e:
                db.session.rollback()
                print(f"  - Migration view_count skipped: {e}")
        
        if 'is_flagged' not in columns:
            try:
                db.session.execute(text('ALTER TABLE disparus_flask ADD COLUMN is_flagged BOOLEAN DEFAULT FALSE'))
                db.session.commit()
                print("  + Added column: disparus_flask.is_flagged")
                migrations_applied += 1
            except Exception as e:
                db.session.rollback()
                print(f"  - Migration is_flagged skipped: {e}")
    
    if 'contributions_flask' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('contributions_flask')]
        
        if 'is_approved' not in columns:
            try:
                db.session.execute(text('ALTER TABLE contributions_flask ADD COLUMN is_approved BOOLEAN DEFAULT FALSE'))
                db.session.commit()
                print("  + Added column: contributions_flask.is_approved")
                migrations_applied += 1
            except Exception as e:
                db.session.rollback()
                print(f"  - Migration is_approved skipped: {e}")
    
    if migrations_applied > 0:
        print(f"  {migrations_applied} migrations applied")
    else:
        print("  No migrations needed")


def generate_demo_images():
    """Generate demo profile images if they don't exist"""
    demo_folder = 'statics/uploads/demo'
    
    demo_images = [
        'demo_child_male.jpg',
        'demo_adult_male.jpg', 
        'demo_adult_male_2.jpg',
        'demo_adult_female.jpg'
    ]
    
    missing_images = [img for img in demo_images if not os.path.exists(os.path.join(demo_folder, img))]
    
    if missing_images:
        print("  Generating demo images...")
        try:
            from scripts.generate_demo_images import generate_all_demo_images
            generate_all_demo_images()
        except ImportError:
            print("  Warning: Could not import demo image generator")
            os.makedirs(demo_folder, exist_ok=True)
    else:
        print("  Demo images already exist")


def init_database():
    """Main initialization function"""
    print("\n=== DISPARUS.ORG Database Initialization ===\n")
    
    with app.app_context():
        print("1. Checking and creating missing tables...")
        missing = create_missing_tables()
        if missing:
            print(f"   Created tables: {', '.join(missing)}\n")
        else:
            print("   All required tables exist!\n")
        
        print("2. Running migrations...")
        run_migrations()
        print("   Migrations complete!\n")
        
        print("3. Initializing default roles...")
        init_default_roles()
        print("   Roles initialized!\n")
        
        print("4. Initializing default settings...")
        init_default_settings()
        print("   Settings initialized!\n")
        
        print("5. Checking admin user...")
        init_admin_user()
        print("   Admin check complete!\n")
        
        print("6. Checking demo images...")
        generate_demo_images()
        print("   Demo images ready!\n")
        
        print("=== Database initialization complete! ===\n")


if __name__ == '__main__':
    init_database()
