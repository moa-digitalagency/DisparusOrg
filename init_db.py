"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Script d'initialisation de la base de donnees
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
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
import logging

from app import create_app
from models import db, User, Role, Disparu, Contribution, ModerationReport, ActivityLog, Download, SiteSetting, ContentModerationLog
from werkzeug.security import generate_password_hash
from sqlalchemy import text, inspect, Integer, Boolean, String, Text, Float, DateTime, JSON
from sqlalchemy.exc import ProgrammingError, OperationalError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        try:
            existing = Role.query.filter_by(name=role_data['name']).first()
            if not existing:
                role = Role(**role_data)
                db.session.add(role)
                logger.info(f"  Created role: {role_data['name']}")
            else:
                logger.info(f"  Role already exists: {role_data['name']}")
        except Exception as e:
            logger.error(f"  Error checking role {role_data['name']}: {e}")
            db.session.rollback()
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"  Error committing roles: {e}")
        db.session.rollback()


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
        ('default_search_filter', 'all', 'string', 'appearance'),
        ('moderator_whatsapp_number', '', 'string', 'integrations'),
        # PWA Settings
        ('pwa_enabled', 'false', 'boolean', 'pwa'),
        ('pwa_display_mode', 'default', 'string', 'pwa'),
        ('pwa_app_name', 'DISPARUS.ORG', 'string', 'pwa'),
        ('pwa_short_name', 'Disparus', 'string', 'pwa'),
        ('pwa_description', '', 'text', 'pwa'),
        ('pwa_theme_color', '#b91c1c', 'string', 'pwa'),
        ('pwa_background_color', '#ffffff', 'string', 'pwa'),
        ('pwa_icon', '', 'string', 'pwa'),
    ]
    
    for key, value, value_type, category in default_settings:
        try:
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
                logger.info(f"  Created setting: {key}")
            else:
                logger.info(f"  Setting already exists: {key}")
        except Exception as e:
            logger.error(f"  Error checking setting {key}: {e}")
            db.session.rollback()
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"  Error committing settings: {e}")
        db.session.rollback()


def init_admin_user():
    """Initialize default admin user if ADMIN_PASSWORD is set"""
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        logger.info("  ADMIN_PASSWORD not set, skipping admin user creation")
        return
    
    try:
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            logger.info("  Admin role not found, skipping admin user creation")
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
            logger.info("  Created admin user")
        else:
            logger.info("  Admin user already exists")
    except Exception as e:
        logger.error(f"  Error initializing admin user: {e}")
        db.session.rollback()


def create_missing_tables():
    """Create any missing tables for VPS deployments"""
    logger.info("Checking for missing tables...")
    
    try:
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Check all models defined in SQLAlchemy metadata
        missing_tables = []
        for table_name in db.metadata.tables.keys():
            if table_name not in existing_tables:
                missing_tables.append(table_name)

        if missing_tables:
            logger.info(f"  Missing tables: {', '.join(missing_tables)}")
            logger.info("  Creating all tables...")
            try:
                db.create_all()
                logger.info("  Tables created successfully!")
            except Exception as e:
                logger.error(f"  Failed to create tables: {e}")
                # Important: If create_all fails, we might still want to try syncing if some tables exist
        else:
            logger.info("  All tables exist")

        return missing_tables
    except Exception as e:
        logger.error(f"  Error during table check: {e}")
        return []


