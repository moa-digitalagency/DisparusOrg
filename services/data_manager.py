"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Service pour la gestion des données (Backup, Restore, Delete)
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import json
from datetime import datetime
from models import db, Disparu, Contribution, ModerationReport


def generate_backup_stream(country=None):
    """
    Generates a full backup JSON stream.
    """
    # Header
    yield '{'
    yield f'"version": "1.0",'
    yield f'"created_at": "{datetime.now().isoformat()}",'
    yield f'"country": "{country or "all"}",'

    # Disparus
    yield '"disparus": ['

    q_disparu = Disparu.query
    if country:
        q_disparu = q_disparu.filter_by(country=country)

    first = True
    for d in q_disparu.yield_per(100):
        if not first:
            yield ','
        first = False

        d_dict = {
            'public_id': d.public_id,
            'first_name': d.first_name,
            'last_name': d.last_name,
            'age': d.age,
            'sex': d.sex,
            'person_type': d.person_type,
            'country': d.country,
            'city': d.city,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'physical_description': d.physical_description,
            'circumstances': d.circumstances,
            'disappearance_date': d.disappearance_date.isoformat() if d.disappearance_date else None,
            'clothing': d.clothing,
            'objects': d.objects,
            'contacts': d.contacts,
            'photo_url': d.photo_url,
            'status': d.status,
            'is_flagged': d.is_flagged,
            'view_count': d.view_count,
            'created_at': d.created_at.isoformat() if d.created_at else None,
            'updated_at': d.updated_at.isoformat() if d.updated_at else None
        }
        yield json.dumps(d_dict, ensure_ascii=False)

    yield '],'

    # Contributions
    yield '"contributions": ['

    q_contrib_joined = db.session.query(Contribution, Disparu).join(Disparu)
    if country:
        q_contrib_joined = q_contrib_joined.filter(Disparu.country == country)

    first = True
    for c, d in q_contrib_joined.yield_per(100):
        if not first:
            yield ','
        first = False

        c_dict = {
            'disparu_public_id': d.public_id if d else None,
            'contributor_name': c.contact_name or c.contributor_name,
            'contributor_phone': c.contact_phone,
            'contributor_email': c.contact_email,
            'content': c.details or c.content,
            'location': c.location_name or c.location,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'sighting_date': c.observation_date.isoformat() if c.observation_date else None,
            'is_approved': c.is_approved,
            'created_at': c.created_at.isoformat() if c.created_at else None
        }
        yield json.dumps(c_dict, ensure_ascii=False)

    yield '],'

    # Reports
    yield '"moderation_reports": ['

    q_report = db.session.query(ModerationReport, Disparu).join(Disparu, ModerationReport.target_id == Disparu.id).filter(ModerationReport.target_type == 'disparu')
    if country:
        q_report = q_report.filter(Disparu.country == country)

    first = True
    for r, d in q_report.yield_per(100):
        if not first:
            yield ','
        first = False

        r_dict = {
            'disparu_public_id': d.public_id if d else None,
            'target_type': r.target_type,
            'target_id': r.target_id,
            'reason': r.reason,
            'details': r.details,
            'reporter_contact': r.reporter_contact,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None
        }
        yield json.dumps(r_dict, ensure_ascii=False)

    yield ']'
    yield '}'


