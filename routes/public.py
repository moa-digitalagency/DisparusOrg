"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Routes publiques
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename

from models import db, Disparu, Contribution, ModerationReport, ActivityLog, SiteSetting
from utils.geo import get_countries, get_cities, COUNTRIES_CITIES, get_total_cities
from services.signalement import create_signalement, generate_public_id
from security.rate_limit import rate_limit

public_bp = Blueprint('public', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIMETYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}


def allowed_file(filename, file_obj=None):
    """Validate file extension and optionally MIME type"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if file_obj and file_obj.content_type:
        if file_obj.content_type not in ALLOWED_MIMETYPES:
            return False
    return True


def log_public_activity(action, action_type='view', target_type=None, target_id=None, target_name=None):
    """Log public page views"""
    try:
        log = ActivityLog(
            username='visiteur',
            action=action,
            action_type=action_type,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            target_name=target_name,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500],
            severity='info',
            is_security_event=False
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_locale():
    from flask import request
    locale = request.cookies.get('locale')
    if locale in ['fr', 'en']:
        return locale
    return request.accept_languages.best_match(['fr', 'en'], default='fr')


@public_bp.route('/')
def index():
    log_public_activity('Page accueil', target_type='home')

    default_filter = SiteSetting.get('default_search_filter', 'all')

    recent_query = Disparu.query.filter_by(status='missing')
    if default_filter != 'all':
        if default_filter == 'person':
            recent_query = recent_query.filter(Disparu.person_type.in_(['child', 'adult', 'elderly']))
        elif default_filter == 'animal':
            recent_query = recent_query.filter_by(person_type='animal')
        else:
            recent_query = recent_query.filter_by(person_type=default_filter)
    recent = recent_query.order_by(Disparu.created_at.desc()).limit(6).all()

    stats = {
        'total': Disparu.query.count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        'contributions': Contribution.query.count(),
    }

    map_query = db.session.query(
        Disparu.id,
        Disparu.first_name,
        Disparu.last_name,
        Disparu.photo_url,
        Disparu.latitude,
        Disparu.longitude,
        Disparu.city,
        Disparu.country,
        Disparu.status,
        Disparu.person_type
    ).filter(Disparu.latitude.isnot(None))

    # We do not filter map data here to allow frontend toggling
    # if default_filter != 'all':
    #    map_query = map_query.filter(Disparu.person_type == default_filter)

    all_disparus_raw = map_query.all()

    all_disparus = [{
        'id': d.id,
        'full_name': f"{d.first_name} {d.last_name}" if d.person_type != 'animal' else d.first_name,
        'photo_url': d.photo_url,
        'latitude': d.latitude,
        'longitude': d.longitude,
        'city': d.city,
        'country': d.country,
        'status': d.status,
        'person_type': d.person_type
    } for d in all_disparus_raw]

    total_cities = get_total_cities()
    return render_template('index.html', recent=recent, stats=stats, countries=get_countries(), all_disparus=all_disparus, total_cities=total_cities, default_filter=default_filter)


@public_bp.route('/recherche')
def search():
    log_public_activity('Page recherche', target_type='search')

    default_filter = SiteSetting.get('default_search_filter', 'all')

    query = request.args.get('q', '')
    status_filter = request.args.get('status', 'all')
    person_type = request.args.get('type', default_filter)
    country = request.args.get('country', '')
    has_photo = request.args.get('photo', '') == 'on'
    
    q = Disparu.query
    
    if query:
        # Optimized search for Postgres (uses Full Text Search)
        if db.session.get_bind().dialect.name == 'postgresql':
            # Use Full Text Search with exact index matching
            # We use db.text to ensure the SQL matches the index definition exactly (literals vs params)
            # The index uses: to_tsvector('french', coalesce(first_name,'') || ' ' || ...)
            # plainto_tsquery handles user input safety (e.g. spaces, special chars)
            # Note: This performs word-based matching rather than substring matching

            sql_search = db.text("""
                to_tsvector('french',
                    coalesce(first_name,'') || ' ' ||
                    coalesce(last_name,'') || ' ' ||
                    coalesce(public_id,'') || ' ' ||
                    coalesce(city,'')
                ) @@ plainto_tsquery('french', :query)
            """)
            q = q.filter(sql_search).params(query=query)
        else:
            # Fallback for SQLite/Other (Leading wildcard scan)
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
        if person_type == 'person':
            q = q.filter(Disparu.person_type.in_(['child', 'adult', 'elderly']))
        else:
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
@rate_limit(max_requests=10, window=3600)
def report():
    if request.method == 'GET':
        log_public_activity('Page signaler', target_type='report')
    if request.method == 'POST':
        try:
            if not request.form.get('consent'):
                raise ValueError("Vous devez accepter les conditions pour publier un signalement.")

            photo_url = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    if not allowed_file(filename, file):
                        flash('Type de fichier non autorise. Utilisez PNG, JPG, GIF ou WebP.', 'error')
                        return redirect(url_for('public.report'))
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
            
            person_type = request.form['person_type']
            animal_type = None
            breed = None
            last_name = request.form.get('last_name')

            circumstances = request.form.get('circumstances', '')
            objects = request.form.get('objects', '')

            if person_type == 'animal':
                animal_type = request.form.get('animal_type')
                breed = request.form.get('breed')
                # Handle NOT NULL constraint for last_name
                if not last_name:
                    last_name = "-"
                # Force empty strings for animal
                circumstances = ""
                objects = ""

            disparu = Disparu(
                public_id=generate_public_id(),
                person_type=person_type,
                animal_type=animal_type,
                breed=breed,
                first_name=request.form['first_name'],
                last_name=last_name,
                age=int(request.form.get('age')) if request.form.get('age') else -1,
                sex=request.form['sex'],
                country=request.form['country'],
                city=request.form['city'],
                physical_description=request.form['physical_description'],
                photo_url=photo_url,
                disappearance_date=datetime.fromisoformat(request.form['disappearance_date']),
                circumstances=circumstances,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                clothing=request.form.get('clothing', ''),
                objects=objects,
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
    log_public_activity('Fiche disparu', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
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
@rate_limit(max_requests=20, window=3600)
def contribute(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    log_public_activity('Contribution ajoutee', action_type='create', target_type='contribution', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
    
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
@rate_limit(max_requests=5, window=3600)
def report_content(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    log_public_activity('Signalement contenu', action_type='create', target_type='moderation', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
    
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


@public_bp.route('/disparu/<public_id>/pdf')
def download_pdf(public_id):
    from flask import Response
    from utils.pdf_gen import generate_missing_person_pdf
    
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    log_public_activity('Telechargement PDF', action_type='download', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
    
    try:
        from models import Download
        download = Download(
            disparu_public_id=public_id,
            file_type='pdf',
            download_type='pdf_fiche',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(download)
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    base_url = request.url_root.rstrip('/')
    pdf_buffer = generate_missing_person_pdf(disparu, base_url)
    
    if pdf_buffer is None:
        flash('Erreur lors de la generation du PDF', 'error')
        return redirect(url_for('public.detail', public_id=public_id))
    
    filename = f"disparu_{public_id}.pdf"
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@public_bp.route('/disparu/<public_id>/share-image')
def download_share_image(public_id):
    from flask import Response
    from utils.pdf_gen import generate_social_media_image
    
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    log_public_activity('Telechargement image partage', action_type='download', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
    
    try:
        from models import Download
        download = Download(
            disparu_public_id=public_id,
            file_type='png',
            download_type='image_social',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(download)
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    base_url = request.url_root.rstrip('/')
    image_buffer = generate_social_media_image(disparu, base_url)
    
    if image_buffer is None:
        flash('Erreur lors de la generation de l\'image', 'error')
        return redirect(url_for('public.detail', public_id=public_id))
    
    filename = f"disparu_{public_id}_partage.png"
    return Response(
        image_buffer.getvalue(),
        mimetype='image/png',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@public_bp.route('/disparu/<public_id>/qrcode')
def download_qrcode(public_id):
    from flask import Response
    from utils.pdf_gen import generate_qr_code
    
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    log_public_activity('Telechargement QR code', action_type='download', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
    
    try:
        from models import Download
        download = Download(
            disparu_public_id=public_id,
            file_type='png',
            download_type='pdf_qrcode',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(download)
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    base_url = request.url_root.rstrip('/')
    qr_url = f"{base_url}/disparu/{public_id}"
    qr_buffer = generate_qr_code(qr_url, size=15)
    
    if qr_buffer is None:
        flash('Erreur lors de la generation du QR code', 'error')
        return redirect(url_for('public.detail', public_id=public_id))
    
    filename = f"qrcode_{public_id}.png"
    return Response(
        qr_buffer.getvalue(),
        mimetype='image/png',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@public_bp.route('/set-locale/<locale>')
def set_locale(locale):
    if locale in ['fr', 'en']:
        from flask import make_response
        response = make_response(redirect(request.referrer or url_for('public.index')))
        response.set_cookie('locale', locale, max_age=365*24*60*60)
        return response
    return redirect(url_for('public.index'))


@public_bp.route('/robots.txt')
def robots():
    from flask import Response
    base_url = 'https://disparus.org'
    
    robots_content = f"""# Robots.txt for {base_url}
