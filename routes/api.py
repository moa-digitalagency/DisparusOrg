from flask import Blueprint, jsonify, request

from models import db, Disparu, Contribution
from utils.geo import get_countries, get_cities

api_bp = Blueprint('api', __name__)


@api_bp.route('/disparus')
def get_disparus():
    status = request.args.get('status')
    country = request.args.get('country')
    limit = request.args.get('limit', 100, type=int)
    
    q = Disparu.query
    
    if status:
        q = q.filter_by(status=status)
    if country:
        q = q.filter_by(country=country)
    
    disparus = q.order_by(Disparu.created_at.desc()).limit(limit).all()
    
    return jsonify([d.to_dict() for d in disparus])


@api_bp.route('/disparus/<public_id>')
def get_disparu(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first_or_404()
    contributions = Contribution.query.filter_by(disparu_id=disparu.id).all()
    
    data = disparu.to_dict()
    data['contributions'] = [c.to_dict() for c in contributions]
    
    return jsonify(data)


@api_bp.route('/stats')
def get_stats():
    return jsonify({
        'total': Disparu.query.count(),
        'missing': Disparu.query.filter_by(status='missing').count(),
        'found': Disparu.query.filter_by(status='found').count(),
        'contributions': Contribution.query.count(),
        'countries': db.session.query(db.func.count(db.distinct(Disparu.country))).scalar() or 0,
    })


@api_bp.route('/countries')
def get_countries_list():
    return jsonify(get_countries())


@api_bp.route('/cities/<country>')
def get_cities_list(country):
    return jsonify(get_cities(country))


@api_bp.route('/search')
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
