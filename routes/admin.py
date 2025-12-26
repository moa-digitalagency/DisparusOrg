from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for

from models import db, Disparu, Contribution, ModerationReport
from services.analytics import get_platform_stats

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
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
    return redirect(url_for('admin.moderation'))


@admin_bp.route('/disparu/<int:disparu_id>/status', methods=['POST'])
def update_status(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    new_status = request.form.get('status')
    if new_status in ['missing', 'found', 'deceased']:
        disparu.status = new_status
        db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/disparu/<int:disparu_id>/delete', methods=['POST'])
def delete_disparu(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    db.session.delete(disparu)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
