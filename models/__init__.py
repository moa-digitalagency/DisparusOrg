"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.disparu import Disparu
from models.contribution import Contribution
from models.user import User, ModerationReport, Role
from models.activity_log import ActivityLog, log_activity
from models.download import Download
from models.settings import SiteSetting, init_default_settings, init_default_roles

__all__ = [
    'db', 
    'Disparu', 
    'Contribution', 
    'User', 
    'ModerationReport', 
    'Role',
    'ActivityLog', 
    'log_activity',
    'Download',
    'SiteSetting',
    'init_default_settings',
    'init_default_roles',
]
