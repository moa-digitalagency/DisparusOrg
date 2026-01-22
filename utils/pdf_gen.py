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
    from PIL import Image, ImageDraw, ImageFont
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
    """
    Génère une image pour les réseaux sociaux (1080x1350) 
    adaptée au style visuel rouge/bleu de l'affiche Youssef Bennani.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')

    # Dimensions (Format Portrait Social Media)
    width, height = 1080, 1350

    # Palette de couleurs extraite de l'image
    COLOR_BG = '#F4F4F4'        # Gris très clair pour le fond
    COLOR_RED = '#981B1B'       # Rouge bordeaux
    COLOR_NAVY = '#1A1F36'      # Bleu nuit
    COLOR_WHITE = '#FFFFFF'
    COLOR_BLACK = '#000000'
    COLOR_TEXT_GRAY = '#555555' # Gris foncé pour le texte
    COLOR_CONTACT_BOX = '#8B1616' # Rouge sombre pour la boite contact

    img = Image.new('RGB', (width, height), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    # --- Configuration des polices ---
    # On essaie de charger des polices grasses standard pour se rapprocher de l'impact visuel
    def get_font(variant, size):
        font_paths = []
        if variant == "Bold":
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
        return ImageFont.load_default()

    # Définition des tailles de police
    font_header_main = get_font("Bold", 34)
    font_header_meta = get_font("Regular", 24)
    font_subheader_main = get_font("Bold", 55)
    font_subheader_sub = get_font("Regular", 30)
    font_name = get_font("Bold", 65)
    font_details = get_font("Bold", 35)
    font_date = get_font("Bold", 38)
    font_contact_instr = get_font("Bold", 26)
    font_contact_name = get_font("Bold", 36)
    font_contact_phone = get_font("Bold", 55)
    font_footer_text = get_font("Bold", 26)
    font_url = get_font("Regular", 22)

    # --- 1. En-tête Rouge (Top Header) ---
    header_h = 100
    draw.rectangle([0, 0, width, header_h], fill=COLOR_RED)

    # Texte: "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!"
    draw.text((width//2, 35), "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!", fill=COLOR_WHITE, font=font_header_main, anchor='mm')

    # Meta: Site Name | ID
    draw.text((40, 75), site_name, fill=COLOR_WHITE, font=font_header_meta, anchor='lm')
    draw.text((width - 40, 75), f"ID : {disparu.public_id}", fill=COLOR_WHITE, font=font_header_meta, anchor='rm')

    # --- 2. Sous-titre Bleu (Sub-Header) ---
    sub_header_y = header_h
    sub_header_h = 130
    draw.rectangle([0, sub_header_y, width, sub_header_y + sub_header_h], fill=COLOR_NAVY)

    draw.text((width//2, sub_header_y + 45), "PERSONNE DISPARUE", fill=COLOR_WHITE, font=font_subheader_main, anchor='mm')
    # Espacement léger pour le sous-titre anglais
    draw.text((width//2, sub_header_y + 95), "MISSING PERSON", fill='#CCCCCC', font=font_subheader_sub, anchor='mm') 

    # --- 3. Section Photo ---
    photo_y = sub_header_y + sub_header_h + 50
    photo_size = 500 # Carré de 500px
    photo_x = (width - photo_size) // 2

    # Fonction locale pour charger l'image
    def load_photo_image(path):
        try:
             return Image.open(path).convert('RGBA')
        except:
            return None

    photo_img = None
    if disparu.photo_url:
        path = disparu.photo_url.replace('/statics/', 'statics/')
        if os.path.exists(path):
            photo_img = load_photo_image(path)

    # Fallback si pas de photo
    if not photo_img:
        sex = getattr(disparu, 'sex', 'unknown') or 'unknown'
        key = 'placeholder_male' if sex.lower() in ['m', 'male', 'homme', 'masculin'] else 'placeholder_female'
        p_path = settings.get(key, '')
        if p_path:
             full_p = p_path.replace('/statics/', 'statics/')
             if os.path.exists(full_p):
                 photo_img = load_photo_image(full_p)

    if photo_img:
        # Crop au format carré centré
        min_dim = min(photo_img.width, photo_img.height)
        left = (photo_img.width - min_dim) // 2
        top = (photo_img.height - min_dim) // 2
        photo_img = photo_img.crop((left, top, left + min_dim, top + min_dim))
        photo_img = photo_img.resize((photo_size, photo_size), Image.Resampling.LANCZOS)

        # Création du masque pour les coins arrondis
        mask = Image.new("L", (photo_size, photo_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle((0, 0, photo_size, photo_size), radius=40, fill=255)

        # Collage de la photo
        img.paste(photo_img, (photo_x, photo_y), mask=mask)
    else:
        # Carré gris si aucune image n'est trouvée
        draw.rounded_rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], radius=40, fill='#DDDDDD')
        draw.text((width//2, photo_y + photo_size//2), "Photo non disponible", fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    # --- 4. Informations ---
    info_y = photo_y + photo_size + 50

    # Nom complet
    name = f"{disparu.first_name} {disparu.last_name}"
    draw.text((width//2, info_y), name.upper(), fill=COLOR_BLACK, font=font_name, anchor='mm')

    info_y += 70

    # Détails: AGE - SEXE
    age_str = f"{disparu.age} ANS" if disparu.age else ""
    sex_input = getattr(disparu, 'sex', '') or ''
    sex_str = "HOMME" if sex_input.lower() in ['m', 'male', 'homme'] else "FEMME" if sex_input else ""

    details_line = " - ".join(filter(None, [age_str, sex_str]))
    draw.text((width//2, info_y), details_line, fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    info_y += 50
    # Ville, Pays
    loc_str = f"{disparu.city}, {disparu.country}".upper()
    draw.text((width//2, info_y), loc_str, fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    info_y += 70
    # Date de disparition
    date_line = "DISPARU(E)"
    if disparu.disappearance_date:
        d_str = disparu.disappearance_date.strftime('%d/%m/%Y')
        t_str = disparu.disappearance_date.strftime('%H:%M')
        if t_str and t_str != "00:00":
             date_line += f" LE {d_str} A {t_str}"
        else:
             date_line += f" LE {d_str}"

    draw.text((width//2, info_y), date_line, fill=COLOR_RED, font=font_date, anchor='mm')

    # --- 5. Boîte de Contact ---
    contact_box_top = info_y + 50
    contact_box_width = int(width * 0.92) # 92% de la largeur
    contact_box_x = (width - contact_box_width) // 2
    contact_box_height = 240

    draw.rectangle([contact_box_x, contact_box_top, contact_box_x + contact_box_width, contact_box_top + contact_box_height], fill=COLOR_CONTACT_BOX)

    c_y = contact_box_top + 45
    draw.text((width//2, c_y), "CONTACTEZ NOUS SI VOUS AVEZ UNE INFORMATION", fill=COLOR_WHITE, font=font_contact_instr, anchor='mm')

    # Récupération du premier contact
    contacts = getattr(disparu, 'contacts', [])
    contact_name_str = "FAMILLE"
    contact_phone_str = ""

    if contacts and len(contacts) > 0:
        c = contacts[0]
        if isinstance(c, dict):
            contact_name_str = c.get('name', 'FAMILLE')
            contact_phone_str = c.get('phone', '')
        else:
            contact_name_str = getattr(c, 'name', 'FAMILLE')
            contact_phone_str = getattr(c, 'phone', '')

    c_y += 60
    draw.text((width//2, c_y), contact_name_str.upper(), fill=COLOR_WHITE, font=font_contact_name, anchor='mm')

    if contact_phone_str:
        c_y += 70
        draw.text((width//2, c_y), contact_phone_str, fill=COLOR_WHITE, font=font_contact_phone, anchor='mm')

    # --- 6. Texte de pied de page (Appel au partage) ---
    footer_text_y = contact_box_top + contact_box_height + 45
    draw.text((width//2, footer_text_y), "TOUTE INFORMATION PEUT PERMETTRE DE RETROUVER CETTE PERSONNE,", fill=COLOR_RED, font=font_footer_text, anchor='mm')
    draw.text((width//2, footer_text_y + 40), "UN PARTAGE DE CETTE IMAGE PEUT AIDER A LA RECHERCHE AUSSI", fill=COLOR_RED, font=font_footer_text, anchor='mm')

    # --- 7. Barre URL en bas ---
    bottom_bar_h = 70
    draw.rectangle([0, height - bottom_bar_h, width, height], fill=COLOR_RED)

    url_text = f"{base_url}/disparu/{disparu.public_id}".upper()
    draw.text((width//2, height - bottom_bar_h/2), url_text, fill=COLOR_WHITE, font=font_url, anchor='mm')

    # Finalisation
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    return buffer