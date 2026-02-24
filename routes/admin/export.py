from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, Response, make_response, stream_with_context
from models import db, Disparu, Contribution, ModerationReport, Download
from services import stats_service, export_manager, data_manager
from utils.geo import get_countries
from . import admin_bp, admin_required, log_activity

@admin_bp.route('/statistics')
@admin_required
def statistics():
    log_activity('Consultation statistiques', action_type='view', target_type='statistics')

    period = request.args.get('period', 'all')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    data = stats_service.get_statistics_data(period, start_date_str, end_date_str)

    return render_template('admin_statistics.html',
                         stats=data['stats'],
                         by_country=data['by_country'],
                         by_status=data['by_status'],
                         most_viewed=data['all_files_stats'][:5],
                         all_files_stats=data['all_files_stats'],
                         most_downloaded=data['most_downloaded'],
                         downloads_by_type=data['downloads_by_type'],
                         filters=data['filters'])

@admin_bp.route('/statistics/export/csv')
@admin_required
def export_stats_csv():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    locale = request.cookies.get('locale', 'fr')

    stream = export_manager.generate_stats_csv_stream(start_date_str, end_date_str, locale)
    response = Response(stream_with_context(stream), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=statistiques.csv'
    return response


@admin_bp.route('/statistics/export/pdf')
@admin_required
def export_stats_pdf():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    period = request.args.get('period', 'all')
    locale = request.cookies.get('locale', 'fr')
    generated_by = session.get('admin_username', 'Admin')

    data = stats_service.get_statistics_data(period, start_date_str, end_date_str)
    pdf_buffer = export_manager.generate_stats_pdf(data, locale, generated_by)

    if not pdf_buffer:
        flash("Erreur lors de la génération du PDF", "error")
        return redirect(url_for('admin.statistics'))

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=statistiques.pdf'
    return response


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

    log_activity(f'Export donnees {export_format.upper()} - {country or "Tous"}', action_type='export', target_type='data', severity='info')

    filename = f"disparus_{country or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if export_format == 'csv':
        stream = export_manager.generate_data_csv_stream(country)
        mimetype = 'text/csv; charset=utf-8'
        ext = 'csv'
    else:
        stream = export_manager.generate_data_json_stream(country)
        mimetype = 'application/json; charset=utf-8'
        ext = 'json'

    response = Response(stream_with_context(stream), mimetype=mimetype)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.{ext}'
    return response


@admin_bp.route('/data/backup', methods=['POST'])
@admin_required
def backup_data():
    country = request.form.get('country', '')

    log_activity(f'Sauvegarde base - {country or "Tous"}', action_type='backup', target_type='data', severity='info')

    filename = f"backup_{country or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    stream = data_manager.generate_backup_stream(country)

    response = Response(stream_with_context(stream), mimetype='application/json; charset=utf-8')
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
        result = data_manager.restore_from_json(content)

        msg = f'Restauration terminee: {result["restored"]} signalements ajoutes, {result["skipped"]} ignores (doublons), {result["errors"]} erreurs validation'
        log_activity(f'Restauration base - {result["restored"]} ajoutes, {result["skipped"]} ignores', action_type='restore', target_type='data', severity='warning')
        flash(msg, 'success')

    except ValueError as e:
        flash(f'Erreur validation: {str(e)}', 'error')
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
        deleted_count = data_manager.delete_data_by_country(country)

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
        result = data_manager.delete_demo_data()

        log_activity(f'Suppression donnees demo: {result["disparus"]} signalements', action_type='delete', target_type='demo_data', severity='warning')
        flash(f'{result["disparus"]} profils demo supprimes (+ {result["contributions"]} contributions, {result["reports"]} rapports)', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('admin.data_management'))
