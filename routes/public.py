import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

from models import db, Disparu, Contribution, ModerationReport
from utils.geo import get_countries, get_cities, COUNTRIES_CITIES, get_total_cities
from services.signalement import create_signalement, generate_public_id

public_bp = Blueprint('public', __name__)


def get_locale():
    from flask import request
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')


@public_bp.route('/')
def index():
    recent = Disparu.query.filter_by(status='missing').order_by(Disparu.created_at.desc()).limit(6).all()
    stats = {
        'total': Disparu.query.count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        'contributions': Contribution.query.count(),
    }
    all_disparus = Disparu.query.filter(Disparu.latitude.isnot(None)).all()
    total_cities = get_total_cities()
    return render_template('index.html', recent=recent, stats=stats, countries=get_countries(), all_disparus=all_disparus, total_cities=total_cities)


@public_bp.route('/recherche')
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


@public_bp.route('/signaler', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        try:
            photo_url = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_name = f"{generate_public_id()}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                    file.save(filepath)
                    photo_url = f"/statics/uploads/{unique_name}"
            
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
            
            return redirect(url_for('public.detail', public_id=disparu.public_id))
        
        except Exception as e:
            db.session.rollback()
            return render_template('report.html', 
                                 countries=get_countries(),
                                 countries_cities=COUNTRIES_CITIES,
                                 error=str(e))
    
    return render_template('report.html', 
                         countries=get_countries(),
                         countries_cities=COUNTRIES_CITIES)


@public_bp.route('/disparu/<public_id>')
def detail(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    try:
        db.session.execute(
            db.text("UPDATE disparus_flask SET view_count = COALESCE(view_count, 0) + 1 WHERE id = :id"),
            {"id": disparu.id}
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
    contributions = Contribution.query.filter_by(disparu_id=disparu.id).order_by(Contribution.created_at.desc()).all()
    return render_template('detail.html', person=disparu, contributions=contributions)


@public_bp.route('/disparu/<public_id>/contribute', methods=['POST'])
def contribute(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    
    try:
        proof_url = None
        if 'proof' in request.files:
            file = request.files['proof']
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_name = f"proof_{generate_public_id()}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(filepath)
                proof_url = f"/statics/uploads/{unique_name}"
        
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
    
    return redirect(url_for('public.detail', public_id=public_id))


@public_bp.route('/disparu/<public_id>/report', methods=['POST'])
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
    
    return redirect(url_for('public.detail', public_id=public_id))


@public_bp.route('/set-locale/<locale>')
def set_locale(locale):
    if locale in ['fr', 'en']:
        from flask import make_response
        response = make_response(redirect(request.referrer or url_for('public.index')))
        response.set_cookie('locale', locale, max_age=365*24*60*60)
        return response
    return redirect(url_for('public.index'))
