from models import db


class Download(db.Model):
    __tablename__ = 'downloads_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users_flask.id'), nullable=True)
    
    disparu_id = db.Column(db.Integer, db.ForeignKey('disparus_flask.id'), nullable=True)
    disparu_public_id = db.Column(db.String(10))
    disparu_name = db.Column(db.String(200))
    
    file_type = db.Column(db.String(20), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    
    download_type = db.Column(db.String(50), nullable=False)
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    user = db.relationship('User', backref='downloads', lazy='select')
    disparu = db.relationship('Disparu', backref='downloads', lazy='select')
    
    DOWNLOAD_TYPES = ['pdf_fiche', 'pdf_qrcode', 'pdf_affiche', 'image_photo', 'csv_export', 'json_export']
    FILE_TYPES = ['pdf', 'png', 'jpg', 'csv', 'json']
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'disparu_id': self.disparu_id,
            'disparu_public_id': self.disparu_public_id,
            'disparu_name': self.disparu_name,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'download_type': self.download_type,
            'ip_address': self.ip_address,
            'country': self.country,
            'city': self.city,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
