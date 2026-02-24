"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Service pour les statistiques
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from datetime import datetime, timedelta
from models import db, Disparu, Contribution, Download


def get_dashboard_stats():
    """
    Retrieves statistics for the main dashboard.
    """
    # Optimization: Fetch all Disparu stats in a single query
    disparu_stats = db.session.query(
        db.func.count(Disparu.id).label('total'),
        db.func.count(db.case((Disparu.status == 'missing', 1))).label('missing'),
        db.func.count(db.case((Disparu.status.in_(['found', 'found_alive']), 1))).label('found'),
        db.func.count(db.case((Disparu.status.in_(['deceased', 'found_deceased']), 1))).label('deceased'),
        db.func.count(db.case((Disparu.is_flagged == True, 1))).label('flagged'),
        db.func.count(db.distinct(Disparu.country)).label('countries')
    ).one()

    stats = {
        'total': disparu_stats.total,
        'missing': disparu_stats.missing,
        'found': disparu_stats.found,
        'deceased': disparu_stats.deceased,
        'flagged': disparu_stats.flagged,
        'contributions': Contribution.query.count(),
        'countries': disparu_stats.countries or 0,
    }

    # Optimization: Only fetch 5 recent for the list
    recent_disparus = Disparu.query.order_by(Disparu.created_at.desc()).limit(5).all()

    # Optimization: For map, fetch only needed fields to avoid hydrating all objects
    # Limit to 1000 most recent for performance
    map_data_query = db.session.query(
        Disparu.latitude, Disparu.longitude, Disparu.first_name,
        Disparu.last_name, Disparu.public_id, Disparu.status, Disparu.is_flagged
    ).filter(Disparu.latitude.isnot(None), Disparu.longitude.isnot(None))\
    .order_by(Disparu.created_at.desc())\
    .limit(1000).all()

    map_list = [{
        'latitude': d.latitude,
        'longitude': d.longitude,
        'first_name': d.first_name,
        'last_name': d.last_name,
        'public_id': d.public_id,
        'status': d.status,
        'is_flagged': d.is_flagged
    } for d in map_data_query]

    return {
        'stats': stats,
        'recent_disparus': recent_disparus,
        'map_list': map_list
    }


def get_map_data():
    """
    Retrieves data for the dedicated map view.
    """
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

    return {
        'results': results,
        'disparus_list': disparus_list
    }


