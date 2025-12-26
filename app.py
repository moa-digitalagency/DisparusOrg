import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext as _
from werkzeug.utils import secure_filename

db = SQLAlchemy()
babel = Babel()

COUNTRIES_CITIES = {
    "Algérie": ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Sétif", "Djelfa", "Biskra", "Tébessa"],
    "Angola": ["Luanda", "Huambo", "Lobito", "Benguela", "Lucapa", "Kuito", "Malanje", "Namibe", "Soyo", "Cabinda"],
    "Bénin": ["Cotonou", "Porto-Novo", "Parakou", "Djougou", "Bohicon", "Kandi", "Abomey", "Natitingou", "Lokossa", "Ouidah"],
    "Botswana": ["Gaborone", "Francistown", "Molepolole", "Serowe", "Maun", "Kanye", "Mahalapye", "Mogoditshane", "Lobatse", "Palapye"],
    "Burkina Faso": ["Ouagadougou", "Bobo-Dioulasso", "Koudougou", "Banfora", "Ouahigouya", "Pouytenga", "Kaya", "Tenkodogo", "Fada N'gourma", "Dédougou"],
    "Burundi": ["Bujumbura", "Gitega", "Muyinga", "Ngozi", "Ruyigi", "Kayanza", "Bururi", "Rumonge", "Makamba", "Cibitoke"],
    "Cameroun": ["Yaoundé", "Douala", "Garoua", "Bamenda", "Bafoussam", "Ngaoundéré", "Maroua", "Bertoua", "Buea", "Kribi", "Limbé", "Ebolowa", "Nkongsamba", "Kumba", "Foumban"],
    "Cap-Vert": ["Praia", "Mindelo", "Santa Maria", "Assomada", "Porto Novo", "São Filipe", "Tarrafal", "Espargos"],
    "Centrafrique": ["Bangui", "Bimbo", "Berbérati", "Carnot", "Bambari", "Bouar", "Bossangoa", "Bria", "Bangassou", "Nola"],
    "Comores": ["Moroni", "Mutsamudu", "Fomboni", "Domoni", "Sima", "Ouani", "Mirontsi", "Mbéni"],
    "Congo-Brazzaville": ["Brazzaville", "Pointe-Noire", "Dolisie", "Nkayi", "Impfondo", "Ouesso", "Madingou", "Owando", "Sibiti", "Loutété"],
    "Congo-Kinshasa": ["Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kananga", "Kisangani", "Bukavu", "Goma", "Tshikapa", "Kolwezi", "Likasi", "Matadi", "Butembo", "Kikwit", "Uvira", "Boma"],
    "Côte d'Ivoire": ["Abidjan", "Bouaké", "Yamoussoukro", "Daloa", "Korhogo", "San-Pédro", "Man", "Divo", "Gagnoa", "Abengourou", "Anyama", "Agboville", "Grand-Bassam", "Séguéla", "Bondoukou"],
    "Djibouti": ["Djibouti", "Ali Sabieh", "Tadjoura", "Obock", "Dikhil", "Arta"],
    "Égypte": ["Le Caire", "Alexandrie", "Gizeh", "Charm el-Cheikh", "Louxor", "Assouan", "Port-Saïd", "Suez", "Hurghada", "Mansourah", "Tanta", "Ismaïlia", "Fayoum", "Zagazig", "Damanhour"],
    "Érythrée": ["Asmara", "Keren", "Massawa", "Assab", "Mendefera", "Adi Keyh", "Barentu", "Dekemhare", "Senafe", "Ghinda"],
    "Eswatini": ["Mbabane", "Manzini", "Lobamba", "Siteki", "Piggs Peak", "Simunye", "Nhlangano", "Big Bend", "Mhlume"],
    "Éthiopie": ["Addis-Abeba", "Dire Dawa", "Mekele", "Gondar", "Bahir Dar", "Awassa", "Dessie", "Jimma", "Harar", "Adama", "Debre Markos", "Debre Berhan", "Kombolcha", "Arba Minch", "Dila"],
    "Gabon": ["Libreville", "Port-Gentil", "Franceville", "Oyem", "Moanda", "Mouila", "Lambaréné", "Tchibanga", "Koulamoutou", "Makokou"],
    "Gambie": ["Banjul", "Serekunda", "Brikama", "Bakau", "Farafenni", "Lamin", "Sukuta", "Brusubi", "Gunjur", "Soma"],
    "Ghana": ["Accra", "Kumasi", "Tamale", "Takoradi", "Ashaiman", "Sunyani", "Cape Coast", "Obuasi", "Tema", "Koforidua", "Ho", "Wa", "Bolgatanga", "Techiman", "Teshie"],
    "Guinée": ["Conakry", "Nzérékoré", "Kankan", "Kindia", "Labé", "Guéckédou", "Mamou", "Kissidougou", "Siguiri", "Boké", "Faranah", "Dabola", "Fria", "Pita", "Macenta"],
    "Guinée-Bissau": ["Bissau", "Bafatá", "Gabú", "Bissorã", "Bolama", "Cacheu", "Catió", "Farim", "Mansôa", "Quinhámel"],
    "Guinée équatoriale": ["Malabo", "Bata", "Ebebiyín", "Aconibe", "Añisok", "Luba", "Evinayong", "Mongomo", "Mikomeseng", "Rebola"],
    "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Ruiru", "Kikuyu", "Thika", "Malindi", "Naivasha", "Machakos", "Nyeri", "Meru", "Lamu", "Garissa"],
    "Lesotho": ["Maseru", "Teyateyaneng", "Mafeteng", "Hlotse", "Mohale's Hoek", "Quthing", "Qacha's Nek", "Butha-Buthe", "Mokhotlong", "Thaba-Tseka"],
    "Liberia": ["Monrovia", "Gbarnga", "Kakata", "Bensonville", "Harper", "Voinjama", "Buchanan", "Zwedru", "Sanniquellie", "Greenville"],
    "Libye": ["Tripoli", "Benghazi", "Misrata", "Zawiya", "Zliten", "Khoms", "Bayda", "Ajdabiya", "Tobrouk", "Sabha", "Syrte", "Derna", "Gharyan", "Bani Walid", "Tarhuna"],
    "Madagascar": ["Antananarivo", "Toamasina", "Antsirabe", "Fianarantsoa", "Mahajanga", "Toliara", "Antsiranana", "Nosy Be", "Morondava", "Ambatondrazaka", "Antalaha", "Manakara", "Sambava", "Fort-Dauphin", "Maintirano"],
    "Malawi": ["Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Kasungu", "Mangochi", "Karonga", "Salima", "Nkhotakota", "Liwonde"],
    "Mali": ["Bamako", "Sikasso", "Mopti", "Koutiala", "Ségou", "Kayes", "Gao", "Kati", "San", "Tombouctou", "Kolokani", "Niono", "Markala", "Bougouni", "Yanfolila"],
    "Maroc": ["Casablanca", "Rabat", "Fès", "Marrakech", "Tanger", "Agadir", "Meknès", "Oujda", "Kenitra", "Tétouan", "Salé", "Nador", "Mohammedia", "El Jadida", "Essaouira"],
    "Maurice": ["Port-Louis", "Beau Bassin-Rose Hill", "Vacoas-Phoenix", "Curepipe", "Quatre Bornes", "Triolet", "Goodlands", "Centre de Flacq", "Mahébourg", "Saint-Pierre"],
    "Mauritanie": ["Nouakchott", "Nouadhibou", "Kiffa", "Kaédi", "Rosso", "Zouérat", "Atar", "Néma", "Aleg", "Sélibabi"],
    "Mozambique": ["Maputo", "Matola", "Beira", "Nampula", "Chimoio", "Nacala", "Quelimane", "Tete", "Xai-Xai", "Maxixe", "Lichinga", "Pemba", "Inhambane", "Gurué", "Cuamba"],
    "Namibie": ["Windhoek", "Rundu", "Walvis Bay", "Oshakati", "Swakopmund", "Katima Mulilo", "Grootfontein", "Rehoboth", "Otjiwarongo", "Okahandja"],
    "Niger": ["Niamey", "Zinder", "Maradi", "Agadez", "Tahoua", "Dosso", "Diffa", "Tillabéri", "Arlit", "Birni N'Konni", "Tessaoua", "Mirriah", "Gaya", "Madaoua", "Magaria"],
    "Nigeria": ["Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Benin City", "Kaduna", "Maiduguri", "Zaria", "Aba", "Jos", "Ilorin", "Oyo", "Enugu", "Abeokuta", "Onitsha", "Warri", "Sokoto", "Calabar", "Uyo"],
    "Ouganda": ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Mbale", "Mukono", "Nansana", "Kasese", "Masaka", "Entebbe", "Fort Portal", "Hoima", "Arua", "Soroti"],
    "Rwanda": ["Kigali", "Butare", "Gitarama", "Ruhengeri", "Gisenyi", "Byumba", "Cyangugu", "Nyanza", "Kibungo", "Kibuye"],
    "Sao Tomé-et-Principe": ["São Tomé", "Santo António", "Neves", "Santana", "Trindade", "Santa Catarina", "Guadalupe", "Pantufo"],
    "Sénégal": ["Dakar", "Touba", "Thiès", "Rufisque", "Kaolack", "Mbour", "Saint-Louis", "Ziguinchor", "Diourbel", "Louga", "Tambacounda", "Richard-Toll", "Kolda", "Mbacké", "Tivaouane"],
    "Seychelles": ["Victoria", "Anse Boileau", "Beau Vallon", "Anse Royale", "Baie Lazare", "Takamaka", "Port Glaud", "Grand'Anse Mahé"],
    "Sierra Leone": ["Freetown", "Bo", "Kenema", "Koidu", "Makeni", "Lunsar", "Port Loko", "Kabala", "Waterloo", "Bonthe"],
    "Somalie": ["Mogadiscio", "Hargeisa", "Kismayo", "Marka", "Berbera", "Baidoa", "Burao", "Bosaso", "Galkayo", "Beledweyne"],
    "Soudan": ["Khartoum", "Omdurman", "Port-Soudan", "Kassala", "El-Obeid", "Nyala", "Wad Madani", "El-Fasher", "Gedaref", "Atbara"],
    "Soudan du Sud": ["Djouba", "Wau", "Malakal", "Yei", "Bor", "Aweil", "Bentiu", "Rumbek", "Torit", "Nimule"],
    "Tanzanie": ["Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya", "Morogoro", "Tanga", "Zanzibar", "Kigoma", "Moshi", "Tabora", "Iringa", "Songea", "Shinyanga", "Bukoba"],
    "Tchad": ["N'Djamena", "Moundou", "Abéché", "Sarh", "Kélo", "Koumra", "Pala", "Am Timan", "Mongo", "Bongor"],
    "Togo": ["Lomé", "Sokodé", "Kara", "Kpalimé", "Atakpamé", "Bassar", "Tsévié", "Aného", "Mango", "Dapaong"],
    "Tunisie": ["Tunis", "Sfax", "Sousse", "Ettadhamen", "Kairouan", "Gabès", "Bizerte", "Ariana", "Gafsa", "El Mourouj", "Monastir", "Ben Arous", "La Marsa", "Médenine", "Nabeul"],
    "Zambie": ["Lusaka", "Kitwe", "Ndola", "Kabwe", "Chingola", "Mufulira", "Livingstone", "Luanshya", "Kasama", "Chipata"],
    "Zimbabwe": ["Harare", "Bulawayo", "Chitungwiza", "Mutare", "Gweru", "Epworth", "Kwekwe", "Kadoma", "Masvingo", "Chinhoyi"]
}

