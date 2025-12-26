from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.disparu import Disparu
from models.contribution import Contribution
from models.user import User, ModerationReport

__all__ = ['db', 'Disparu', 'Contribution', 'User', 'ModerationReport']
