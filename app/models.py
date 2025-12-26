import random
import string
from datetime import datetime
from app import db

def generate_public_id():
    """Generate 6-character alphanumeric ID."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choice(chars) for _ in range(6))

class Disparu(db.Model):
    __tablename__ = 'disparus_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(6), unique=True, nullable=False, default=generate_public_id)
    
    person_type = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(20), nullable=False)
    
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    physical_description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(500))
    disappearance_date = db.Column(db.DateTime, nullable=False)
    circumstances = db.Column(db.Text, nullable=False)
    clothing = db.Column(db.Text, nullable=False)
    belongings = db.Column(db.Text)
    
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(50), nullable=False)
    contact_email = db.Column(db.String(100))
    contact_relation = db.Column(db.String(50))
    
    status = db.Column(db.String(20), default='missing')
    found_state = db.Column(db.String(20))
    found_circumstances = db.Column(db.Text)
    found_latitude = db.Column(db.Float)
    found_longitude = db.Column(db.Float)
    
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contributions = db.relationship('Contribution', backref='disparu', lazy='dynamic', cascade='all, delete-orphan')
    
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
            'latitude': self.latitude,
            'longitude': self.longitude,
            'physical_description': self.physical_description,
            'photo_url': self.photo_url,
            'disappearance_date': self.disappearance_date.isoformat() if self.disappearance_date else None,
            'circumstances': self.circumstances,
            'clothing': self.clothing,
            'belongings': self.belongings,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'contact_relation': self.contact_relation,
            'status': self.status,
            'found_state': self.found_state,
            'is_verified': self.is_verified,
            'is_flagged': self.is_flagged,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Contribution(db.Model):
    __tablename__ = 'contributions_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    disparu_id = db.Column(db.Integer, db.ForeignKey('disparus_flask.id', ondelete='CASCADE'), nullable=False)
    
    contribution_type = db.Column(db.String(30), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    observation_date = db.Column(db.DateTime)
    details = db.Column(db.Text, nullable=False)
    proof_url = db.Column(db.String(500))
    
    found_state = db.Column(db.String(20))
    return_circumstances = db.Column(db.Text)
    return_latitude = db.Column(db.Float)
    return_longitude = db.Column(db.Float)
    
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'disparu_id': self.disparu_id,
            'contribution_type': self.contribution_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'observation_date': self.observation_date.isoformat() if self.observation_date else None,
            'details': self.details,
            'proof_url': self.proof_url,
            'found_state': self.found_state,
            'contact_name': self.contact_name,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ModerationReport(db.Model):
    __tablename__ = 'moderation_reports_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(30), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    reporter_contact = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.String(100))
    reviewed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


COUNTRIES_CITIES = {
    "Cameroun": ["Yaoundé", "Douala", "Garoua", "Bafoussam", "Bamenda", "Ngaoundéré", "Maroua", "Bertoua", "Ebolowa", "Kribi"],
    "Nigeria": ["Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Benin City", "Kaduna", "Enugu", "Onitsha", "Jos"],
    "Côte d'Ivoire": ["Abidjan", "Bouaké", "Yamoussoukro", "Daloa", "Gagnoa", "Korhogo", "San Pedro", "Man", "Divo", "Séguéla"],
    "Sénégal": ["Dakar", "Thiès", "Kaolack", "Ziguinchor", "Saint-Louis", "Mbour", "Touba", "Rufisque", "Diourbel", "Tambacounda"],
    "Ghana": ["Accra", "Kumasi", "Tamale", "Sekondi-Takoradi", "Cape Coast", "Obuasi", "Tema", "Teshie", "Koforidua", "Ho"],
    "RD Congo": ["Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kisangani", "Goma", "Bukavu", "Kananga", "Likasi", "Kolwezi", "Matadi"],
    "Mali": ["Bamako", "Sikasso", "Ségou", "Mopti", "Koutiala", "Kayes", "Gao", "Kidal", "Tombouctou", "San"],
    "Burkina Faso": ["Ouagadougou", "Bobo-Dioulasso", "Koudougou", "Banfora", "Ouahigouya", "Kaya", "Fada N'Gourma", "Tenkodogo", "Dédougou", "Dori"],
    "Niger": ["Niamey", "Zinder", "Maradi", "Tahoua", "Agadez", "Dosso", "Diffa", "Tillabéri", "Tessaoua", "Arlit"],
    "Guinée": ["Conakry", "Nzérékoré", "Kankan", "Kindia", "Labé", "Boké", "Mamou", "Siguiri", "Faranah", "Kissidougou"],
    "Bénin": ["Cotonou", "Porto-Novo", "Parakou", "Djougou", "Abomey", "Bohicon", "Natitingou", "Lokossa", "Ouidah", "Kandi"],
    "Togo": ["Lomé", "Sokodé", "Kara", "Kpalimé", "Atakpamé", "Bassar", "Tsévié", "Aného", "Mango", "Dapaong"],
    "Gabon": ["Libreville", "Port-Gentil", "Franceville", "Oyem", "Moanda", "Mouila", "Lambaréné", "Tchibanga", "Makokou", "Bitam"],
    "Rwanda": ["Kigali", "Butare", "Gitarama", "Ruhengeri", "Gisenyi", "Byumba", "Cyangugu", "Kibungo", "Kibuye", "Nyanza"],
    "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi", "Kitale", "Garissa", "Nyeri"],
    "Tanzanie": ["Dar es Salaam", "Dodoma", "Mwanza", "Arusha", "Zanzibar", "Mbeya", "Morogoro", "Tanga", "Kigoma", "Moshi"],
    "Ouganda": ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Mbale", "Masaka", "Entebbe", "Fort Portal", "Soroti"],
    "Éthiopie": ["Addis-Abeba", "Dire Dawa", "Mek'ele", "Gondar", "Bahir Dar", "Hawassa", "Jimma", "Dessie", "Harar", "Adama"],
    "Afrique du Sud": ["Johannesburg", "Le Cap", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley"],
    "Maroc": ["Casablanca", "Rabat", "Fès", "Marrakech", "Tanger", "Agadir", "Meknès", "Oujda", "Kenitra", "Tétouan"],
    "Algérie": ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Sétif", "Djelfa", "Biskra", "Tébessa"],
    "Tunisie": ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Gabès", "Ariana", "Gafsa", "Monastir", "Ben Arous"],
    "Égypte": ["Le Caire", "Alexandrie", "Gizeh", "Port-Saïd", "Suez", "Louxor", "Assouan", "Ismaïlia", "Tanta", "Zagazig"],
}
