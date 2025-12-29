from models import db


class Contribution(db.Model):
    __tablename__ = 'contributions_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    disparu_id = db.Column(db.Integer, db.ForeignKey('disparus_flask.id'), nullable=False)
    
    contribution_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)
    
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String(200))
    
    observation_date = db.Column(db.DateTime)
    proof_url = db.Column(db.String(500))
    
    person_state = db.Column(db.String(50))
    return_circumstances = db.Column(db.Text)
    
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    
    contributor_name = db.Column(db.String(100))
    content = db.Column(db.Text)
    location = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'disparu_id': self.disparu_id,
            'contribution_type': self.contribution_type,
            'details': self.details,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'observation_date': self.observation_date.isoformat() if self.observation_date else None,
            'proof_url': self.proof_url,
            'person_state': self.person_state,
            'return_circumstances': self.return_circumstances,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
