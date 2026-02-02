from models import db, Disparu
import math
from collections import defaultdict
from sqlalchemy import or_


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
    
    # Spatial hashing / Grid-based clustering optimization
    GRID_SIZE = 0.5  # degrees, approx 55km at equator
    grid = defaultdict(list)
    max_lon_idx = int(360 / GRID_SIZE)

    for idx, d in enumerate(disparus):
        lat_idx = int(d.latitude / GRID_SIZE)
        # Normalize longitude to 0..360
        norm_lon = d.longitude % 360
        lon_idx = int(norm_lon / GRID_SIZE)
        grid[(lat_idx, lon_idx)].append((idx, d))

    hotspots = []
    processed = set()
    
    for i, d1 in enumerate(disparus):
        if i in processed:
            continue
        
        cluster = [d1]
        cluster_ids = {i}
        
        lat_idx = int(d1.latitude / GRID_SIZE)
        norm_lon = d1.longitude % 360
        lon_idx = int(norm_lon / GRID_SIZE)

        # Calculate search radius in grid units
        lat_steps = math.ceil(radius_km / 111.0 / GRID_SIZE)

        cos_lat = math.cos(math.radians(d1.latitude))
        if abs(cos_lat) < 0.0001:
            lon_steps = max_lon_idx // 2  # Search everything
        else:
            lon_steps = math.ceil(radius_km / (111.0 * abs(cos_lat)) / GRID_SIZE)
            if lon_steps > max_lon_idx // 2:
                lon_steps = max_lon_idx // 2

        # Check neighbor cells
        checked_cells = set()
        for d_lat in range(-lat_steps, lat_steps + 1):
            curr_lat = lat_idx + d_lat
            for d_lon in range(-lon_steps, lon_steps + 1):
                curr_lon = (lon_idx + d_lon) % max_lon_idx

                if (curr_lat, curr_lon) in checked_cells:
                    continue
                checked_cells.add((curr_lat, curr_lon))

                cell_points = grid.get((curr_lat, curr_lon))
                if not cell_points:
                    continue

                for j, d2 in cell_points:
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
    # Calculate bounding box
    # 1 degree of latitude ~= 111 km
    lat_delta = radius_km / 111.0

    # 1 degree of longitude ~= 111 km * cos(latitude)
    # Handle pole case to avoid division by zero
    if abs(latitude) >= 90:
        lon_delta = 180
    else:
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        if lon_delta > 180:
            lon_delta = 180

    min_lat = latitude - lat_delta
    max_lat = latitude + lat_delta
    min_lon = longitude - lon_delta
    max_lon = longitude + lon_delta

    query = Disparu.query.filter(
        Disparu.latitude.isnot(None),
        Disparu.longitude.isnot(None),
        Disparu.latitude >= min_lat,
        Disparu.latitude <= max_lat
    )

    if lon_delta >= 180:
        # Cover all longitudes
        pass
    elif min_lon < -180:
        query = query.filter(or_(
            Disparu.longitude >= min_lon + 360,
            Disparu.longitude <= max_lon
        ))
    elif max_lon > 180:
        query = query.filter(or_(
            Disparu.longitude >= min_lon,
            Disparu.longitude <= max_lon - 360
        ))
    else:
        query = query.filter(
            Disparu.longitude >= min_lon,
            Disparu.longitude <= max_lon
        )

    disparus = query.all()
    
    nearby = []
    for d in disparus:
        distance = haversine_distance(latitude, longitude, d.latitude, d.longitude)
        if distance <= radius_km:
            nearby.append({
                'disparu': d.to_dict(),
                'distance_km': round(distance, 2)
            })
    
    return sorted(nearby, key=lambda x: x['distance_km'])