def sync_schema_columns():
    """
    Robust migration: Iterates through all models and adds missing columns.
    This ensures the DB schema matches the code even if 'db.create_all()' was skipped
    or if the DB is from an older version.
    """
    logger.info("Syncing schema columns (Auto-Migration)...")
    
    try:
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        # Use get_bind() to ensure we get the correct engine/connection
        try:
            dialect = db.session.get_bind().dialect.name
        except:
            dialect = db.engine.dialect.name

        logger.info(f"  Detected Database Dialect: {dialect}")
        
        migrations_applied = 0

        for table_name, table_obj in db.metadata.tables.items():
            if table_name not in existing_tables:
                continue

            try:
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
            except Exception as e:
                logger.error(f"  Failed to inspect columns for {table_name}: {e}")
                continue

            for column in table_obj.columns:
                if column.name not in existing_columns:
                    logger.info(f"  Found missing column: {table_name}.{column.name}")

                    # Determine SQL type
                    col_type = column.type.compile(db.engine.dialect)

                    # Handle default for NOT NULL constraint mitigation
                    default_val = ""
                    if not column.nullable:
                        if isinstance(column.type, (Integer, Float)):
                            default_val = " DEFAULT 0"
                        elif isinstance(column.type, Boolean):
                            # PostgreSQL requires TRUE/FALSE, SQLite can take 1/0 but 0/1 is safer there too usually
                            # but let's be specific
                            default_val = " DEFAULT FALSE"
                            if dialect == 'sqlite':
                                default_val = " DEFAULT 0"
                        elif isinstance(column.type, (String, Text)):
                            default_val = " DEFAULT ''"
                        elif isinstance(column.type, DateTime):
                             # CURRENT_TIMESTAMP works in both Postgres and SQLite
                             default_val = " DEFAULT CURRENT_TIMESTAMP"
                        elif isinstance(column.type, JSON):
                            default_val = " DEFAULT '{}'"

                    try:
                        # Construct ALTER TABLE statement
                        # SQLite 'ADD COLUMN' syntax is standard-ish
                        sql = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{default_val}'
                        db.session.execute(text(sql))
                        db.session.commit()
                        logger.info(f"  + Added column {column.name} to {table_name}")
                        migrations_applied += 1
                    except ProgrammingError as e:
                        # Handle case where column might have been added by another process or race condition
                        if "already exists" in str(e) or "duplicate column" in str(e):
                            logger.info(f"  - Column {column.name} already exists (race condition handled)")
                            db.session.rollback()
                        else:
                            logger.error(f"  - Failed to add column {column.name} to {table_name} (ProgrammingError): {e}")
                            db.session.rollback()
                    except Exception as e:
                        logger.error(f"  - Failed to add column {column.name} to {table_name}: {e}")
                        db.session.rollback()

        if migrations_applied > 0:
            logger.info(f"  {migrations_applied} column migrations applied successfully.")
        else:
            logger.info("  Schema is up to date. No columns missing.")

    except Exception as e:
        logger.error(f"  Critical error during schema sync: {e}")


def run_migrations():
    """Run database specific optimizations and migrations"""
    logger.info("Running specific migrations/optimizations...")

    # Generic Sync (Covers the manual checks previously here)
    sync_schema_columns()
    
    # Postgres-specific optimizations (Indexes)
    try:
        # Check dialect again just to be safe
        dialect_name = db.session.get_bind().dialect.name
    except:
        dialect_name = 'unknown'

    if dialect_name == 'postgresql':
        try:
            # Create GIN index for Full Text Search
            # Using DO block for robustness if possible, but standard IF NOT EXISTS is good
            sql = """
            CREATE INDEX IF NOT EXISTS idx_disparu_fulltext
            ON disparus_flask
            USING gin(to_tsvector('french',
                coalesce(first_name,'') || ' ' ||
                coalesce(last_name,'') || ' ' ||
                coalesce(public_id,'') || ' ' ||
                coalesce(city,'')
            ));
            """
            db.session.execute(text(sql))
            db.session.commit()
            logger.info("  + Verified/Created Postgres GIN index for full text search")
        except Exception as e:
            db.session.rollback()
            logger.warning(f"  - Postgres optimization skipped/failed: {e}")

    elif dialect_name == 'sqlite':
        try:
            # Check if FTS table exists
            # We use inspect to check regular tables, but virtual tables show up there too usually.
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if 'disparus_fts' not in tables:
                logger.info("  Setting up SQLite FTS...")

                # 1. Create Virtual Table (External Content)
                # This indexes content from disparus_flask without duplicating storage
                db.session.execute(text("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS disparus_fts USING fts5(
                        first_name,
                        last_name,
                        public_id,
                        city,
                        content='disparus_flask',
                        content_rowid='id'
                    );
                """))

                # 2. Create Triggers to keep index in sync
                # Insert Trigger
                db.session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS disparus_ai AFTER INSERT ON disparus_flask BEGIN
                        INSERT INTO disparus_fts(rowid, first_name, last_name, public_id, city)
                        VALUES (new.id, new.first_name, new.last_name, new.public_id, new.city);
                    END;
                """))

                # Delete Trigger
                db.session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS disparus_ad AFTER DELETE ON disparus_flask BEGIN
                        INSERT INTO disparus_fts(disparus_fts, rowid, first_name, last_name, public_id, city)
                        VALUES('delete', old.id, old.first_name, old.last_name, old.public_id, old.city);
                    END;
                """))

                # Update Trigger
                db.session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS disparus_au AFTER UPDATE ON disparus_flask BEGIN
                        INSERT INTO disparus_fts(disparus_fts, rowid, first_name, last_name, public_id, city)
                        VALUES('delete', old.id, old.first_name, old.last_name, old.public_id, old.city);
                        INSERT INTO disparus_fts(rowid, first_name, last_name, public_id, city)
                        VALUES (new.id, new.first_name, new.last_name, new.public_id, new.city);
                    END;
                """))

                # 3. Populate initially from existing data
                db.session.execute(text("""
                    INSERT INTO disparus_fts(rowid, first_name, last_name, public_id, city)
                    SELECT id, first_name, last_name, public_id, city FROM disparus_flask;
                """))

                db.session.commit()
                logger.info("  + SQLite FTS setup complete.")
            else:
                 logger.info("  SQLite FTS already setup.")

        except Exception as e:
            db.session.rollback()
            # If fts5 is not available, this will fail. We should log it but not crash.
            logger.warning(f"  - SQLite optimization skipped/failed: {e}")


