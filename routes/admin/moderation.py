from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash
from models import db, ModerationReport, Disparu, Contribution, ActivityLog, ContentModerationLog
from . import admin_bp, admin_required, log_activity

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


@admin_bp.route('/blocked-attempts')
@admin_required
def blocked_attempts():
    log_activity('Consultation tentatives bloquees', action_type='view', target_type='security')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    logs = ContentModerationLog.query.order_by(ContentModerationLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_blocked_attempts.html', logs=logs)


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
