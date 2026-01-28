"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Routes pour l'administration
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
import json
import csv
import io
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response, make_response

from models import db, Disparu, Contribution, ModerationReport, User, Role, ActivityLog, Download, SiteSetting
from models.settings import invalidate_settings_cache
from services.analytics import get_platform_stats
from utils.geo import get_countries
from security.rate_limit import rate_limit

admin_bp = Blueprint('admin', __name__)


def log_activity(action, action_type='admin', target_type=None, target_id=None, target_name=None, severity='info', is_security=False):
    """Helper function to log admin activities"""
    try:
        log = ActivityLog()
        log.username = session.get('admin_username', 'system')
        log.action = action
        log.action_type = action_type
        log.target_type = target_type
        log.target_id = str(target_id) if target_id else None
        log.target_name = target_name
        log.ip_address = request.remote_addr
        log.user_agent = request.headers.get('User-Agent', '')[:500] if request.headers.get('User-Agent') else None
        log.severity = severity
        log.is_security_event = is_security
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        import logging
        logging.error(f"Error logging activity: {e}")
        try:
            db.session.rollback()
        except:
            pass


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=60)
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', '')
        
        if not admin_password:
            try:
                log_activity(f'Tentative connexion avec ADMIN_PASSWORD vide', action_type='auth', severity='error', is_security=True)
            except: pass
            error = 'Erreur configuration: Mot de passe admin non defini'
        elif username == admin_username and password == admin_password:
            session.permanent = True  # Enable session expiration
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_role'] = 'admin'
            
            try:
                log_activity('Connexion admin reussie', action_type='auth', severity='info', is_security=True)
            except Exception as e:
                import logging
                logging.warning(f"Could not log activity: {e}")
            
            return redirect(url_for('admin.dashboard'))
        else:
            try:
                log_activity(f'Tentative de connexion echouee pour: {username}', action_type='auth', severity='warning', is_security=True)
            except Exception as e:
                import logging
                logging.warning(f"Could not log activity: {e}")
            error = 'Identifiants invalides'
    
    return render_template('admin_login.html', error=error)


@admin_bp.route('/logout')
def logout():
    try:
        log_activity('Deconnexion admin', action_type='auth', severity='info', is_security=True)
    except Exception as e:
        import logging
        logging.warning(f"Could not log activity: {e}")
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@admin_required
def dashboard():
    try:
        log_activity('Consultation tableau de bord', action_type='view', target_type='dashboard')
    except Exception as e:
        import logging
        logging.warning(f"Could not log activity: {e}")
    stats = {
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'deceased': Disparu.query.filter_by(status='deceased').count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
    }
    # Optimization: Only fetch 5 recent for the list
    recent_disparus = Disparu.query.order_by(Disparu.created_at.desc()).limit(5).all()

    # Optimization: For map, fetch only needed fields to avoid hydrating all objects
    # Limit to 1000 most recent for performance
    map_data = db.session.query(
        Disparu.latitude, Disparu.longitude, Disparu.first_name,
        Disparu.last_name, Disparu.public_id, Disparu.status, Disparu.is_flagged
    ).filter(Disparu.latitude.isnot(None), Disparu.longitude.isnot(None))\
    .order_by(Disparu.created_at.desc())\
    .limit(1000).all()

    disparus_list = [{
        'latitude': d.latitude,
        'longitude': d.longitude,
        'first_name': d.first_name,
        'last_name': d.last_name,
        'public_id': d.public_id,
        'status': d.status,
        'is_flagged': d.is_flagged
    } for d in map_data]

    return render_template('admin.html', stats=stats, disparus=recent_disparus, disparus_list=disparus_list)


@admin_bp.route('/moderation')
@admin_required
def moderation():
    log_activity('Consultation moderation', action_type='view', target_type='moderation')
    reports = ModerationReport.query.filter_by(status='pending').order_by(ModerationReport.created_at.desc()).all()
    flagged = Disparu.query.filter_by(is_flagged=True).all()
    stats = {
        'pending': len(reports),
        'flagged': len(flagged),
        'total_disparus': Disparu.query.count(),
        'total_contributions': Contribution.query.count(),
    }
    return render_template('moderation.html', reports=reports, flagged_disparus=flagged, stats=stats)


