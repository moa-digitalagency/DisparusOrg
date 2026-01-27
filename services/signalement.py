"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Service de gestion des signalements
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import os
import random
import string
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from models import db, Disparu


def generate_public_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_signalement(form_data, photo_file=None):
    photo_url = None
    if photo_file and photo_file.filename:
        filename = secure_filename(photo_file.filename)
        unique_name = f"{generate_public_id()}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        photo_file.save(filepath)
        photo_url = f"/statics/uploads/{unique_name}"
    
    contacts = []
    for i in range(3):
        name = form_data.get(f'contact_name_{i}')
        phone = form_data.get(f'contact_phone_{i}')
        if name and phone:
            contacts.append({
                'name': name,
                'phone': phone,
                'email': form_data.get(f'contact_email_{i}', ''),
                'relation': form_data.get(f'contact_relation_{i}', '')
            })
    
    lat = form_data.get('latitude')
    lng = form_data.get('longitude')
    
    disparu = Disparu(
        public_id=generate_public_id(),
        person_type=form_data['person_type'],
        first_name=form_data['first_name'],
        last_name=form_data['last_name'],
        age=int(form_data['age']),
        sex=form_data['sex'],
        country=form_data['country'],
        city=form_data['city'],
        physical_description=form_data['physical_description'],
        photo_url=photo_url,
        disappearance_date=datetime.fromisoformat(form_data['disappearance_date']),
        circumstances=form_data['circumstances'],
        latitude=float(lat) if lat else None,
        longitude=float(lng) if lng else None,
        clothing=form_data.get('clothing', ''),
        objects=form_data.get('objects', ''),
        contacts=contacts,
    )
    
    db.session.add(disparu)
    db.session.commit()
    
    return disparu


def update_signalement(public_id, form_data):
    disparu = Disparu.query.filter_by(public_id=public_id).first()
    if not disparu:
        return None
    
    for key, value in form_data.items():
        if hasattr(disparu, key) and key not in ['id', 'public_id', 'created_at']:
            setattr(disparu, key, value)
    
    db.session.commit()
    return disparu


def delete_signalement(public_id):
    disparu = Disparu.query.filter_by(public_id=public_id).first()
    if disparu:
        db.session.delete(disparu)
        db.session.commit()
        return True
    return False
