import time
import os
import sys
import random
import string
from datetime import datetime

# Add root directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.disparu import Disparu

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def setup_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create dummy data
        disparus = []
        print("Generating 5000 records...")
        for i in range(5000):
            d = Disparu(
                public_id=f"DEMO{i}",
                person_type='adult',
                first_name=generate_random_string(),
                last_name=generate_random_string(),
                age=random.randint(18, 90),
                sex='male',
                country='Country',
                city='City',
                physical_description='Desc',
                disappearance_date=datetime.now(),
                circumstances='Circumstances',
                latitude=random.uniform(-90, 90) if i % 2 == 0 else None,
                longitude=random.uniform(-180, 180) if i % 2 == 0 else None,
                status='missing'
            )
            disparus.append(d)

        db.session.bulk_save_objects(disparus)
        db.session.commit()
        print("Database populated with 5000 records.")

def benchmark_current(app):
    with app.app_context():
        # Warmup
        Disparu.query.filter(Disparu.latitude.isnot(None)).all()

        start_time = time.time()

        # Current implementation
        all_disparus_raw = Disparu.query.filter(Disparu.latitude.isnot(None)).all()
        all_disparus = [{
            'id': d.id,
            'full_name': f"{d.first_name} {d.last_name}",
            'photo_url': d.photo_url,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'city': d.city,
            'country': d.country,
            'status': d.status
        } for d in all_disparus_raw]

        end_time = time.time()
        return end_time - start_time, len(all_disparus)

def benchmark_optimized(app):
    with app.app_context():
        # Warmup
        db.session.query(Disparu.id).filter(Disparu.latitude.isnot(None)).all()

        start_time = time.time()

        # Optimized implementation
        results = db.session.query(
            Disparu.id,
            Disparu.first_name,
            Disparu.last_name,
            Disparu.photo_url,
            Disparu.latitude,
            Disparu.longitude,
            Disparu.city,
            Disparu.country,
            Disparu.status
        ).filter(Disparu.latitude.isnot(None)).all()

        all_disparus = [{
            'id': r.id,
            'full_name': f"{r.first_name} {r.last_name}",
            'photo_url': r.photo_url,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'city': r.city,
            'country': r.country,
            'status': r.status
        } for r in results]

        end_time = time.time()
        return end_time - start_time, len(all_disparus)

if __name__ == "__main__":
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SESSION_SECRET'] = 'test'

    app = create_app()
    setup_database(app)

    print("\nBenchmarking Current Implementation...")
    current_time, current_count = benchmark_current(app)
    print(f"Time: {current_time:.4f} seconds")
    print(f"Records: {current_count}")

    print("\nBenchmarking Optimized Implementation...")
    optimized_time, optimized_count = benchmark_optimized(app)
    print(f"Time: {optimized_time:.4f} seconds")
    print(f"Records: {optimized_count}")

    if current_count != optimized_count:
        print("\nERROR: Record counts do not match!")
        sys.exit(1)

    improvement = (current_time - optimized_time) / current_time * 100
    print(f"\nImprovement: {improvement:.2f}%")