def generate_demo_images():
    """Generate demo profile images if they don't exist"""
    demo_folder = 'statics/uploads/demo'
    
    demo_images = [
        'demo_child_male.jpg',
        'demo_adult_male.jpg', 
        'demo_adult_male_2.jpg',
        'demo_adult_female.jpg'
    ]
    
    # Check if we need to generate images
    missing_images = [img for img in demo_images if not os.path.exists(os.path.join(demo_folder, img))]
    
    if missing_images:
        logger.info("  Generating demo images...")
        try:
            # We import here to avoid dependency issues if script is missing
            from scripts.generate_demo_images import generate_all_demo_images
            generate_all_demo_images()
        except ImportError:
            logger.warning("  Warning: Could not import demo image generator (scripts.generate_demo_images)")
            os.makedirs(demo_folder, exist_ok=True)
    else:
        logger.info("  Demo images already exist")


def init_database():
    """Main initialization function"""
    logger.info("=== DISPARUS.ORG Database Initialization ===")
    
    with app.app_context():
        # Ensure the instance folder exists if using SQLite (before connecting)
        # This prevents "unable to open database file" errors on first run
        if 'sqlite' in str(db.engine.url):
            try:
                os.makedirs('instance', exist_ok=True)
                logger.info("   Checked/Created instance folder for SQLite.")
            except OSError as e:
                logger.warning(f"   Could not create instance folder: {e}")

        # 0. Pre-flight Connection Check
        try:
            with db.engine.connect() as conn:
                pass
        except OperationalError as e:
            logger.critical(f"FATAL: Could not connect to database: {e}")
            logger.critical("Check DATABASE_URL and ensure database server is running.")
            sys.exit(1)

        # Log database connection info
        try:
            db_url = db.engine.url.render_as_string(hide_password=True)
            logger.info(f"   Using Database: {db_url}")
        except:
            # Fallback for older SQLAlchemy versions or if something goes wrong
            logger.info(f"   Using Database: {db.engine.url}")

        logger.info("1. Checking and creating missing tables...")
        missing = create_missing_tables()
        if missing:
            logger.info(f"   Created tables: {', '.join(missing)}")
        else:
            logger.info("   All required tables exist!")
        
        logger.info("2. Running migrations and schema sync...")
        run_migrations()
        logger.info("   Migrations complete!")
        
        logger.info("3. Initializing default roles...")
        init_default_roles()
        logger.info("   Roles initialized!")
        
        logger.info("4. Initializing default settings...")
        init_default_settings()
        logger.info("   Settings initialized!")
        
        logger.info("5. Checking admin user...")
        init_admin_user()
        logger.info("   Admin check complete!")
        
        logger.info("6. Checking demo images...")
        generate_demo_images()
        logger.info("   Demo images ready!")
        
        logger.info("=== Database initialization complete! ===")


if __name__ == '__main__':
    init_database()