def get_countries():
    return sorted(COUNTRIES_CITIES.keys())

def get_cities(country):
    return COUNTRIES_CITIES.get(country, [])

def get_locale():
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')

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


class ModerationReport(db.Model):
    __tablename__ = 'moderation_reports_flask'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    
    reason = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    reporter_contact = db.Column(db.String(200))
    
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.String(100))
    reviewed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=db.func.now())


def generate_public_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    app.jinja_env.globals['get_locale'] = get_locale
    
    register_routes(app)
    
    return app


def register_routes(app):
    
    @app.route('/')
    def index():
        recent = Disparu.query.filter_by(status='missing').order_by(Disparu.created_at.desc()).limit(6).all()
        stats = {
            'total': Disparu.query.count(),
            'found': Disparu.query.filter_by(status='found').count(),
            'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
            'contributions': Contribution.query.count(),
        }
        all_disparus = Disparu.query.filter(Disparu.latitude.isnot(None)).all()
        return render_template('index.html', recent=recent, stats=stats, countries=get_countries(), all_disparus=all_disparus)
    
    @app.route('/recherche')
    def search():
        query = request.args.get('q', '')
        status_filter = request.args.get('status', 'all')
        person_type = request.args.get('type', 'all')
        country = request.args.get('country', '')
        has_photo = request.args.get('photo', '') == 'on'
        
        q = Disparu.query
        
        if query:
            search_term = f"%{query}%"
            q = q.filter(
                db.or_(
                    Disparu.first_name.ilike(search_term),
                    Disparu.last_name.ilike(search_term),
                    Disparu.public_id.ilike(search_term),
                    Disparu.city.ilike(search_term),
                )
            )
        
        if status_filter and status_filter != 'all':
            q = q.filter_by(status=status_filter)
        
        if person_type and person_type != 'all':
            q = q.filter_by(person_type=person_type)
        
        if country:
            q = q.filter_by(country=country)
        
        if has_photo:
            q = q.filter(Disparu.photo_url.isnot(None))
        
        results = q.order_by(Disparu.created_at.desc()).limit(100).all()
        
        return render_template('search.html', 
                             results=results, 
                             query=query,
                             status_filter=status_filter,
                             person_type=person_type,
                             country=country,
                             countries=get_countries())
    
    @app.route('/signaler', methods=['GET', 'POST'])
    def report():
        if request.method == 'POST':
            try:
                photo_url = None
                if 'photo' in request.files:
                    file = request.files['photo']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        unique_name = f"{generate_public_id()}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                        file.save(filepath)
                        photo_url = f"/static/uploads/{unique_name}"
                
                contacts = []
                for i in range(3):
                    name = request.form.get(f'contact_name_{i}')
                    phone = request.form.get(f'contact_phone_{i}')
                    if name and phone:
                        contacts.append({
                            'name': name,
                            'phone': phone,
                            'email': request.form.get(f'contact_email_{i}', ''),
                            'relation': request.form.get(f'contact_relation_{i}', '')
                        })
                
                lat = request.form.get('latitude')
                lng = request.form.get('longitude')
                
                disparu = Disparu(
                    public_id=generate_public_id(),
                    person_type=request.form['person_type'],
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    age=int(request.form['age']),
                    sex=request.form['sex'],
                    country=request.form['country'],
                    city=request.form['city'],
                    physical_description=request.form['physical_description'],
                    photo_url=photo_url,
                    disappearance_date=datetime.fromisoformat(request.form['disappearance_date']),
                    circumstances=request.form['circumstances'],
                    latitude=float(lat) if lat else None,
                    longitude=float(lng) if lng else None,
                    clothing=request.form.get('clothing', ''),
                    objects=request.form.get('objects', ''),
                    contacts=contacts,
                )
                
                db.session.add(disparu)
                db.session.commit()
                
                return redirect(url_for('detail', public_id=disparu.public_id))
            
            except Exception as e:
                db.session.rollback()
                return render_template('report.html', 
                                     countries=get_countries(),
                                     countries_cities=COUNTRIES_CITIES,
                                     error=str(e))
        
        return render_template('report.html', 
                             countries=get_countries(),
                             countries_cities=COUNTRIES_CITIES)
    
    @app.route('/disparu/<public_id>')
    def detail(public_id):
        disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
        contributions = Contribution.query.filter_by(disparu_id=disparu.id).order_by(Contribution.created_at.desc()).all()
        return render_template('detail.html', person=disparu, contributions=contributions)
    
    @app.route('/disparu/<public_id>/contribute', methods=['POST'])
    def contribute(public_id):
        disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
        
        try:
            proof_url = None
            if 'proof' in request.files:
                file = request.files['proof']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_name = f"proof_{generate_public_id()}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                    file.save(filepath)
                    proof_url = f"/static/uploads/{unique_name}"
            
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')
            obs_date = request.form.get('observation_date')
            
            contribution = Contribution(
                disparu_id=disparu.id,
                contribution_type=request.form['contribution_type'],
                details=request.form['details'],
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                location_name=request.form.get('location_name', ''),
                observation_date=datetime.fromisoformat(obs_date) if obs_date else None,
                proof_url=proof_url,
                person_state=request.form.get('person_state'),
                return_circumstances=request.form.get('return_circumstances'),
                contact_name=request.form.get('contact_name'),
                contact_phone=request.form.get('contact_phone'),
                contact_email=request.form.get('contact_email'),
            )
            
            if request.form['contribution_type'] == 'found':
                disparu.status = 'found'
            
            db.session.add(contribution)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
        
        return redirect(url_for('detail', public_id=public_id))
    
    @app.route('/disparu/<public_id>/report', methods=['POST'])
    def report_content(public_id):
        disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
        
        try:
            report = ModerationReport(
                target_type='disparu',
                target_id=disparu.id,
                reason=request.form['reason'],
                details=request.form.get('details'),
                reporter_contact=request.form.get('reporter_contact'),
            )
            
            db.session.add(report)
            disparu.is_flagged = True
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        
        return redirect(url_for('detail', public_id=public_id))
    
    @app.route('/moderation')
    def moderation():
        reports = ModerationReport.query.filter_by(status='pending').order_by(ModerationReport.created_at.desc()).all()
        flagged = Disparu.query.filter_by(is_flagged=True).all()
        stats = {
            'pending': len(reports),
            'flagged': len(flagged),
            'total_disparus': Disparu.query.count(),
            'total_contributions': Contribution.query.count(),
        }
        return render_template('moderation.html', reports=reports, flagged_disparus=flagged, stats=stats)
    
    @app.route('/moderation/<int:report_id>/resolve', methods=['POST'])
    def resolve_report(report_id):
        report = ModerationReport.query.get_or_404(report_id)
        
        report.status = 'resolved'
        report.reviewed_by = 'admin'
        report.reviewed_at = datetime.utcnow()
        
        action = request.form.get('action')
        
        if action == 'remove':
            if report.target_type == 'disparu':
                disparu = Disparu.query.get(report.target_id)
                if disparu:
                    db.session.delete(disparu)
        elif action == 'unflag':
            if report.target_type == 'disparu':
                disparu = Disparu.query.get(report.target_id)
                if disparu:
                    disparu.is_flagged = False
        
        db.session.commit()
        return redirect(url_for('moderation'))
    
    @app.route('/admin')
    def admin():
        disparus = Disparu.query.order_by(Disparu.created_at.desc()).all()
        stats = {
            'total': Disparu.query.count(),
            'missing': Disparu.query.filter_by(status='missing').count(),
            'found': Disparu.query.filter_by(status='found').count(),
            'deceased': Disparu.query.filter_by(status='deceased').count(),
            'flagged': Disparu.query.filter_by(is_flagged=True).count(),
            'contributions': Contribution.query.count(),
            'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        }
        return render_template('admin.html', disparus=disparus, stats=stats, countries=get_countries())
    
    @app.route('/set-locale/<locale>')
    def set_locale(locale):
        if locale in ['fr', 'en']:
            response = make_response(redirect(request.referrer or url_for('index')))
            response.set_cookie('locale', locale, max_age=60*60*24*365)
            return response
        return redirect(url_for('index'))
    
    @app.route('/api/disparus')
    def api_disparus():
        disparus = Disparu.query.order_by(Disparu.created_at.desc()).limit(100).all()
        return jsonify([d.to_dict() for d in disparus])
    
    @app.route('/api/disparus/<public_id>')
    def api_disparu(public_id):
        disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
        data = disparu.to_dict()
        data['contributions'] = [c.to_dict() for c in disparu.contributions.all()]
        return jsonify(data)
    
    @app.route('/api/stats')
    def api_stats():
        return jsonify({
            'total': Disparu.query.count(),
            'found': Disparu.query.filter_by(status='found').count(),
            'missing': Disparu.query.filter_by(status='missing').count(),
            'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
            'contributions': Contribution.query.count(),
        })
    
    @app.route('/api/countries')
    def api_countries():
        return jsonify(COUNTRIES_CITIES)
    
    @app.route('/api/cities/<country>')
    def api_cities(country):
        return jsonify(get_cities(country))
    
    @app.route('/manifest.json')
    def manifest():
        return jsonify({
            "name": "DISPARUS.ORG",
            "short_name": "Disparus",
            "description": "Plateforme citoyenne de signalement de personnes disparues en Afrique",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#b91c1c",
            "icons": [
                {"src": "/static/favicon.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/static/favicon.png", "sizes": "512x512", "type": "image/png"}
            ]
        })
    
    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
