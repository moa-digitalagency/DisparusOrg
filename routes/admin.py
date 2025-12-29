import os
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import db, Disparu, Contribution, ModerationReport
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


@admin_bp.route('/settings')
@admin_required
def settings():
    return render_template('admin_settings.html')
