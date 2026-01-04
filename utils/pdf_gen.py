import io
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    import qrcode
    from PIL import Image
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def get_site_settings():
    try:
        from models import SiteSetting
        settings = {}
        for s in SiteSetting.query.all():
            settings[s.key] = s.value
        return settings
    except Exception:
        return {}


def generate_missing_person_pdf(disparu, base_url='https://disparus.org'):
    if not HAS_REPORTLAB:
        return None
    
    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    red_primary = HexColor('#B91C1C')
    red_dark = HexColor('#7F1D1D')
    gray_dark = HexColor('#1F2937')
    gray_medium = HexColor('#6B7280')
    
    p.setFillColor(red_primary)
    p.rect(0, height - 4*cm, width, 4*cm, fill=1, stroke=0)
    
    logo_path = settings.get('site_logo')
    if logo_path and os.path.exists(f'statics/{logo_path}'):
        try:
            logo = ImageReader(f'statics/{logo_path}')
            p.drawImage(logo, 1.5*cm, height - 3.2*cm, width=2*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 28)
    p.drawString(4*cm, height - 2.5*cm, site_name)
    
    p.setFont("Helvetica", 12)
    p.drawRightString(width - 1.5*cm, height - 2.5*cm, f"ID: {disparu.public_id}")
    
    p.setFillColor(red_dark)
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(width/2, height - 6*cm, "PERSONNE DISPARUE")
    p.drawCentredString(width/2, height - 7.2*cm, "MISSING PERSON")
    
    p.setStrokeColor(red_primary)
    p.setLineWidth(2)
    p.line(2*cm, height - 7.8*cm, width - 2*cm, height - 7.8*cm)
    
    photo_x = 2*cm
    photo_y = height - 15*cm
    photo_width = 6*cm
    photo_height = 7*cm
    
    p.setStrokeColor(red_primary)
    p.setLineWidth(3)
    p.roundRect(photo_x - 2*mm, photo_y - 2*mm, photo_width + 4*mm, photo_height + 4*mm, 5*mm, fill=0, stroke=1)
    
    if disparu.photo_url and os.path.exists(f'statics/{disparu.photo_url.replace("/statics/", "")}'):
        try:
            photo = ImageReader(f'statics/{disparu.photo_url.replace("/statics/", "")}')
            p.drawImage(photo, photo_x, photo_y, width=photo_width, height=photo_height, preserveAspectRatio=True)
        except Exception:
            p.setFillColor(HexColor('#E5E7EB'))
            p.roundRect(photo_x, photo_y, photo_width, photo_height, 3*mm, fill=1, stroke=0)
            p.setFillColor(gray_medium)
            p.setFont("Helvetica", 10)
            p.drawCentredString(photo_x + photo_width/2, photo_y + photo_height/2, "Photo non disponible")
    else:
        p.setFillColor(HexColor('#E5E7EB'))
        p.roundRect(photo_x, photo_y, photo_width, photo_height, 3*mm, fill=1, stroke=0)
        p.setFillColor(gray_medium)
        p.setFont("Helvetica", 10)
        p.drawCentredString(photo_x + photo_width/2, photo_y + photo_height/2, "Photo non disponible")
    
    info_x = 9*cm
    info_y = height - 8.8*cm
    
    p.setFillColor(gray_dark)
    p.setFont("Helvetica-Bold", 24)
    name = f"{disparu.first_name} {disparu.last_name}"
    p.drawString(info_x, info_y, name)
    
    info_y -= 1.2*cm
    p.setFont("Helvetica", 14)
    p.setFillColor(gray_medium)
    
    details = [
        ("Age:", f"{disparu.age} ans"),
        ("Sexe:", disparu.sex or "Non specifie"),
        ("Lieu:", f"{disparu.city}, {disparu.country}"),
        ("Date:", disparu.disappearance_date.strftime('%d/%m/%Y') if disparu.disappearance_date else "Non specifie"),
    ]
    
    for label, value in details:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(gray_dark)
        p.drawString(info_x, info_y, label)
        p.setFont("Helvetica", 12)
        p.setFillColor(gray_medium)
        p.drawString(info_x + 2*cm, info_y, value)
        info_y -= 0.7*cm
    
    desc_y = height - 16*cm
    p.setFillColor(red_primary)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2*cm, desc_y, "DESCRIPTION PHYSIQUE")
    
    p.setStrokeColor(red_primary)
    p.setLineWidth(1)
    p.line(2*cm, desc_y - 3*mm, width - 2*cm, desc_y - 3*mm)
    
    desc_y -= 1*cm
    p.setFillColor(gray_dark)
    p.setFont("Helvetica", 11)
    
    description = disparu.physical_description or "Aucune description disponible"
    max_chars = 80
    lines = []
    words = description.split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line = current_line + " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for line in lines[:6]:
        p.drawString(2*cm, desc_y, line)
        desc_y -= 0.5*cm
    
    if disparu.circumstances:
        circ_y = desc_y - 0.8*cm
        p.setFillColor(red_primary)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm, circ_y, "CIRCONSTANCES")
        
        p.setStrokeColor(red_primary)
        p.line(2*cm, circ_y - 3*mm, width - 2*cm, circ_y - 3*mm)
        
        circ_y -= 1*cm
        p.setFillColor(gray_dark)
        p.setFont("Helvetica", 11)
        
        circ_text = disparu.circumstances[:300]
        circ_lines = []
        words = circ_text.split()
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line = current_line + " " + word if current_line else word
            else:
                circ_lines.append(current_line)
                current_line = word
        if current_line:
            circ_lines.append(current_line)
        
        for line in circ_lines[:4]:
            p.drawString(2*cm, circ_y, line)
            circ_y -= 0.5*cm
    
    qr_url = f"{base_url}/disparu/{disparu.public_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        p.drawImage(qr_reader, width - 5*cm, 2.5*cm, width=3.5*cm, height=3.5*cm)
        
        p.setFillColor(gray_medium)
        p.setFont("Helvetica", 8)
        p.drawCentredString(width - 3.25*cm, 2*cm, "Scannez pour plus d'infos")
    except Exception:
        pass
    
    p.setFillColor(red_primary)
    p.rect(0, 0, width, 1.5*cm, fill=1, stroke=0)
    
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, 0.7*cm, f"{base_url} - Si vous avez des informations, contactez-nous!")
    
    contacts = getattr(disparu, 'contacts', [])
    if contacts:
        contact_y = 6.5*cm
        p.setFillColor(red_primary)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm, contact_y, "CONTACTS")
        
        p.setStrokeColor(red_primary)
        p.line(2*cm, contact_y - 3*mm, 10*cm, contact_y - 3*mm)
        
        contact_y -= 0.8*cm
        p.setFillColor(gray_dark)
        p.setFont("Helvetica", 11)
        
        for contact in contacts[:3]:
            contact_name = contact.name if hasattr(contact, 'name') else str(contact.get('name', ''))
            contact_phone = contact.phone if hasattr(contact, 'phone') else str(contact.get('phone', ''))
            p.drawString(2*cm, contact_y, f"{contact_name}: {contact_phone}")
            contact_y -= 0.5*cm
    
    p.setFillColor(gray_medium)
    p.setFont("Helvetica", 8)
    p.drawString(2*cm, 2*cm, f"Document genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer


def generate_qr_code(data, size=10):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def generate_social_media_image(disparu, base_url='https://disparus.org'):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    
    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')
    
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, width, 120], fill='#B91C1C')
    
    logo_path = settings.get('site_logo')
    if logo_path and os.path.exists(f'statics/{logo_path}'):
        try:
            logo = Image.open(f'statics/{logo_path}')
            logo = logo.convert('RGBA')
            logo.thumbnail((80, 80), Image.Resampling.LANCZOS)
            img.paste(logo, (30, 20), logo if logo.mode == 'RGBA' else None)
        except Exception:
            pass
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    draw.text((130, 40), site_name, fill='#FFFFFF', font=font_title)
    draw.text((width - 200, 45), f"ID: {disparu.public_id}", fill='#FFFFFF', font=font_small)
    
    draw.text((width//2 - 180, 150), "PERSONNE DISPARUE", fill='#7F1D1D', font=font_large)
    
    draw.line([(100, 210), (width - 100, 210)], fill='#B91C1C', width=3)
    
    photo_x, photo_y = 50, 240
    photo_size = 320
    
    draw.rectangle([photo_x - 5, photo_y - 5, photo_x + photo_size + 5, photo_y + photo_size + 5], outline='#B91C1C', width=4)
    
    photo_loaded = False
    if disparu.photo_url:
        photo_path = f'statics/{disparu.photo_url.replace("/statics/", "")}'
        if os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                photo.thumbnail((photo_size, photo_size), Image.Resampling.LANCZOS)
                paste_x = photo_x + (photo_size - photo.width) // 2
                paste_y = photo_y + (photo_size - photo.height) // 2
                img.paste(photo, (paste_x, paste_y))
                photo_loaded = True
            except Exception:
                pass
    
    if not photo_loaded:
        draw.rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], fill='#E5E7EB')
        draw.text((photo_x + 60, photo_y + 140), "Photo non\ndisponible", fill='#6B7280', font=font_medium)
    
    info_x = 420
    info_y = 250
    
    name = f"{disparu.first_name} {disparu.last_name}"
    draw.text((info_x, info_y), name, fill='#1F2937', font=font_large)
    
    info_y += 70
    draw.text((info_x, info_y), f"Age: {disparu.age} ans", fill='#6B7280', font=font_medium)
    
    info_y += 45
    location = f"{disparu.city}, {disparu.country}"
    draw.text((info_x, info_y), location, fill='#6B7280', font=font_medium)
    
    info_y += 45
    if disparu.disappearance_date:
        date_str = disparu.disappearance_date.strftime('%d/%m/%Y')
        draw.text((info_x, info_y), f"Disparu(e) le: {date_str}", fill='#B91C1C', font=font_medium)
    
    qr_url = f"{base_url}/disparu/{disparu.public_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((100, 100), Image.Resampling.LANCZOS)
        img.paste(qr_img, (width - 130, 240))
        draw.text((width - 150, 350), "Plus d'infos", fill='#6B7280', font=font_small)
    except Exception:
        pass
    
    draw.rectangle([0, height - 60, width, height], fill='#B91C1C')
    draw.text((width//2 - 280, height - 45), f"{base_url} - Aidez-nous a retrouver cette personne", fill='#FFFFFF', font=font_small)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    return buffer