@admin_bp.route('/moderation/<int:report_id>/resolve', methods=['POST'])
@admin_required
def resolve_report(report_id):
    report = ModerationReport.query.get_or_404(report_id)
    
    report.status = 'resolved'
    report.reviewed_by = session.get('admin_username', 'admin')
    report.reviewed_at = datetime.utcnow()
    
    action = request.form.get('action')
    
    if action == 'remove':
        if report.target_type == 'disparu':
            disparu = Disparu.query.get(report.target_id)
            if disparu:
                log_activity(f'Suppression fiche suite a moderation', action_type='delete', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}', severity='warning')
                db.session.delete(disparu)
    elif action == 'unflag':
        if report.target_type == 'disparu':
            disparu = Disparu.query.get(report.target_id)
            if disparu:
                disparu.is_flagged = False
    
    log_activity(f'Resolution signalement #{report_id} - Action: {action}', action_type='update', target_type='moderation', target_id=report_id, severity='info')
    db.session.commit()
    return redirect(url_for('admin.moderation'))


@admin_bp.route('/disparu/<int:disparu_id>/status', methods=['POST'])
@admin_required
def update_status(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    new_status = request.form.get('status')
    old_status = disparu.status
    if new_status in ['missing', 'found', 'deceased']:
        disparu.status = new_status
        log_activity(f'Changement statut: {old_status} -> {new_status}', action_type='update', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
        db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/disparu/<int:disparu_id>/delete', methods=['POST'])
@admin_required
def delete_disparu(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    name = f'{disparu.first_name} {disparu.last_name}'
    log_activity(f'Suppression fiche disparu', action_type='delete', target_type='disparu', target_id=disparu.id, target_name=name, severity='warning')
    db.session.delete(disparu)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reports')
@admin_required
def all_reports():
    log_activity('Consultation signalements', action_type='view', target_type='reports')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    country_filter = request.args.get('country', '')
    type_filter = request.args.get('type', '')
    
    query = Disparu.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if country_filter:
        query = query.filter_by(country=country_filter)
    
    if type_filter == 'person':
        query = query.filter(Disparu.person_type != 'animal')
    elif type_filter == 'animal':
        query = query.filter(Disparu.person_type == 'animal')

    disparus = query.order_by(Disparu.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    countries = db.session.query(Disparu.country).distinct().all()
    
    return render_template('admin_reports.html', 
                         disparus=disparus, 
                         countries=[c[0] for c in countries],
                         status_filter=status_filter,
                         country_filter=country_filter,
                         type_filter=type_filter)


@admin_bp.route('/contributions')
@admin_required
def contributions():
    log_activity('Consultation contributions', action_type='view', target_type='contributions')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    contributions = Contribution.query.order_by(Contribution.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_contributions.html', contributions=contributions)


@admin_bp.route('/statistics')
@admin_required
def statistics():
    log_activity('Consultation statistiques', action_type='view', target_type='statistics')
    total_views = db.session.query(db.func.sum(Disparu.view_count)).scalar() or 0
    total_downloads = Download.query.count()
    
    stats = {
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'deceased': Disparu.query.filter_by(status='deceased').count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        'pending_reports': ModerationReport.query.filter_by(status='pending').count(),
        'total_views': total_views,
        'total_downloads': total_downloads,
    }
    
    by_country = db.session.query(
        Disparu.country, 
        db.func.count(Disparu.id)
    ).group_by(Disparu.country).order_by(db.func.count(Disparu.id).desc()).limit(10).all()
    
    by_status = db.session.query(
        Disparu.status, 
        db.func.count(Disparu.id)
    ).group_by(Disparu.status).all()
    
    by_city = db.session.query(
        Disparu.city,
        Disparu.country,
        db.func.count(Disparu.id)
    ).group_by(Disparu.city, Disparu.country).order_by(db.func.count(Disparu.id).desc()).limit(10).all()
    
    most_viewed = Disparu.query.order_by(Disparu.view_count.desc()).limit(5).all()
    
    most_downloaded = db.session.query(
        Disparu.public_id,
        Disparu.first_name,
        Disparu.last_name,
        Disparu.city,
        Disparu.country,
        db.func.count(Download.id).label('download_count')
    ).join(Download, Download.disparu_public_id == Disparu.public_id).group_by(
        Disparu.public_id, Disparu.first_name, Disparu.last_name, Disparu.city, Disparu.country
    ).order_by(db.func.count(Download.id).desc()).limit(5).all()
    
    downloads_by_type = db.session.query(
        Download.file_type,
        db.func.count(Download.id)
    ).group_by(Download.file_type).order_by(db.func.count(Download.id).desc()).all()
    
    downloads_by_country = db.session.query(
        Download.country,
        db.func.count(Download.id)
    ).filter(Download.country.isnot(None)).group_by(Download.country).order_by(db.func.count(Download.id).desc()).limit(10).all()
    
    return render_template('admin_statistics.html', 
                         stats=stats, 
                         by_country=by_country, 
                         by_status=by_status,
                         by_city=by_city,
                         most_viewed=most_viewed,
                         most_downloaded=most_downloaded,
                         downloads_by_type=downloads_by_type,
                         downloads_by_country=downloads_by_country)


@admin_bp.route('/map')
@admin_required
def map_view():
    log_activity('Consultation carte', action_type='view', target_type='map')

    # Optimized query: select only needed fields
    results = db.session.query(
        Disparu.id,
        Disparu.public_id,
        Disparu.first_name,
        Disparu.last_name,
        Disparu.latitude,
        Disparu.longitude,
        Disparu.country,
        Disparu.city,
        Disparu.status,
        Disparu.is_flagged,
        Disparu.photo_url,
        Disparu.disappearance_date,
        Disparu.person_type
    ).all()

    disparus_list = []
    for row in results:
        disparus_list.append({
            'id': row.id,
            'public_id': row.public_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'latitude': row.latitude,
            'longitude': row.longitude,
            'country': row.country,
            'city': row.city,
            'status': row.status,
            'is_flagged': row.is_flagged,
            'photo_url': row.photo_url,
            'disappearance_date': row.disappearance_date.isoformat() if row.disappearance_date else None,
            'person_type': row.person_type
        })

    return render_template('admin_map.html', disparus=results, disparus_list=disparus_list)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'GET':
        log_activity('Consultation parametres', action_type='view', target_type='settings')
    if request.method == 'POST':
        import os
        from werkzeug.utils import secure_filename
        
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico'}
        ALLOWED_MIMETYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/x-icon', 'image/vnd.microsoft.icon'}
        
        def allowed_file(filename, file_obj):
            if '.' not in filename:
                return False
            ext = filename.rsplit('.', 1)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return False
            if file_obj.content_type and file_obj.content_type not in ALLOWED_MIMETYPES:
                return False
            return True
        
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics', 'uploads', 'settings')
        os.makedirs(upload_folder, exist_ok=True)
        
        image_fields = ['og_image', 'favicon', 'logo', 'placeholder_male', 'placeholder_female']
        for field in image_fields:
            file_key = f'upload_{field}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    if not allowed_file(filename, file):
                        continue
                    ext = filename.rsplit('.', 1)[-1].lower()
                    new_filename = f'{field}.{ext}'
                    file_path = os.path.join(upload_folder, new_filename)
                    file.save(file_path)
                    
                    setting_key = f'seo_{field}' if field == 'og_image' else field
                    existing = SiteSetting.query.filter_by(key=setting_key).first()
                    value = f'/statics/uploads/settings/{new_filename}'
                    if existing:
                        existing.value = value
                        existing.updated_by = session.get('admin_username')
                    else:
                        new_setting = SiteSetting(
                            key=setting_key,
                            value=value,
                            value_type='string',
                            category='seo' if field == 'og_image' else 'general',
                            updated_by=session.get('admin_username')
                        )
                        db.session.add(new_setting)
        
        for key in request.form:
            if key.startswith('setting_'):
                setting_key = key[8:]
                value = request.form[key]
                existing = SiteSetting.query.filter_by(key=setting_key).first()
                if existing:
                    existing.value = value
                    existing.updated_by = session.get('admin_username')
                else:
                    category = 'footer' if setting_key.startswith('footer_') else 'seo' if setting_key.startswith('seo_') else 'security' if setting_key in ['enable_rate_limiting', 'rate_limit_per_minute', 'blocked_ips', 'enable_ip_logging', 'max_upload_size_mb'] else 'general'
                    value_type = 'boolean' if value in ['true', 'false'] else 'text' if setting_key.endswith('_scripts') or setting_key.endswith('_description') else 'string'
                    new_setting = SiteSetting(
                        key=setting_key,
                        value=value,
                        value_type=value_type,
                        category=category,
                        updated_by=session.get('admin_username')
                    )
                    db.session.add(new_setting)
        log_activity(f'Modification parametres', action_type='update', target_type='settings', severity='info')
        db.session.commit()
        invalidate_settings_cache()
        flash('Parametres sauvegardes', 'success')
        return redirect(url_for('admin.settings'))
    
    settings_list = SiteSetting.query.order_by(SiteSetting.category, SiteSetting.key).all()
    settings_dict = {s.key: s.value for s in settings_list}
    settings_by_category = {}
    for s in settings_list:
        if s.category not in settings_by_category:
            settings_by_category[s.category] = []
        settings_by_category[s.category].append(s)
    
    return render_template('admin_settings.html', settings_by_category=settings_by_category, settings=settings_dict)


@admin_bp.route('/users')
@admin_required
def users():
    log_activity('Consultation utilisateurs', action_type='view', target_type='users')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    roles = Role.query.all()
    
    return render_template('admin_users.html', 
                         users=users, 
                         roles=roles,
                         role_filter=role_filter,
                         search=search)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role', 'user')
        organization = request.form.get('organization')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email existe deja', 'error')
            return redirect(url_for('admin.add_user'))
        
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            organization=organization,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(f'Creation utilisateur', action_type='create', target_type='user', target_id=user.id, target_name=email)
        
        flash('Utilisateur cree avec succes', 'success')
        return redirect(url_for('admin.users'))
    
    roles = Role.query.all()
    return render_template('admin_user_form.html', user=None, roles=roles)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.username = request.form.get('username')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role', 'user')
        user.organization = request.form.get('organization')
        user.is_active = request.form.get('is_active') == 'on'
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        log_activity(f'Modification utilisateur', action_type='update', target_type='user', target_id=user.id, target_name=user.email)
        db.session.commit()
        flash('Utilisateur mis a jour', 'success')
        return redirect(url_for('admin.users'))
    
    roles = Role.query.all()
    return render_template('admin_user_form.html', user=user, roles=roles)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    log_activity(f'Suppression utilisateur', action_type='delete', target_type='user', target_id=user.id, target_name=user.email, severity='warning')
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprime', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/roles')
@admin_required
def roles():
    log_activity('Consultation roles', action_type='view', target_type='roles')
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin_roles.html', roles=roles)


@admin_bp.route('/roles/add', methods=['GET', 'POST'])
@admin_required
def add_role():
    if request.method == 'POST':
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        
        permissions = {}
        for key in request.form:
            if key.startswith('perm_'):
                permissions[key[5:]] = True
        
        menu_access = request.form.getlist('menu_access')
        
        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            permissions=permissions,
            menu_access=menu_access,
            is_system=False
        )
        db.session.add(role)
        db.session.commit()
        log_activity(f'Creation role', action_type='create', target_type='role', target_id=role.id, target_name=name)
        
        flash('Role cree avec succes', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin_role_form.html', role=None)


@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        if not role.is_system:
            role.name = request.form.get('name')
        role.display_name = request.form.get('display_name')
        role.description = request.form.get('description')
        
        permissions = {}
        for key in request.form:
            if key.startswith('perm_'):
                permissions[key[5:]] = True
        role.permissions = permissions
        
        role.menu_access = request.form.getlist('menu_access')
        
        log_activity(f'Modification role', action_type='update', target_type='role', target_id=role.id, target_name=role.name)
        db.session.commit()
        flash('Role mis a jour', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin_role_form.html', role=role)


@admin_bp.route('/logs')
@admin_required
def logs():
    log_activity('Consultation logs', action_type='view', target_type='logs')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    action_type = request.args.get('action_type', '')
    severity = request.args.get('severity', '')
    search = request.args.get('search', '')
    security_only = request.args.get('security', '') == '1'
    
    query = ActivityLog.query
    
    if action_type:
        query = query.filter_by(action_type=action_type)
    if severity:
        query = query.filter_by(severity=severity)
    if security_only:
        query = query.filter_by(is_security_event=True)
    if search:
        query = query.filter(
            db.or_(
                ActivityLog.username.ilike(f'%{search}%'),
                ActivityLog.action.ilike(f'%{search}%'),
                ActivityLog.ip_address.ilike(f'%{search}%'),
                ActivityLog.target_name.ilike(f'%{search}%')
            )
        )
    
    logs = query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    action_types = ['auth', 'view', 'create', 'update', 'delete', 'download', 'security', 'admin']
    severity_levels = ['debug', 'info', 'warning', 'error', 'critical']
    
    return render_template('admin_logs.html', 
                         logs=logs,
                         action_types=action_types,
                         severity_levels=severity_levels,
                         action_type=action_type,
                         severity=severity,
                         search=search,
                         security_only=security_only)


@admin_bp.route('/downloads')
@admin_required
def downloads():
    log_activity('Consultation telechargements', action_type='view', target_type='downloads')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    file_type = request.args.get('file_type', '')
    download_type = request.args.get('download_type', '')
    
    query = Download.query
    
    if file_type:
        query = query.filter_by(file_type=file_type)
    if download_type:
        query = query.filter_by(download_type=download_type)
    
    downloads = query.order_by(Download.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    file_types = ['pdf', 'png', 'jpg', 'csv', 'json']
    download_types = ['pdf_fiche', 'pdf_qrcode', 'pdf_affiche', 'image_photo', 'csv_export', 'json_export']
    
    return render_template('admin_downloads.html',
                         downloads=downloads,
                         file_types=file_types,
                         download_types=download_types,
                         file_type=file_type,
                         download_type=download_type)


@admin_bp.route('/contributions/<int:contrib_id>/approve', methods=['POST'])
@admin_required
def approve_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    contribution.is_approved = True
    contribution.approved_by = session.get('admin_username')
    contribution.approved_at = datetime.utcnow()
    log_activity(f'Approbation contribution', action_type='update', target_type='contribution', target_id=contrib_id, target_name=contribution.contributor_name)
    db.session.commit()
    flash('Contribution approuvee', 'success')
    return redirect(url_for('admin.contributions'))


@admin_bp.route('/contributions/<int:contrib_id>/reject', methods=['POST'])
@admin_required
def reject_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    log_activity(f'Rejet contribution', action_type='delete', target_type='contribution', target_id=contrib_id, target_name=contribution.contributor_name, severity='warning')
    db.session.delete(contribution)
    db.session.commit()
    flash('Contribution rejetee', 'success')
    return redirect(url_for('admin.contributions'))


@admin_bp.route('/data')
@admin_required
def data_management():
    log_activity('Consultation gestion donnees', action_type='view', target_type='data')
    countries = get_countries()
    
    # Optimization: Use single aggregation query instead of multiple queries
    stats = db.session.query(
        Disparu.country,
        db.func.count(db.distinct(Disparu.id)).label('disparus_count'),
        db.func.count(db.distinct(Contribution.id)).label('contributions_count'),
        db.func.count(db.distinct(ModerationReport.id)).label('reports_count')
    ).outerjoin(
        Contribution, Contribution.disparu_id == Disparu.id
    ).outerjoin(
        ModerationReport, (ModerationReport.target_id == Disparu.id) & (ModerationReport.target_type == 'disparu')
    ).filter(
        Disparu.country.isnot(None),
        Disparu.country != ''
    ).group_by(Disparu.country).all()

    country_stats = []
    for country, d_count, c_count, r_count in stats:
        country_stats.append({
            'country': country,
            'disparus_count': d_count,
            'contributions_count': c_count,
            'reports_count': r_count
        })
    
    country_stats.sort(key=lambda x: x['disparus_count'], reverse=True)
    
    return render_template('admin_data.html', countries=countries, country_stats=country_stats)


@admin_bp.route('/data/export', methods=['POST'])
@admin_required
def export_data():
    country = request.form.get('country', '')
    export_format = request.form.get('format', 'json')
    
    q = Disparu.query
    if country:
        q = q.filter_by(country=country)
    
    disparus = q.all()
    
    data = []
    for d in disparus:
        item = {
            'public_id': d.public_id,
            'first_name': d.first_name,
            'last_name': d.last_name,
            'age': d.age,
            'sex': d.sex,
            'person_type': d.person_type,
            'country': d.country,
            'city': d.city,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'physical_description': d.physical_description,
            'circumstances': d.circumstances,
            'contacts': d.contacts,
            'status': d.status,
            'created_at': d.created_at.isoformat() if d.created_at else None,
            'disappearance_date': d.disappearance_date.isoformat() if d.disappearance_date else None
        }
        data.append(item)
    
    log_activity(f'Export donnees {export_format.upper()} - {country or "Tous"}', action_type='export', target_type='data', severity='info')
    
    filename = f"disparus_{country or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        output = io.StringIO()
        if data:
            # Sanitize data for CSV injection
            sanitized_data = []
            for row in data:
                sanitized_row = {}
                for k, v in row.items():
                    if isinstance(v, str) and v.startswith(('=', '+', '-', '@')):
                        sanitized_row[k] = "'" + v
                    else:
                        sanitized_row[k] = v
                sanitized_data.append(sanitized_row)

            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(sanitized_data)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'
        return response
    else:
        response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.json'
        return response


@admin_bp.route('/data/backup', methods=['POST'])
@admin_required
def backup_data():
    country = request.form.get('country', '')
    
    q = Disparu.query
    if country:
        q = q.filter_by(country=country)
    
    disparus = q.all()
    disparu_ids = [d.id for d in disparus]
    
    contributions = Contribution.query.filter(Contribution.disparu_id.in_(disparu_ids)).all() if disparu_ids else []
    reports = ModerationReport.query.filter(ModerationReport.target_type == 'disparu', ModerationReport.target_id.in_(disparu_ids)).all() if disparu_ids else []
    
    backup = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'country': country or 'all',
        'disparus': [],
        'contributions': [],
        'moderation_reports': []
    }
    
    for d in disparus:
        backup['disparus'].append({
            'public_id': d.public_id,
            'first_name': d.first_name,
            'last_name': d.last_name,
            'age': d.age,
            'sex': d.sex,
            'person_type': d.person_type,
            'country': d.country,
            'city': d.city,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'physical_description': d.physical_description,
            'circumstances': d.circumstances,
            'disappearance_date': d.disappearance_date.isoformat() if d.disappearance_date else None,
            'clothing': d.clothing,
            'objects': d.objects,
            'contacts': d.contacts,
            'photo_url': d.photo_url,
            'status': d.status,
            'is_flagged': d.is_flagged,
            'view_count': d.view_count,
            'created_at': d.created_at.isoformat() if d.created_at else None,
            'updated_at': d.updated_at.isoformat() if d.updated_at else None
        })
    
    for c in contributions:
        disparu_contrib = Disparu.query.get(c.disparu_id) if c.disparu_id else None
        backup['contributions'].append({
            'disparu_public_id': disparu_contrib.public_id if disparu_contrib else None,
            'contributor_name': c.contributor_name,
            'contributor_phone': c.contributor_phone,
            'contributor_email': c.contributor_email,
            'content': c.content,
            'location': c.location,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'sighting_date': c.sighting_date.isoformat() if c.sighting_date else None,
            'is_approved': c.is_approved,
            'created_at': c.created_at.isoformat() if c.created_at else None
        })
    
    for r in reports:
        disparu = Disparu.query.get(r.target_id) if r.target_id else None
        backup['moderation_reports'].append({
            'disparu_public_id': disparu.public_id if disparu else None,
            'target_type': r.target_type,
            'target_id': r.target_id,
            'reason': r.reason,
            'details': r.details,
            'reporter_contact': r.reporter_contact,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    
    log_activity(f'Sauvegarde base - {country or "Tous"}', action_type='backup', target_type='data', severity='info')
    
    filename = f"backup_{country or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response = make_response(json.dumps(backup, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@admin_bp.route('/data/restore', methods=['POST'])
@admin_required
def restore_data():
    if 'backup_file' not in request.files:
        flash('Aucun fichier selectionne', 'error')
        return redirect(url_for('admin.data_management'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash('Aucun fichier selectionne', 'error')
        return redirect(url_for('admin.data_management'))
    
    try:
        content = file.read().decode('utf-8')
        backup = json.loads(content)
        
        restored_count = 0
        skipped_count = 0
        
        for d_data in backup.get('disparus', []):
            existing = Disparu.query.filter_by(public_id=d_data.get('public_id')).first()
            if existing:
                skipped_count += 1
                continue
            
            d = Disparu()
            d.public_id = d_data.get('public_id')
            d.first_name = d_data.get('first_name')
            d.last_name = d_data.get('last_name')
            d.age = d_data.get('age')
            d.sex = d_data.get('sex', 'unknown')
            d.person_type = d_data.get('person_type', 'adult')
            d.country = d_data.get('country')
            d.city = d_data.get('city')
            d.latitude = d_data.get('latitude')
            d.longitude = d_data.get('longitude')
            d.physical_description = d_data.get('physical_description', '')
            d.circumstances = d_data.get('circumstances', '')
            d.disappearance_date = datetime.fromisoformat(d_data['disappearance_date']) if d_data.get('disappearance_date') else datetime.now()
            d.clothing = d_data.get('clothing')
            d.objects = d_data.get('objects')
            d.contacts = d_data.get('contacts')
            d.photo_url = d_data.get('photo_url')
            d.status = d_data.get('status', 'missing')
            d.is_flagged = d_data.get('is_flagged', False)
            db.session.add(d)
            restored_count += 1
        
        db.session.commit()
        
        log_activity(f'Restauration base - {restored_count} ajoutes, {skipped_count} ignores', action_type='restore', target_type='data', severity='warning')
        flash(f'Restauration terminee: {restored_count} signalements ajoutes, {skipped_count} ignores (doublons)', 'success')
        
    except json.JSONDecodeError:
        flash('Fichier JSON invalide', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la restauration: {str(e)}', 'error')
    
    return redirect(url_for('admin.data_management'))


@admin_bp.route('/data/delete', methods=['POST'])
@admin_required
def delete_data():
    country = request.form.get('country', '')
    confirm = request.form.get('confirm')
    
    if not confirm:
        flash('Vous devez confirmer la suppression', 'error')
        return redirect(url_for('admin.data_management'))
    
    try:
        q = Disparu.query
        if country:
            q = q.filter_by(country=country)
        
        disparus = q.all()
        disparu_ids = [d.id for d in disparus]
        
        if disparu_ids:
            Contribution.query.filter(Contribution.disparu_id.in_(disparu_ids)).delete(synchronize_session=False)
            ModerationReport.query.filter(ModerationReport.target_type == 'disparu', ModerationReport.target_id.in_(disparu_ids)).delete(synchronize_session=False)
        
        deleted_count = q.delete(synchronize_session=False)
        db.session.commit()
        
        log_activity(f'Suppression donnees - {country or "Tous"}: {deleted_count} signalements', action_type='delete', target_type='data', severity='critical', is_security=True)
        flash(f'{deleted_count} signalements et donnees associees supprimes', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.data_management'))


@admin_bp.route('/data/delete-demo', methods=['POST'])
@admin_required
def delete_demo_data():
    try:
        DEMO_IDS = ['DEMO01', 'DEMO02', 'DEMO03', 'DEMO04', 'DEMO05', 'DEMO06', 'DEMO07', 'DEMO08']
        
        disparus = Disparu.query.filter(Disparu.public_id.in_(DEMO_IDS)).all()
        disparu_db_ids = [d.id for d in disparus]
        
        contrib_deleted = 0
        report_deleted = 0
        
        if disparu_db_ids:
            contrib_deleted = Contribution.query.filter(Contribution.disparu_id.in_(disparu_db_ids)).delete(synchronize_session=False)
            report_deleted = ModerationReport.query.filter(
                ModerationReport.target_type == 'disparu',
                ModerationReport.target_id.in_(disparu_db_ids)
            ).delete(synchronize_session=False)
        
        disparu_deleted = Disparu.query.filter(Disparu.public_id.in_(DEMO_IDS)).delete(synchronize_session=False)
        db.session.commit()
        
        log_activity(f'Suppression donnees demo: {disparu_deleted} signalements', action_type='delete', target_type='demo_data', severity='warning')
        flash(f'{disparu_deleted} profils demo supprimes (+ {contrib_deleted} contributions, {report_deleted} rapports)', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.data_management'))
