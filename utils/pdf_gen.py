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
    
    draw.rectangle([0, 0, width, 180], fill='#B91C1C')
    draw.rectangle([0, 180, width, 195], fill='#7F1D1D')
    
    try:
        font_site = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_alert = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_id = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except Exception:
        font_site = font_alert = font_name = font_label = font_value = font_medium = font_small = font_id = ImageFont.load_default()
    
    logo_path = settings.get('site_logo')
    logo_drawn = False
    if logo_path:
        full_path = f'statics/{logo_path}' if not logo_path.startswith('statics/') else logo_path
        if os.path.exists(full_path):
            try:
                logo = Image.open(full_path)
                logo = logo.convert('RGBA')
                logo.thumbnail((120, 120), Image.Resampling.LANCZOS)
                img.paste(logo, (40, 30), logo if logo.mode == 'RGBA' else None)
                logo_drawn = True
            except Exception:
                pass
    
    text_x = 180 if logo_drawn else 40
    draw.text((text_x, 50), site_name, fill='#FFFFFF', font=font_site)
    draw.text((text_x, 105), "Plateforme citoyenne", fill='#FEE2E2', font=font_small)
    draw.text((width - 180, 70), f"ID: {disparu.public_id}", fill='#FFFFFF', font=font_id)
    
    draw.rectangle([0, 195, width, 280], fill='#FEE2E2')
    draw.text((width//2, 220), "PERSONNE DISPARUE", fill='#B91C1C', font=font_alert, anchor='mm')
    draw.text((width//2, 260), "MISSING PERSON", fill='#7F1D1D', font=font_medium, anchor='mm')
    
    photo_y = 310
    photo_width = 700
    photo_height = 520
    photo_x = (width - photo_width) // 2
    
    draw.rectangle([photo_x - 8, photo_y - 8, photo_x + photo_width + 8, photo_y + photo_height + 8], outline='#B91C1C', width=6)
    
    photo_loaded = False
    if disparu.photo_url:
        photo_path = disparu.photo_url.replace('/statics/', 'statics/')
        if os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                photo_ratio = photo.width / photo.height
                target_ratio = photo_width / photo_height
                if photo_ratio > target_ratio:
                    new_height = photo_height
                    new_width = int(new_height * photo_ratio)
                else:
                    new_width = photo_width
                    new_height = int(new_width / photo_ratio)
                photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - photo_width) // 2
                top = (new_height - photo_height) // 2
                photo = photo.crop((left, top, left + photo_width, top + photo_height))
                img.paste(photo, (photo_x, photo_y))
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
                    photo_ratio = photo.width / photo.height
                    target_ratio = photo_width / photo_height
                    if photo_ratio > target_ratio:
                        new_height = photo_height
                        new_width = int(new_height * photo_ratio)
                    else:
                        new_width = photo_width
                        new_height = int(new_width / photo_ratio)
                    photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    left = (new_width - photo_width) // 2
                    top = (new_height - photo_height) // 2
                    photo = photo.crop((left, top, left + photo_width, top + photo_height))
                    img.paste(photo, (photo_x, photo_y))
                    photo_loaded = True
                except Exception:
                    pass
    
    if not photo_loaded:
        draw.rectangle([photo_x, photo_y, photo_x + photo_width, photo_y + photo_height], fill='#F3F4F6')
        draw.text((width//2, photo_y + photo_height//2 - 20), "Photo non disponible", fill='#6B7280', font=font_value, anchor='mm')
        draw.text((width//2, photo_y + photo_height//2 + 20), "Photo not available", fill='#9CA3AF', font=font_medium, anchor='mm')
    
    info_y = photo_y + photo_height + 40
    name = f"{disparu.first_name} {disparu.last_name}"
    draw.text((width//2, info_y), name.upper(), fill='#1F2937', font=font_name, anchor='mm')
    
    info_y += 60
    draw.rectangle([60, info_y, width - 60, info_y + 180], fill='#F9FAFB', outline='#E5E7EB', width=2)
    
    col1_x = 100
    col2_x = width // 2 + 40
    row_y = info_y + 25
    
    draw.text((col1_x, row_y), "AGE", fill='#6B7280', font=font_label)
    draw.text((col1_x, row_y + 28), f"{disparu.age} ans", fill='#1F2937', font=font_value)
    
    sex_display = "Homme" if disparu.sex and disparu.sex.lower() in ['m', 'male', 'homme', 'masculin'] else "Femme" if disparu.sex else "N/A"
    draw.text((col2_x, row_y), "SEXE", fill='#6B7280', font=font_label)
    draw.text((col2_x, row_y + 28), sex_display, fill='#1F2937', font=font_value)
    
    row_y += 85
    draw.text((col1_x, row_y), "LOCALISATION", fill='#6B7280', font=font_label)
    location = f"{disparu.city}, {disparu.country}"
    if len(location) > 35:
        location = location[:32] + "..."
    draw.text((col1_x, row_y + 28), location, fill='#1F2937', font=font_value)
    
    if disparu.disappearance_date:
        draw.text((col2_x, row_y), "DISPARU(E) LE", fill='#6B7280', font=font_label)
        date_str = disparu.disappearance_date.strftime('%d/%m/%Y')
        draw.text((col2_x, row_y + 28), date_str, fill='#B91C1C', font=font_value)
    
    qr_section_y = info_y + 200
    qr_size = 140
    qr_x = width // 2 - qr_size // 2
    qr_url = f"{base_url}/disparu/{disparu.public_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#7F1D1D", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        img.paste(qr_img, (qr_x, qr_section_y))
        draw.text((width//2, qr_section_y + qr_size + 10), "Scannez pour plus d'informations", fill='#6B7280', font=font_small, anchor='mm')
    except Exception:
        pass
    
    footer_y = height - 100
    draw.rectangle([0, footer_y, width, height], fill='#B91C1C')
    draw.rectangle([0, footer_y - 5, width, footer_y], fill='#D97706')
    
    draw.text((width//2, footer_y + 30), base_url, fill='#FFFFFF', font=font_site, anchor='mm')
    draw.text((width//2, footer_y + 70), "Si vous avez des informations, contactez-nous!", fill='#FEE2E2', font=font_small, anchor='mm')
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    return buffer
