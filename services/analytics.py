from models import db, Disparu, Contribution


def get_platform_stats():
    return {
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'deceased': Disparu.query.filter_by(status='deceased').count(),
        'flagged': Disparu.query.filter_by(is_flagged=True).count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
    }


def get_stats_by_country():
    results = db.session.query(
        Disparu.country,
        db.func.count(Disparu.id).label('total'),
        db.func.sum(db.case((Disparu.status == 'missing', 1), else_=0)).label('missing'),
        db.func.sum(db.case((Disparu.status == 'found', 1), else_=0)).label('found'),
    ).group_by(Disparu.country).all()
    
    return [
        {
            'country': r.country,
            'total': r.total,
            'missing': r.missing or 0,
            'found': r.found or 0,
        }
        for r in results
    ]


def get_stats_by_period(start_date=None, end_date=None):
    q = Disparu.query
    
    if start_date:
        q = q.filter(Disparu.created_at >= start_date)
    if end_date:
        q = q.filter(Disparu.created_at <= end_date)
    
    return {
        'total': q.count(),
        'missing': q.filter_by(status='missing').count(),
        'found': q.filter_by(status='found').count(),
    }


def get_recent_activity(limit=10):
    recent_disparus = Disparu.query.order_by(Disparu.created_at.desc()).limit(limit).all()
    recent_contributions = Contribution.query.order_by(Contribution.created_at.desc()).limit(limit).all()
    
    return {
        'recent_disparus': [d.to_dict() for d in recent_disparus],
        'recent_contributions': [c.to_dict() for c in recent_contributions],
    }
