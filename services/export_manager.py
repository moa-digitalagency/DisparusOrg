"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Service pour la gestion des exports (CSV, JSON, PDF)
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import csv
import io
import json
from datetime import datetime, timedelta
from models import Disparu, db
from utils.i18n import get_translation
from utils.pdf_gen import generate_statistics_pdf as utils_generate_stats_pdf


def generate_stats_csv_stream(start_date_str=None, end_date_str=None, locale='fr'):
    """
    Generates a CSV stream of statistics (list of Disparus) for a given period.
    """
    start_date = None
    end_date = datetime.now()

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                 end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            pass

    q = Disparu.query
    if start_date:
        q = q.filter(Disparu.created_at >= start_date, Disparu.created_at <= end_date)

    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        get_translation('admin.export.header.id', locale),
        get_translation('admin.export.header.name', locale),
        get_translation('admin.export.header.type', locale),
        get_translation('admin.export.header.status', locale),
        get_translation('admin.export.header.country', locale),
        get_translation('admin.export.header.city', locale),
        get_translation('admin.export.header.views', locale),
        get_translation('admin.export.header.created_at', locale)
    ]
    writer.writerow(headers)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for d in q.yield_per(100):
        writer.writerow([
            d.public_id,
            f"{d.first_name} {d.last_name}",
            d.person_type,
            d.status,
            d.country,
            d.city,
            d.view_count,
            d.created_at.strftime('%Y-%m-%d') if d.created_at else ''
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


def generate_stats_pdf(data, locale='fr', generated_by='System'):
    """
    Generates a PDF buffer for statistics.
    Wraps the utility function.
    """
    def t(key, **kwargs):
        text = get_translation(key, locale)
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text

    return utils_generate_stats_pdf(data, t, locale=locale, generated_by=generated_by)


def _get_disparu_dict(d):
    return {
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
        'contacts': d.contacts,
        'status': d.status,
        'created_at': d.created_at.isoformat() if d.created_at else None,
        'disappearance_date': d.disappearance_date.isoformat() if d.disappearance_date else None
    }


def generate_data_csv_stream(country=None):
    """
    Generates a CSV stream of full Disparu data.
    """
    q = Disparu.query
    if country:
        q = q.filter_by(country=country)

    output = io.StringIO()
    fieldnames = [
        'public_id', 'first_name', 'last_name', 'age', 'sex', 'person_type',
        'country', 'city', 'latitude', 'longitude', 'physical_description',
        'circumstances', 'contacts', 'status', 'created_at', 'disappearance_date'
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for d in q.yield_per(100):
        item = _get_disparu_dict(d)

        sanitized_row = {}
        for k, v in item.items():
            if isinstance(v, str) and v.startswith(('=', '+', '-', '@')):
                sanitized_row[k] = "'" + v
            else:
                sanitized_row[k] = v

        writer.writerow(sanitized_row)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


def generate_data_json_stream(country=None):
    """
    Generates a JSON stream of full Disparu data.
    """
    q = Disparu.query
    if country:
        q = q.filter_by(country=country)

    yield '['
    first = True
    for d in q.yield_per(100):
        if not first:
            yield ','
        first = False
        yield json.dumps(_get_disparu_dict(d), ensure_ascii=False)
    yield ']'