def validate_disparu_data(data):
    """
    Strict validation of Disparu data structure.
    Raises ValueError if validation fails.
    """
    required_fields = [
        'public_id', 'first_name', 'last_name', 'age', 'sex', 'person_type',
        'country', 'city', 'disappearance_date', 'physical_description', 'status'
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Missing mandatory field: {field}")

    # Type validation
    if not isinstance(data.get('age'), int):
         # Try to convert if it's a string digit
         try:
             data['age'] = int(data['age'])
         except:
             raise ValueError("Field 'age' must be an integer")

    if not isinstance(data.get('public_id'), str):
        raise ValueError("Field 'public_id' must be a string")

    # Date format validation
    try:
        if isinstance(data.get('disappearance_date'), str):
            datetime.fromisoformat(data['disappearance_date'].replace('Z', '+00:00'))
    except ValueError:
        raise ValueError("Field 'disappearance_date' must be a valid ISO format string")


def restore_from_json(file_content):
    """
    Restores data from a JSON string.
    Returns a dict with stats: {restored, skipped, errors}
    """
    try:
        backup = json.loads(file_content)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON file")

    restored_count = 0
    skipped_count = 0 # Duplicates
    error_count = 0   # Validation errors

    # Optimization: Fetch all existing public_ids in a single query
    backup_disparus = backup.get('disparus', [])
    backup_public_ids = [d.get('public_id') for d in backup_disparus if d.get('public_id')]

    existing_public_ids = set()
    if backup_public_ids:
            # Process in chunks to avoid hitting SQL parameter limits
            chunk_size = 1000
            for i in range(0, len(backup_public_ids), chunk_size):
                chunk = backup_public_ids[i:i + chunk_size]
                existing_query = Disparu.query.filter(Disparu.public_id.in_(chunk)).with_entities(Disparu.public_id).all()
                existing_public_ids.update(r[0] for r in existing_query)

    for d_data in backup_disparus:
        if d_data.get('public_id') in existing_public_ids:
            skipped_count += 1
            continue

        try:
            validate_disparu_data(d_data)
        except ValueError as e:
            # Skip invalid record
            error_count += 1
            continue

        d = Disparu()
        d.public_id = d_data.get('public_id')
        d.first_name = d_data.get('first_name')
        d.last_name = d_data.get('last_name')
        d.age = d_data.get('age')
        d.sex = d_data.get('sex', 'unknown')
        d.person_type = d_data.get('person_type', 'adult')
        d.country = d_data.get('country')
        d.city = d_data.get('city')
        d.latitude = d_data.get('latitude')
        d.longitude = d_data.get('longitude')
        d.physical_description = d_data.get('physical_description', '')
        d.circumstances = d_data.get('circumstances', '')

        # Date parsing handled safely here because validation passed
        if d_data.get('disappearance_date'):
            try:
                d.disappearance_date = datetime.fromisoformat(d_data['disappearance_date'].replace('Z', '+00:00'))
            except ValueError:
                 d.disappearance_date = datetime.now()
        else:
            d.disappearance_date = datetime.now()

        d.clothing = d_data.get('clothing')
        d.objects = d_data.get('objects')
        d.contacts = d_data.get('contacts')
        d.photo_url = d_data.get('photo_url')
        d.status = d_data.get('status', 'missing')
        d.is_flagged = d_data.get('is_flagged', False)

        db.session.add(d)
        restored_count += 1

    db.session.commit()
    return {
        'restored': restored_count,
        'skipped': skipped_count,
        'errors': error_count
    }


def delete_data_by_country(country=None):
    """
    Deletes all data, optionally filtered by country.
    Returns the number of deleted records.
    """
    q = Disparu.query
    if country:
        q = q.filter_by(country=country)

    disparus = q.all()
    disparu_ids = [d.id for d in disparus]

    if disparu_ids:
        Contribution.query.filter(Contribution.disparu_id.in_(disparu_ids)).delete(synchronize_session=False)
        ModerationReport.query.filter(ModerationReport.target_type == 'disparu', ModerationReport.target_id.in_(disparu_ids)).delete(synchronize_session=False)

    deleted_count = q.delete(synchronize_session=False)
    db.session.commit()
    return deleted_count


def delete_demo_data():
    """
    Deletes specific demo data records.
    Returns counts of deleted items.
    """
    DEMO_IDS = ['DEMO01', 'DEMO02', 'DEMO03', 'DEMO04', 'DEMO05', 'DEMO06', 'DEMO07', 'DEMO08']

    disparus = Disparu.query.filter(Disparu.public_id.in_(DEMO_IDS)).all()
    disparu_db_ids = [d.id for d in disparus]

    contrib_deleted = 0
    report_deleted = 0

    if disparu_db_ids:
        contrib_deleted = Contribution.query.filter(Contribution.disparu_id.in_(disparu_db_ids)).delete(synchronize_session=False)
        report_deleted = ModerationReport.query.filter(
            ModerationReport.target_type == 'disparu',
            ModerationReport.target_id.in_(disparu_db_ids)
        ).delete(synchronize_session=False)

    disparu_deleted = Disparu.query.filter(Disparu.public_id.in_(DEMO_IDS)).delete(synchronize_session=False)
    db.session.commit()

    return {
        'disparus': disparu_deleted,
        'contributions': contrib_deleted,
        'reports': report_deleted
    }
