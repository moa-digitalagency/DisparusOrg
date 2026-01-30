"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Modele pour les logs de moderation
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from datetime import datetime
from models import db

class ContentModerationLog(db.Model):
    __tablename__ = 'content_moderation_logs'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    detection_type = db.Column(db.String(50))  # 'nudity', 'violence'
    score = db.Column(db.Float)
    details = db.Column(db.Text)
    metadata_json = db.Column(db.Text)  # For storing full JSON response or extra headers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'country': self.country,
            'city': self.city,
            'detection_type': self.detection_type,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
