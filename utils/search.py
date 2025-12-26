from models import db, Disparu


def search_disparus(query, filters=None):
    q = Disparu.query
    
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            db.or_(
                Disparu.first_name.ilike(search_term),
                Disparu.last_name.ilike(search_term),
                Disparu.public_id.ilike(search_term),
                Disparu.city.ilike(search_term),
                Disparu.physical_description.ilike(search_term),
            )
        )
    
    if filters:
        if filters.get('status'):
            q = q.filter_by(status=filters['status'])
        if filters.get('person_type'):
            q = q.filter_by(person_type=filters['person_type'])
        if filters.get('country'):
            q = q.filter_by(country=filters['country'])
        if filters.get('city'):
            q = q.filter_by(city=filters['city'])
        if filters.get('has_photo'):
            q = q.filter(Disparu.photo_url.isnot(None))
    
    return q.order_by(Disparu.created_at.desc())


def build_search_index():
    pass


def update_search_index(disparu):
    pass
