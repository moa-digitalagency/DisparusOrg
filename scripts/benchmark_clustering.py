import os
import sys

# Set environment variables BEFORE importing app or config
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test'

import time
import random
import string
from datetime import datetime

# Add root directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Disparu
from algorithms.clustering import find_hotspots

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def setup_database(app, count=1000):
    with app.app_context():
        db.drop_all()
        db.create_all()

        disparus = []
        print(f"Generating {count} records...")
        for i in range(count):
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
                latitude=random.uniform(-90, 90),
                longitude=random.uniform(-180, 180),
                status='missing'
            )
            disparus.append(d)

        db.session.bulk_save_objects(disparus)
        db.session.commit()
        print(f"Database populated with {count} records.")

def run_benchmark(app):
    with app.app_context():
        print("Warming up DB connection...")
        Disparu.query.first()

        print("Running find_hotspots...")
        start_time = time.time()
        hotspots = find_hotspots(min_cases=3, radius_km=50)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Found {len(hotspots)} hotspots.")
        return duration

if __name__ == "__main__":
    app = create_app()

    # Use enough records to make O(N^2) painful.
    record_count = 2000

    setup_database(app, count=record_count)

    duration = run_benchmark(app)
    print(f"\nExecution time for {record_count} records: {duration:.4f} seconds")