def get_statistics_data(period='all', start_date_str=None, end_date_str=None):
    """
    Helper to gather all platform statistics with filtering.
    """
    start_date = None
    end_date = datetime.now()

    if period == '1d':
        start_date = end_date - timedelta(days=1)
    elif period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '1m':
        start_date = end_date - timedelta(days=30)
    elif period == 'custom' and start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                 end_date_parsed = datetime.strptime(end_date_str, '%Y-%m-%d')
                 # Set end_date to end of that day
                 end_date = end_date_parsed + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            pass

    # Base queries
    q_disparu = Disparu.query

    if start_date:
        q_disparu = q_disparu.filter(Disparu.created_at >= start_date, Disparu.created_at <= end_date)

    # Stats Aggregation
    aggregated_stats = q_disparu.with_entities(
        db.func.sum(db.case((Disparu.person_type != 'animal', 1), else_=0)).label('total_persons'),
        db.func.sum(db.case((Disparu.person_type == 'animal', 1), else_=0)).label('total_animals'),
        db.func.sum(db.case((db.and_(Disparu.person_type != 'animal', Disparu.status.in_(['found', 'found_alive'])), 1), else_=0)).label('found_persons'),
        db.func.sum(db.case((db.and_(Disparu.person_type == 'animal', Disparu.status.in_(['found', 'found_alive'])), 1), else_=0)).label('found_animals'),
        db.func.sum(db.case((db.and_(Disparu.person_type != 'animal', Disparu.status.in_(['deceased', 'found_deceased'])), 1), else_=0)).label('deceased_persons'),
        db.func.sum(db.case((db.and_(Disparu.person_type == 'animal', Disparu.status.in_(['deceased', 'found_deceased'])), 1), else_=0)).label('deceased_animals'),
        db.func.sum(db.case((Disparu.person_type != 'animal', Disparu.view_count), else_=0)).label('views_persons'),
        db.func.sum(db.case((Disparu.person_type == 'animal', Disparu.view_count), else_=0)).label('views_animals')
    ).one()

    total_persons = aggregated_stats.total_persons or 0
    total_animals = aggregated_stats.total_animals or 0
    found_persons = aggregated_stats.found_persons or 0
    found_animals = aggregated_stats.found_animals or 0
    deceased_persons = aggregated_stats.deceased_persons or 0
    deceased_animals = aggregated_stats.deceased_animals or 0
    views_persons = aggregated_stats.views_persons or 0
    views_animals = aggregated_stats.views_animals or 0

    q_downloads = db.session.query(Download).join(Disparu)
    if start_date:
        q_downloads = q_downloads.filter(Download.created_at >= start_date, Download.created_at <= end_date)

    downloads_persons = q_downloads.filter(Disparu.person_type != 'animal').count()
    downloads_animals = q_downloads.filter(Disparu.person_type == 'animal').count()

    stats = {
        'total': total_persons + total_animals,
        'total_persons': total_persons,
        'total_animals': total_animals,
        'found': found_persons + found_animals,
        'found_persons': found_persons,
        'found_animals': found_animals,
        'deceased': deceased_persons + deceased_animals,
        'deceased_persons': deceased_persons,
        'deceased_animals': deceased_animals,
        'total_views': int(views_persons + views_animals),
        'views_persons': int(views_persons),
        'views_animals': int(views_animals),
        'total_downloads': downloads_persons + downloads_animals,
        'downloads_persons': downloads_persons,
        'downloads_animals': downloads_animals,
        'contributions': Contribution.query.count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0
    }

    by_country = db.session.query(Disparu.country, db.func.count(Disparu.id))
    if start_date:
        by_country = by_country.filter(Disparu.created_at >= start_date, Disparu.created_at <= end_date)
    by_country = by_country.group_by(Disparu.country).order_by(db.func.count(Disparu.id).desc()).limit(10).all()

    by_status = db.session.query(Disparu.status, db.func.count(Disparu.id))
    if start_date:
        by_status = by_status.filter(Disparu.created_at >= start_date, Disparu.created_at <= end_date)
    by_status = by_status.group_by(Disparu.status).all()

    q_most_viewed = Disparu.query
    if start_date:
        q_most_viewed = q_most_viewed.filter(Disparu.created_at >= start_date, Disparu.created_at <= end_date)
    all_files_stats = q_most_viewed.order_by(Disparu.view_count.desc()).limit(100).all()

    most_downloaded = db.session.query(
        Disparu.public_id, Disparu.first_name, Disparu.last_name, Disparu.city, Disparu.country,
        db.func.count(Download.id).label('download_count')
    ).join(Download, Download.disparu_public_id == Disparu.public_id)
    if start_date:
        most_downloaded = most_downloaded.filter(Download.created_at >= start_date, Download.created_at <= end_date)
    most_downloaded = most_downloaded.group_by(
        Disparu.public_id, Disparu.first_name, Disparu.last_name, Disparu.city, Disparu.country
    ).order_by(db.func.count(Download.id).desc()).limit(10).all()

    downloads_by_type = db.session.query(Download.file_type, db.func.count(Download.id))
    if start_date:
        downloads_by_type = downloads_by_type.filter(Download.created_at >= start_date, Download.created_at <= end_date)
    downloads_by_type = downloads_by_type.group_by(Download.file_type).order_by(db.func.count(Download.id).desc()).all()

    return {
        'stats': stats,
        'by_country': by_country,
        'by_status': by_status,
        'all_files_stats': all_files_stats,
        'most_downloaded': most_downloaded,
        'downloads_by_type': downloads_by_type,
        'filters': {'period': period, 'start_date': start_date_str, 'end_date': end_date_str}
    }
