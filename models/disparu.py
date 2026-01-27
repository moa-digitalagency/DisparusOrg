"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Modele pour les personnes disparues
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from models import db


class Disparu(db.Model):
    __tablename__ = 'disparus_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(6), unique=True, nullable=False, index=True)
    
    person_type = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(20), nullable=False)
    
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    
    physical_description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(500))
    
    disappearance_date = db.Column(db.DateTime, nullable=False)
    circumstances = db.Column(db.Text, nullable=False)
    
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    clothing = db.Column(db.Text)
    objects = db.Column(db.Text)
    
    contacts = db.Column(db.JSON)
    
    status = db.Column(db.String(20), default='missing')
    is_flagged = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    contributions = db.relationship('Contribution', backref='disparu', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'public_id': self.public_id,
            'person_type': self.person_type,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'sex': self.sex,
            'country': self.country,
            'city': self.city,
            'physical_description': self.physical_description,
            'photo_url': self.photo_url,
            'disappearance_date': self.disappearance_date.isoformat() if self.disappearance_date else None,
            'circumstances': self.circumstances,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'clothing': self.clothing,
            'objects': self.objects,
            'contacts': self.contacts,
            'status': self.status,
            'is_flagged': self.is_flagged,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