# Plateforme citoyenne pour les personnes disparues en Afrique

User-agent: *
Allow: /
Allow: /recherche
Allow: /disparu/
Allow: /signaler

# Pages admin - Ne pas indexer
Disallow: /admin/
Disallow: /admin/*
Disallow: /api/
Disallow: /moderation

# Fichiers statiques autorises
Allow: /statics/
Allow: /manifest.json

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Autoriser les moteurs IA
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Anthropic-AI
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Googlebot
Allow: /

# Crawl-delay pour eviter la surcharge
Crawl-delay: 1
"""
    return Response(robots_content, mimetype='text/plain')


@public_bp.route('/sitemap.xml')
def sitemap():
    from flask import Response
    from datetime import datetime
    
    base_url = 'https://disparus.org'
    today = datetime.now().strftime('%Y-%m-%d')
    
    def generate_sitemap():
        yield '<?xml version="1.0" encoding="UTF-8"?>\n'
        yield '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        yield f'''  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
'''

        yield f'''  <url>
    <loc>{base_url}/recherche</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
'''

        yield f'''  <url>
    <loc>{base_url}/signaler</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''

        # Optimize memory usage by fetching only necessary columns and yielding results
        query = Disparu.query.with_entities(Disparu.public_id, Disparu.updated_at)\
            .filter(Disparu.status.in_(['missing', 'found']))\
            .order_by(Disparu.updated_at.desc())\
            .execution_options(yield_per=1000)

        for public_id, updated_at in query:
            last_mod = updated_at.strftime('%Y-%m-%d') if updated_at else today
            yield f'''  <url>
    <loc>{base_url}/disparu/{public_id}</loc>
    <lastmod>{last_mod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>
'''

        yield '</urlset>'
    
    return Response(generate_sitemap(), mimetype='application/xml')
