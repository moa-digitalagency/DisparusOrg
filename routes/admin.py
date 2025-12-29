import os
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import db, Disparu, Contribution, ModerationReport, User, Role, ActivityLog, Download, SiteSetting
from services.analytics import get_platform_stats

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', '')
        
        if username == admin_username and password == admin_password and admin_password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Identifiants invalides'
    
    return render_template('admin_login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'deceased': Disparu.query.filter_by(status='deceased').count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
    }
    disparus = Disparu.query.order_by(Disparu.created_at.desc()).all()
    return render_template('admin.html', stats=stats, disparus=disparus)


@admin_bp.route('/moderation')
@admin_required
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
                db.session.delete(disparu)
    elif action == 'unflag':
        if report.target_type == 'disparu':
            disparu = Disparu.query.get(report.target_id)
            if disparu:
                disparu.is_flagged = False
    
    db.session.commit()
    return redirect(url_for('admin.moderation'))


@admin_bp.route('/disparu/<int:disparu_id>/status', methods=['POST'])
@admin_required
def update_status(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    new_status = request.form.get('status')
    if new_status in ['missing', 'found', 'deceased']:
        disparu.status = new_status
        db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/disparu/<int:disparu_id>/delete', methods=['POST'])
@admin_required
def delete_disparu(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    db.session.delete(disparu)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reports')
@admin_required
def all_reports():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    country_filter = request.args.get('country', '')
    
    query = Disparu.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if country_filter:
        query = query.filter_by(country=country_filter)
    
    disparus = query.order_by(Disparu.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    countries = db.session.query(Disparu.country).distinct().all()
    
    return render_template('admin_reports.html', 
                         disparus=disparus, 
                         countries=[c[0] for c in countries],
                         status_filter=status_filter,
                         country_filter=country_filter)


@admin_bp.route('/contributions')
@admin_required
def contributions():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    contributions = Contribution.query.order_by(Contribution.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_contributions.html', contributions=contributions)


@admin_bp.route('/statistics')
@admin_required
def statistics():
    stats = {
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'deceased': Disparu.query.filter_by(status='deceased').count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
        'pending_reports': ModerationReport.query.filter_by(status='pending').count(),
    }
    
    by_country = db.session.query(
        Disparu.country, 
        db.func.count(Disparu.id)
    ).group_by(Disparu.country).order_by(db.func.count(Disparu.id).desc()).limit(10).all()
    
    by_status = db.session.query(
        Disparu.status, 
        db.func.count(Disparu.id)
    ).group_by(Disparu.status).all()
    
    return render_template('admin_statistics.html', 
                         stats=stats, 
                         by_country=by_country, 
                         by_status=by_status)


@admin_bp.route('/map')
@admin_required
def map_view():
    disparus = Disparu.query.all()
    return render_template('admin_map.html', disparus=disparus)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        for key in request.form:
            if key.startswith('setting_'):
                setting_key = key[8:]
                value = request.form[key]
                existing = SiteSetting.query.filter_by(key=setting_key).first()
                if existing:
                    existing.value = value
                    existing.updated_by = session.get('admin_username')
                else:
                    category = 'seo' if setting_key.startswith('seo_') else 'security' if setting_key in ['enable_rate_limiting', 'rate_limit_per_minute', 'blocked_ips', 'enable_ip_logging', 'max_upload_size_mb'] else 'general'
                    value_type = 'boolean' if value in ['true', 'false'] else 'text' if setting_key.endswith('_scripts') else 'string'
                    new_setting = SiteSetting(
                        key=setting_key,
                        value=value,
                        value_type=value_type,
                        category=category,
                        updated_by=session.get('admin_username')
                    )
                    db.session.add(new_setting)
        db.session.commit()
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
        
        db.session.commit()
        flash('Utilisateur mis a jour', 'success')
        return redirect(url_for('admin.users'))
    
    roles = Role.query.all()
    return render_template('admin_user_form.html', user=user, roles=roles)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprime', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/roles')
@admin_required
def roles():
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
        
        db.session.commit()
        flash('Role mis a jour', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin_role_form.html', role=role)


@admin_bp.route('/logs')
@admin_required
def logs():
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
    db.session.commit()
    flash('Contribution approuvee', 'success')
    return redirect(url_for('admin.contributions'))


@admin_bp.route('/contributions/<int:contrib_id>/reject', methods=['POST'])
@admin_required
def reject_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    db.session.delete(contribution)
    db.session.commit()
    flash('Contribution rejetee', 'success')
    return redirect(url_for('admin.contributions'))
