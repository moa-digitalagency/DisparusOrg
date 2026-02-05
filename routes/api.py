"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Routes pour l'API
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, jsonify, request
from math import radians, sin, cos, sqrt, atan2

from models import db, Disparu, Contribution
from utils.geo import get_countries, get_cities
from security.rate_limit import rate_limit
from services.moderation import get_geo_info

api_bp = Blueprint('api', __name__)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


@api_bp.route('/disparus')
@rate_limit()
def get_disparus():
    status = request.args.get('status')
    country = request.args.get('country')
    limit = request.args.get('limit', 100, type=int)
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    
    q = Disparu.query
    
    if status:
        q = q.filter_by(status=status)
    if country:
        q = q.filter_by(country=country)
    
    disparus = q.order_by(Disparu.created_at.desc()).limit(limit).all()
    
    result = [d.to_dict() for d in disparus]
    
    if user_lat and user_lng:
        for d in result:
            d['distance'] = haversine_distance(user_lat, user_lng, d.get('latitude'), d.get('longitude'))
        result.sort(key=lambda x: x.get('distance', float('inf')))
    
    return jsonify(result)


@api_bp.route('/map-data')
@rate_limit()
def get_map_data():
    min_lat = request.args.get('min_lat', type=float)
    max_lat = request.args.get('max_lat', type=float)
    min_lng = request.args.get('min_lng', type=float)
    max_lng = request.args.get('max_lng', type=float)

    person_type = request.args.get('type')
    country = request.args.get('country')

    # Select only necessary fields for map display
    query = db.session.query(
        Disparu.id,
        Disparu.public_id,
        Disparu.first_name,
        Disparu.last_name,
        Disparu.photo_url,
        Disparu.latitude,
        Disparu.longitude,
        Disparu.city,
        Disparu.country,
        Disparu.status,
        Disparu.person_type,
        Disparu.is_flagged
    ).filter(Disparu.latitude.isnot(None), Disparu.longitude.isnot(None))

    if min_lat is not None and max_lat is not None and min_lng is not None and max_lng is not None:
        # Handle date line crossing if needed (min_lng > max_lng)
        if min_lng > max_lng:
             query = query.filter(
                Disparu.latitude.between(min_lat, max_lat),
                db.or_(Disparu.longitude >= min_lng, Disparu.longitude <= max_lng)
            )
        else:
            query = query.filter(
                Disparu.latitude.between(min_lat, max_lat),
                Disparu.longitude.between(min_lng, max_lng)
            )

    if country:
        query = query.filter(Disparu.country == country)

    if person_type and person_type != 'all':
        if person_type == 'person':
            query = query.filter(Disparu.person_type.in_(['child', 'adult', 'elderly']))
        else:
            query = query.filter(Disparu.person_type == person_type)

    # Limit to prevent overload if bbox is too large
    results = query.limit(500).all()

    data = [{
        'id': d.id,
        'public_id': d.public_id,
        'full_name': f"{d.first_name} {d.last_name}" if d.person_type != 'animal' else d.first_name,
        'photo_url': d.photo_url,
        'latitude': d.latitude,
        'longitude': d.longitude,
        'city': d.city,
        'country': d.country,
        'status': d.status,
        'person_type': d.person_type,
        'is_flagged': d.is_flagged
    } for d in results]

    return jsonify(data)


@api_bp.route('/disparus/nearby')
@rate_limit()
def get_nearby_disparus():
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    status = request.args.get('status', 'missing')
    limit = request.args.get('limit', 20, type=int)
    
    if not user_lat or not user_lng:
        return jsonify({'error': 'lat and lng required'}), 400
    
    # Helper to construct the query with optional bounding box
    def get_query(bbox=None):
        if bbox:
            min_lat, max_lat, min_lng, max_lng = bbox
            q = Disparu.query.filter(
                Disparu.latitude.between(min_lat, max_lat),
                Disparu.longitude.between(min_lng, max_lng)
            )
        else:
            q = Disparu.query.filter(Disparu.latitude.isnot(None), Disparu.longitude.isnot(None))

        if status:
            q = q.filter_by(status=status)
        return q

    # Optimization: Use bounding box to limit search space (approx 550km box)
    BOX_SIZE = 5.0
    bbox = (user_lat - BOX_SIZE, user_lat + BOX_SIZE, user_lng - BOX_SIZE, user_lng + BOX_SIZE)
    
    disparus = get_query(bbox).all()

    # Fallback: if not enough results, search everything (preserves behavior for distant matches)
    if len(disparus) < limit:
        disparus = get_query(None).all()
    
    results = []
    for d in disparus:
        dist = haversine_distance(user_lat, user_lng, d.latitude, d.longitude)
        data = d.to_dict()
        data['distance'] = round(dist, 1)
        results.append(data)
    
    results.sort(key=lambda x: x['distance'])
    
    return jsonify(results[:limit])


@api_bp.route('/disparus/<public_id>')
@rate_limit()
def get_disparu(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    contributions = Contribution.query.filter_by(disparu_id=disparu.id).all()
    
    data = disparu.to_dict()
    data['contributions'] = [c.to_dict() for c in contributions]
    
    return jsonify(data)


@api_bp.route('/stats')
@rate_limit()
def get_stats():
    # Subquery for contributions count
    contributions_subq = db.select(db.func.count(Contribution.id)).scalar_subquery()

    # Main query on Disparu
    stats = db.session.execute(
        db.select(
            db.func.count(Disparu.id),
            db.func.sum(db.case((Disparu.status == 'missing', 1), else_=0)),
            db.func.sum(db.case((Disparu.status.in_(['found', 'found_alive']), 1), else_=0)),
            db.func.count(db.distinct(Disparu.country)),
            contributions_subq
        )
    ).first()

    return jsonify({
        'total': stats[0] or 0,
        'missing': stats[1] or 0,
        'found': stats[2] or 0,
        'countries': stats[3] or 0,
        'contributions': stats[4] or 0,
    })


@api_bp.route('/countries')
@rate_limit()
def get_countries_list():
    return jsonify(get_countries())


@api_bp.route('/cities/<country>')
@rate_limit()
def get_cities_list(country):
    return jsonify(get_cities(country))


@api_bp.route('/search')
@rate_limit()
def search_api():
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    search_term = f"%{query}%"
    results = Disparu.query.filter(
        db.or_(
            Disparu.first_name.ilike(search_term),
            Disparu.last_name.ilike(search_term),
            Disparu.public_id.ilike(search_term),
            Disparu.city.ilike(search_term),
        )
    ).limit(20).all()
    
    return jsonify([d.to_dict() for d in results])


@api_bp.route('/geo/ip')
@rate_limit()
def get_ip_location():
    # Detect IP
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr

    country, city = get_geo_info(ip_address)

    return jsonify({
        'country': country,
        'city': city,
        'ip': ip_address
    })
