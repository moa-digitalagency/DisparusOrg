from app import create_app, db
from models import Disparu
from datetime import datetime

app = create_app()
with app.app_context():
    if Disparu.query.first():
        print("Data already exists")
    else:
        d = Disparu(
            first_name="Jean",
            last_name="Dupont",
            age=30,
            sex="male",
            country="France",
            city="Paris",
            disappearance_date=datetime.now(),
            physical_description="Test description",
            circumstances="Test circumstances",
            status="missing",
            person_type="adult",
            photo_url="/static/img/favicon.png",
            public_id="TEST-001"
        )
        db.session.add(d)
        db.session.commit()
        print("Dummy created")
