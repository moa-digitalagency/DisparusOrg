from models import db, Disparu
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def find_hotspots(min_cases=3, radius_km=50):
    disparus = Disparu.query.filter(
        Disparu.latitude.isnot(None),
        Disparu.longitude.isnot(None),
        Disparu.status == 'missing'
    ).all()
    
    if len(disparus) < min_cases:
        return []
    
    hotspots = []
    processed = set()
    
    for i, d1 in enumerate(disparus):
        if i in processed:
            continue
        
        cluster = [d1]
        cluster_ids = {i}
        
        for j, d2 in enumerate(disparus):
            if j in processed or j == i:
                continue
            
            distance = haversine_distance(
                d1.latitude, d1.longitude,
                d2.latitude, d2.longitude
            )
            
            if distance <= radius_km:
                cluster.append(d2)
                cluster_ids.add(j)
        
        if len(cluster) >= min_cases:
            center_lat = sum(d.latitude for d in cluster) / len(cluster)
            center_lng = sum(d.longitude for d in cluster) / len(cluster)
            
            hotspots.append({
                'latitude': center_lat,
                'longitude': center_lng,
                'count': len(cluster),
                'disparus': [d.public_id for d in cluster],
                'radius_km': radius_km,
            })
            
            processed.update(cluster_ids)
    
    return sorted(hotspots, key=lambda x: x['count'], reverse=True)


def get_nearby_cases(latitude, longitude, radius_km=100):
    disparus = Disparu.query.filter(
        Disparu.latitude.isnot(None),
        Disparu.longitude.isnot(None)
    ).all()
    
    nearby = []
    for d in disparus:
        distance = haversine_distance(latitude, longitude, d.latitude, d.longitude)
        if distance <= radius_km:
            nearby.append({
                'disparu': d.to_dict(),
                'distance_km': round(distance, 2)
            })
    
    return sorted(nearby, key=lambda x: x['distance_km'])
