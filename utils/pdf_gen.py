import io
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor, white, black, Color
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import qrcode
    from PIL import Image
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


RED_PRIMARY = HexColor('#B91C1C')
RED_DARK = HexColor('#7F1D1D')
RED_LIGHT = HexColor('#FEE2E2')
GRAY_DARK = HexColor('#1F2937')
GRAY_MEDIUM = HexColor('#6B7280')
GRAY_LIGHT = HexColor('#F3F4F6')
ACCENT_GOLD = HexColor('#D97706')


def get_site_settings():
    try:
        from models import SiteSetting
        settings = {}
        for s in SiteSetting.query.all():
            settings[s.key] = s.value
        return settings
    except Exception:
        return {}


def draw_rounded_rect(c, x, y, width, height, radius, fill_color=None, stroke_color=None, stroke_width=1):
    c.saveState()
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    
    p = c.beginPath()
    p.moveTo(x + radius, y)
    p.lineTo(x + width - radius, y)
    p.arcTo(x + width - radius, y, x + width, y + radius, radius)
    p.lineTo(x + width, y + height - radius)
    p.arcTo(x + width, y + height - radius, x + width - radius, y + height, radius)
    p.lineTo(x + radius, y + height)
    p.arcTo(x + radius, y + height, x, y + height - radius, radius)
    p.lineTo(x, y + radius)
    p.arcTo(x, y + radius, x + radius, y, radius)
    p.close()
    
    if fill_color and stroke_color:
        c.drawPath(p, fill=1, stroke=1)
    elif fill_color:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke_color:
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def generate_missing_person_pdf(disparu, base_url='https://disparus.org'):
    if not HAS_REPORTLAB:
        return None
    
    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFillColor(RED_PRIMARY)
    p.rect(0, height - 5*cm, width, 5*cm, fill=1, stroke=0)
    
    p.setFillColor(RED_DARK)
    p.rect(0, height - 5.3*cm, width, 0.3*cm, fill=1, stroke=0)
    
    p.setFillColor(ACCENT_GOLD)
    p.rect(0, height - 5.5*cm, width, 0.2*cm, fill=1, stroke=0)
    
    logo_drawn = False
    logo_path = settings.get('site_logo')
    if logo_path:
        full_path = f'statics/{logo_path}' if not logo_path.startswith('statics/') else logo_path
        if os.path.exists(full_path):
            try:
                logo = ImageReader(full_path)
                p.drawImage(logo, 1.5*cm, height - 4*cm, width=2.5*cm, height=2.5*cm, preserveAspectRatio=True, mask='auto')
                logo_drawn = True
            except Exception:
                pass
    
    if not logo_drawn:
        p.setFillColor(white)
        p.circle(2.75*cm, height - 2.75*cm, 1.2*cm, fill=1, stroke=0)
        p.setFillColor(RED_PRIMARY)
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(2.75*cm, height - 3*cm, "D")
    
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 32)
    p.drawString(5*cm, height - 2.8*cm, site_name)
    
    p.setFont("Helvetica", 11)
    p.drawString(5*cm, height - 4*cm, "Plateforme citoyenne pour personnes disparues")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 1.5*cm, height - 2.8*cm, f"ID: {disparu.public_id}")
    
    p.setFillColor(RED_DARK)
    p.setFont("Helvetica-Bold", 42)
    title_y = height - 7.5*cm
    p.drawCentredString(width/2, title_y, "PERSONNE DISPARUE")
    
    p.setFillColor(GRAY_MEDIUM)
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, title_y - 1.2*cm, "MISSING PERSON")
    
    p.setStrokeColor(RED_PRIMARY)
    p.setLineWidth(3)
    p.line(3*cm, title_y - 1.8*cm, width - 3*cm, title_y - 1.8*cm)
    
    p.setStrokeColor(ACCENT_GOLD)
    p.setLineWidth(1)
    p.line(5*cm, title_y - 2*cm, width - 5*cm, title_y - 2*cm)
    
    photo_x = 2*cm
    photo_y = height - 18*cm
    photo_width = 7*cm
    photo_height = 8*cm
    
    draw_rounded_rect(p, photo_x - 3*mm, photo_y - 3*mm, photo_width + 6*mm, photo_height + 6*mm, 5*mm, stroke_color=RED_PRIMARY, stroke_width=3)
    
    photo_loaded = False
    if disparu.photo_url:
        photo_path = disparu.photo_url.replace('/statics/', 'statics/')
        if os.path.exists(photo_path):
            try:
                photo = ImageReader(photo_path)
                p.drawImage(photo, photo_x, photo_y, width=photo_width, height=photo_height, preserveAspectRatio=True)
                photo_loaded = True
            except Exception:
                pass
    
    if not photo_loaded:
        sex = getattr(disparu, 'sex', 'unknown') or 'unknown'
        placeholder_key = 'placeholder_male' if sex.lower() in ['m', 'male', 'homme', 'masculin'] else 'placeholder_female'
        placeholder_path = settings.get(placeholder_key, '')
        if placeholder_path:
            full_placeholder = placeholder_path.replace('/statics/', 'statics/')
            if os.path.exists(full_placeholder):
                try:
                    photo = ImageReader(full_placeholder)
                    p.drawImage(photo, photo_x, photo_y, width=photo_width, height=photo_height, preserveAspectRatio=True)
                    photo_loaded = True
                except Exception:
                    pass
    
    if not photo_loaded:
        draw_rounded_rect(p, photo_x, photo_y, photo_width, photo_height, 3*mm, fill_color=GRAY_LIGHT)
        p.setFillColor(GRAY_MEDIUM)
        p.setFont("Helvetica", 12)
        p.drawCentredString(photo_x + photo_width/2, photo_y + photo_height/2 + 0.3*cm, "Photo non")
        p.drawCentredString(photo_x + photo_width/2, photo_y + photo_height/2 - 0.3*cm, "disponible")
    
    info_x = 10*cm
    info_y = height - 10.5*cm
    
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica-Bold", 28)
    name = f"{disparu.first_name} {disparu.last_name}"
    if len(name) > 25:
        p.setFont("Helvetica-Bold", 22)
    p.drawString(info_x, info_y, name)
    
    info_y -= 1.5*cm
    
    draw_rounded_rect(p, info_x - 2*mm, info_y - 2.8*cm, 8.5*cm, 3.2*cm, 3*mm, fill_color=RED_LIGHT)
    
    details = [
        ("Age:", f"{disparu.age} ans / years old"),
        ("Sexe / Gender:", disparu.sex or "Non specifie"),
        ("Lieu / Location:", f"{disparu.city}, {disparu.country}"),
        ("Date:", disparu.disappearance_date.strftime('%d/%m/%Y') if disparu.disappearance_date else "Non specifie"),
    ]
    
    for label, value in details:
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(RED_DARK)
        p.drawString(info_x, info_y, label)
        p.setFont("Helvetica", 11)
        p.setFillColor(GRAY_DARK)
        label_width = p.stringWidth(label, "Helvetica-Bold", 11)
        p.drawString(info_x + label_width + 3*mm, info_y, value[:35])
        info_y -= 0.65*cm
    
    section_y = height - 19*cm
    
    p.setFillColor(RED_PRIMARY)
    p.rect(2*cm - 2*mm, section_y - 0.2*cm, 4*mm, 0.6*cm, fill=1, stroke=0)
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2*cm + 5*mm, section_y, "DESCRIPTION PHYSIQUE / PHYSICAL DESCRIPTION")
    
    p.setStrokeColor(GRAY_LIGHT)
    p.setLineWidth(1)
    p.line(2*cm, section_y - 4*mm, width - 2*cm, section_y - 4*mm)
    
    section_y -= 1*cm
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica", 11)
    
    description = disparu.physical_description or "Aucune description disponible / No description available"
    max_chars = 90
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
    
    for line in lines[:5]:
        p.drawString(2*cm, section_y, line)
        section_y -= 0.5*cm
    
    if disparu.circumstances:
        section_y -= 0.5*cm
        
        p.setFillColor(RED_PRIMARY)
        p.rect(2*cm - 2*mm, section_y - 0.2*cm, 4*mm, 0.6*cm, fill=1, stroke=0)
        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm + 5*mm, section_y, "CIRCONSTANCES / CIRCUMSTANCES")
        
        p.setStrokeColor(GRAY_LIGHT)
        p.line(2*cm, section_y - 4*mm, width - 2*cm, section_y - 4*mm)
        
        section_y -= 1*cm
        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica", 11)
        
        circ_text = disparu.circumstances[:350]
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
            p.drawString(2*cm, section_y, line)
            section_y -= 0.5*cm
    
    contacts = getattr(disparu, 'contacts', [])
    if contacts:
        section_y -= 0.5*cm
        
        p.setFillColor(RED_PRIMARY)
        p.rect(2*cm - 2*mm, section_y - 0.2*cm, 4*mm, 0.6*cm, fill=1, stroke=0)
        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm + 5*mm, section_y, "CONTACTS")
        
        p.setStrokeColor(GRAY_LIGHT)
        p.line(2*cm, section_y - 4*mm, 12*cm, section_y - 4*mm)
        
        section_y -= 0.8*cm
        p.setFont("Helvetica", 11)
        
        for contact in contacts[:3]:
            contact_name = contact.get('name', '') if isinstance(contact, dict) else getattr(contact, 'name', '')
            contact_phone = contact.get('phone', '') if isinstance(contact, dict) else getattr(contact, 'phone', '')
            if contact_name and contact_phone:
                p.setFillColor(GRAY_DARK)
                p.drawString(2*cm, section_y, f"{contact_name}: {contact_phone}")
                section_y -= 0.5*cm
    
    qr_x = width - 6*cm
    qr_y = 3*cm
    qr_size = 4*cm
    
    draw_rounded_rect(p, qr_x - 5*mm, qr_y - 5*mm, qr_size + 1*cm, qr_size + 2*cm, 5*mm, fill_color=GRAY_LIGHT, stroke_color=RED_PRIMARY, stroke_width=2)
    
    qr_url = f"{base_url}/disparu/{disparu.public_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#7F1D1D", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        p.drawImage(qr_reader, qr_x, qr_y + 0.8*cm, width=qr_size, height=qr_size)
    except Exception:
        pass
    
    p.setFillColor(RED_DARK)
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(qr_x + qr_size/2, qr_y + 0.3*cm, "SCANNEZ / SCAN")
    
    p.setFillColor(RED_PRIMARY)
    p.rect(0, 0, width, 2*cm, fill=1, stroke=0)
    
    p.setFillColor(ACCENT_GOLD)
    p.rect(0, 2*cm, width, 0.2*cm, fill=1, stroke=0)
    
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, 1.2*cm, f"{base_url}")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, 0.5*cm, "Si vous avez des informations, contactez-nous! / If you have information, contact us!")
    
    p.setFillColor(GRAY_MEDIUM)
    p.setFont("Helvetica", 8)
    p.drawString(2*cm, 2.5*cm, f"Document genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer


def generate_qr_code(data, size=10):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#7F1D1D", back_color="white")
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
    
    width, height = 1080, 1350
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    try:
        font_site = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        font_tagline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_id = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_alert = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_contact_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_contact = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_link = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font_site = font_tagline = font_id = font_alert = font_name = font_label = font_value = font_contact_title = font_contact = font_link = ImageFont.load_default()
    
    draw.rectangle([0, 0, width, 100], fill='#DC2626')
    draw.text((50, 35), site_name, fill='#FFFFFF', font=font_site, anchor='lm')
    draw.text((50, 70), "Plateforme citoyenne", fill='#FEE2E2', font=font_tagline, anchor='lm')
    draw.text((width - 50, 50), f"ID: {disparu.public_id}", fill='#FFFFFF', font=font_id, anchor='rm')
    
    draw.rectangle([0, 100, width, 170], fill='#1F2937')
    draw.text((width//2, 135), "PERSONNE DISPARUE", fill='#FFFFFF', font=font_alert, anchor='mm')
    
    content_y = 200
    photo_x = 50
    photo_size = 480
    
    draw.rectangle([photo_x - 3, content_y - 3, photo_x + photo_size + 3, content_y + photo_size + 3], outline='#E5E7EB', width=3)
    
    photo_loaded = False
    if disparu.photo_url:
        photo_path = disparu.photo_url.replace('/statics/', 'statics/')
        if os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                min_dim = min(photo.width, photo.height)
                left = (photo.width - min_dim) // 2
                top = (photo.height - min_dim) // 2
                photo = photo.crop((left, top, left + min_dim, top + min_dim))
                photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
                img.paste(photo, (photo_x, content_y))
                photo_loaded = True
            except Exception:
                pass
    
    if not photo_loaded:
        sex = getattr(disparu, 'sex', 'unknown') or 'unknown'
        placeholder_key = 'placeholder_male' if sex.lower() in ['m', 'male', 'homme', 'masculin'] else 'placeholder_female'
        placeholder_path = settings.get(placeholder_key, '')
        if placeholder_path:
            full_placeholder = placeholder_path.replace('/statics/', 'statics/')
            if os.path.exists(full_placeholder):
                try:
                    photo = Image.open(full_placeholder)
                    photo = photo.convert('RGB')
                    min_dim = min(photo.width, photo.height)
                    left = (photo.width - min_dim) // 2
                    top = (photo.height - min_dim) // 2
                    photo = photo.crop((left, top, left + min_dim, top + min_dim))
                    photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
                    img.paste(photo, (photo_x, content_y))
                    photo_loaded = True
                except Exception:
                    pass
    
    if not photo_loaded:
        draw.rectangle([photo_x, content_y, photo_x + photo_size, content_y + photo_size], fill='#F3F4F6')
        cx, cy = photo_x + photo_size//2, content_y + photo_size//2
        draw.ellipse([cx - 70, cy - 130, cx + 70, cy - 20], fill='#D1D5DB')
        draw.ellipse([cx - 100, cy - 10, cx + 100, cy + 130], fill='#D1D5DB')
    
    info_x = photo_x + photo_size + 40
    info_width = width - info_x - 50
    info_y = content_y + 20
    
    name = f"{disparu.first_name} {disparu.last_name}"
    draw.text((info_x, info_y), name.upper(), fill='#1F2937', font=font_name)
    
    info_y += 70
    draw.text((info_x, info_y), "AGE", fill='#6B7280', font=font_label)
    draw.text((info_x, info_y + 25), f"{disparu.age} ans", fill='#1F2937', font=font_value)
    
    info_y += 80
    draw.text((info_x, info_y), "SEXE", fill='#6B7280', font=font_label)
    sex_text = "Homme" if disparu.sex and disparu.sex.lower() in ['m', 'male', 'homme', 'masculin'] else "Femme" if disparu.sex else "N/A"
    draw.text((info_x, info_y + 25), sex_text, fill='#1F2937', font=font_value)
    
    info_y += 80
    draw.text((info_x, info_y), "LOCALISATION", fill='#6B7280', font=font_label)
    location = f"{disparu.city}"
    draw.text((info_x, info_y + 25), location, fill='#1F2937', font=font_value)
    draw.text((info_x, info_y + 55), disparu.country, fill='#6B7280', font=font_value)
    
    info_y += 110
    if disparu.disappearance_date:
        draw.text((info_x, info_y), "DISPARU(E) LE", fill='#6B7280', font=font_label)
        date_str = disparu.disappearance_date.strftime('%d/%m/%Y')
        time_str = disparu.disappearance_date.strftime('%H:%M')
        if time_str and time_str != "00:00":
            draw.text((info_x, info_y + 25), f"{date_str} a {time_str}", fill='#DC2626', font=font_value)
        else:
            draw.text((info_x, info_y + 25), date_str, fill='#DC2626', font=font_value)
    
    footer_start = content_y + photo_size + 50
    draw.rectangle([0, footer_start, width, height], fill='#1F2937')
    
    draw.text((width//2, footer_start + 30), "CONTACTEZ-NOUS", fill='#FFFFFF', font=font_contact_title, anchor='mm')
    
    contacts = getattr(disparu, 'contacts', None)
    contact_y = footer_start + 70
    if contacts and len(contacts) > 0:
        for i, contact in enumerate(contacts[:2]):
            if isinstance(contact, dict):
                name_c = contact.get('name', '')
                phone = contact.get('phone', '')
                if phone:
                    if name_c:
                        draw.text((width//2, contact_y), f"{name_c}: {phone}", fill='#FFFFFF', font=font_contact, anchor='mm')
                    else:
                        draw.text((width//2, contact_y), phone, fill='#FFFFFF', font=font_contact, anchor='mm')
                    contact_y += 50
    else:
        draw.text((width//2, contact_y), "Voir la fiche pour plus d'infos", fill='#9CA3AF', font=font_value, anchor='mm')
        contact_y += 50
    
    link_y = height - 100
    draw.rectangle([0, link_y, width, height], fill='#DC2626')
    
    profile_url = f"{base_url}/disparu/{disparu.public_id}"
    draw.text((50, link_y + 30), "Fiche complete:", fill='#FEE2E2', font=font_tagline, anchor='lm')
    draw.text((50, link_y + 60), profile_url, fill='#FFFFFF', font=font_link, anchor='lm')
    draw.text((width - 50, link_y + 50), base_url, fill='#FFFFFF', font=font_site, anchor='rm')
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    return buffer
