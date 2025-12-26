from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, make_response
from flask_babel import gettext as _
from app import db
from app.models import Disparu, Contribution, ModerationReport, COUNTRIES_CITIES

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page."""
    disparus = Disparu.query.filter_by(status='missing').order_by(Disparu.created_at.desc()).limit(6).all()
    
    stats = {
        'total': Disparu.query.count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        'contributions': Contribution.query.count(),
    }
    
    markers = []
    for d in Disparu.query.filter(Disparu.latitude.isnot(None), Disparu.longitude.isnot(None)).all():
        markers.append({
            'lat': d.latitude,
            'lng': d.longitude,
            'name': f"{d.first_name} {d.last_name}",
            'id': d.public_id,
            'photo_url': d.photo_url,
        })
    
    return render_template('index.html', 
                         disparus=disparus, 
                         stats=stats, 
                         markers=markers,
                         countries=list(COUNTRIES_CITIES.keys()))

@bp.route('/recherche')
def search():
    """Search page."""
    query = request.args.get('q', '')
    status_filter = request.args.get('status', 'all')
    person_type = request.args.get('personType', 'all')
    country = request.args.get('country', '')
    
    q = Disparu.query
    
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            db.or_(
                Disparu.first_name.ilike(search_term),
                Disparu.last_name.ilike(search_term),
                Disparu.public_id.ilike(search_term),
                Disparu.city.ilike(search_term),
                Disparu.country.ilike(search_term),
            )
        )
    
    if status_filter and status_filter != 'all':
        q = q.filter_by(status=status_filter)
    
    if person_type and person_type != 'all':
        q = q.filter_by(person_type=person_type)
    
    if country:
        q = q.filter_by(country=country)
    
    disparus = q.order_by(Disparu.created_at.desc()).limit(100).all()
    
    return render_template('search.html', 
                         disparus=disparus,
                         query=query,
                         status_filter=status_filter,
                         person_type=person_type,
                         country_filter=country,
                         countries=list(COUNTRIES_CITIES.keys()))

@bp.route('/signaler', methods=['GET', 'POST'])
def report():
    """Report form page."""
    if request.method == 'POST':
        try:
            data = request.form
            
            disappearance_date = datetime.strptime(data['disappearance_date'], '%Y-%m-%d') if data.get('disappearance_date') else datetime.utcnow()
            
            disparu = Disparu(
                person_type=data['person_type'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=int(data['age']),
                sex=data['sex'],
                country=data['country'],
                city=data['city'],
                latitude=float(data['latitude']) if data.get('latitude') else None,
                longitude=float(data['longitude']) if data.get('longitude') else None,
                physical_description=data['physical_description'],
                photo_url=data.get('photo_url'),
                disappearance_date=disappearance_date,
                circumstances=data['circumstances'],
                clothing=data['clothing'],
                belongings=data.get('belongings'),
                contact_name=data['contact_name'],
                contact_phone=data['contact_phone'],
                contact_email=data.get('contact_email'),
                contact_relation=data.get('contact_relation'),
            )
            
            db.session.add(disparu)
            db.session.commit()
            
            return redirect(url_for('main.detail', public_id=disparu.public_id))
        except Exception as e:
            db.session.rollback()
            return render_template('report.html', 
                                 error=str(e),
                                 countries=COUNTRIES_CITIES)
    
    return render_template('report.html', countries=COUNTRIES_CITIES)

@bp.route('/disparu/<public_id>')
def detail(public_id):
    """Detail page."""
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    
    disparu.view_count += 1
    db.session.commit()
    
    contributions = Contribution.query.filter_by(disparu_id=disparu.id).order_by(Contribution.created_at.desc()).all()
    
    return render_template('detail.html', 
                         disparu=disparu,
                         contributions=contributions)

@bp.route('/disparu/<public_id>/contribute', methods=['POST'])
def contribute(public_id):
    """Add contribution."""
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    
    try:
        data = request.form
        
        observation_date = datetime.strptime(data['observation_date'], '%Y-%m-%d') if data.get('observation_date') else None
        
        contribution = Contribution(
            disparu_id=disparu.id,
            contribution_type=data['contribution_type'],
            latitude=float(data['latitude']) if data.get('latitude') else None,
            longitude=float(data['longitude']) if data.get('longitude') else None,
            observation_date=observation_date,
            details=data['details'],
            proof_url=data.get('proof_url'),
            found_state=data.get('found_state'),
            return_circumstances=data.get('return_circumstances'),
            contact_name=data.get('contact_name'),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email'),
        )
        
        db.session.add(contribution)
        
        if data['contribution_type'] == 'found' and data.get('found_state'):
            disparu.status = 'deceased' if data['found_state'] == 'deceased' else 'found'
            disparu.found_state = data['found_state']
            disparu.found_circumstances = data.get('return_circumstances')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
    
    return redirect(url_for('main.detail', public_id=public_id))

@bp.route('/disparu/<public_id>/report', methods=['POST'])
def report_content(public_id):
    """Report content for moderation."""
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    
    try:
        data = request.form
        
        report = ModerationReport(
            target_type='disparu',
            target_id=disparu.id,
            reason=data['reason'],
            details=data.get('details'),
            reporter_contact=data.get('reporter_contact'),
        )
        
        db.session.add(report)
        disparu.is_flagged = True
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
    
    return redirect(url_for('main.detail', public_id=public_id))

@bp.route('/set-locale/<locale>')
def set_locale(locale):
    """Set language preference."""
    if locale in ['fr', 'en']:
        response = make_response(redirect(request.referrer or url_for('main.index')))
        response.set_cookie('locale', locale, max_age=60*60*24*365)
        return response
    return redirect(url_for('main.index'))

@bp.route('/api/disparus')
def api_disparus():
    """API endpoint for disparus."""
    query = request.args.get('query', '')
    status_filter = request.args.get('status', 'all')
    person_type = request.args.get('personType', 'all')
    country = request.args.get('country', '')
    
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
    
    disparus = q.order_by(Disparu.created_at.desc()).limit(100).all()
    
    return jsonify([d.to_dict() for d in disparus])

@bp.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    return jsonify({
        'total': Disparu.query.count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or len(COUNTRIES_CITIES),
        'contributions': Contribution.query.count(),
    })

@bp.route('/api/countries')
def api_countries():
    """API endpoint for countries and cities."""
    return jsonify(COUNTRIES_CITIES)

@bp.route('/manifest.json')
def manifest():
    """PWA manifest."""
    return jsonify({
        "name": "DISPARUS.ORG",
        "short_name": "Disparus",
        "description": "Plateforme citoyenne de signalement de personnes disparues en Afrique",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#b91c1c",
        "icons": [
            {
                "src": "/static/favicon.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    })

@bp.route('/sw.js')
def service_worker():
    """Service worker for offline support."""
    from flask import current_app, send_from_directory
    return send_from_directory(current_app.static_folder, 'sw.js', mimetype='application/javascript')

@bp.route('/moderation')
def moderation():
    """Moderation dashboard for reviewing flagged content."""
    reports = ModerationReport.query.filter_by(status='pending').order_by(ModerationReport.created_at.desc()).all()
    flagged_disparus = Disparu.query.filter_by(is_flagged=True).all()
    return render_template('moderation.html', reports=reports, flagged_disparus=flagged_disparus)

@bp.route('/moderation/<int:report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    """Resolve a moderation report."""
    report = ModerationReport.query.get_or_404(report_id)
    data = request.form
    
    report.status = data.get('status', 'resolved')
    report.reviewed_by = data.get('reviewed_by', 'admin')
    report.reviewed_at = db.func.now()
    
    if data.get('action') == 'remove':
        if report.target_type == 'disparu':
            disparu = Disparu.query.get(report.target_id)
            if disparu:
                db.session.delete(disparu)
    elif data.get('action') == 'unflag':
        if report.target_type == 'disparu':
            disparu = Disparu.query.get(report.target_id)
            if disparu:
                disparu.is_flagged = False
    
    db.session.commit()
    return redirect(url_for('main.moderation'))
