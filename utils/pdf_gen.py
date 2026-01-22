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


# Couleurs
RED_PRIMARY = HexColor('#B91C1C') # Rouge vif du PDF exemple
RED_DARK = HexColor('#7F1D1D')
RED_LIGHT = HexColor('#FEE2E2')
GRAY_DARK = HexColor('#1F2937')
GRAY_MEDIUM = HexColor('#6B7280')
GRAY_LIGHT = HexColor('#F3F4F6')
ACCENT_GOLD = HexColor('#D97706') # Couleur Or pour les soulignements secondaires
WHITE = HexColor('#FFFFFF')
BLACK = HexColor('#000000')


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
    """
    Génère un PDF A4 reproduisant le design original du site (horizontal).
    """
    if not HAS_REPORTLAB:
        return None

    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 # approx 21cm x 29.7cm

    # --- 1. En-tête (Logo + Titre Site) ---
    # Fond blanc pour le haut, pas de gros bloc rouge tout en haut comme l'affiche

    # Logo (ou Placeholder rond rouge avec 'D')
    logo_size = 2.5*cm
    logo_x = 1.5*cm
    logo_y = height - 4*cm

    logo_drawn = False
    logo_path = settings.get('site_logo')
    if logo_path:
        full_path = f'statics/{logo_path}' if not logo_path.startswith('statics/') else logo_path
        if os.path.exists(full_path):
            try:
                logo = ImageReader(full_path)
                p.drawImage(logo, logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
                logo_drawn = True
            except Exception:
                pass

    if not logo_drawn:
        # Cercle rouge avec 'D'
        p.setFillColor(WHITE) # Fond blanc sous le cercle si besoin
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0) 
        # En fait dans le PDF exemple c'est un logo graphique, on va simuler un cercle placeholder propre
        p.setFillColor(RED_PRIMARY)
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0)
        p.setFillColor(WHITE)
        p.setFont("Helvetica-Bold", 40)
        p.drawCentredString(logo_x + logo_size/2, logo_y + logo_size/2 - 10, "D")

    # Titre du site à droite du logo
    title_x = logo_x + logo_size + 0.5*cm
    title_y = height - 2.5*cm
    p.setFillColor(BLACK) # Ou gris très foncé
    p.setFont("Helvetica-Bold", 28)
    p.drawString(title_x, title_y, site_name)

    # Slogan
    p.setFont("Helvetica", 10)
    p.setFillColor(GRAY_MEDIUM)
    p.drawString(title_x, title_y - 0.6*cm, "Plateforme citoyenne pour personnes disparues")

    # ID à droite
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(BLACK)
    p.drawRightString(width - 1.5*cm, title_y, f"ID: {disparu.public_id}")

    # --- 2. Titre Principal "PERSONNE DISPARUE" ---
    main_title_y = height - 6*cm
    p.setFillColor(RED_DARK) # Rouge sombre pour le titre principal
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(width/2, main_title_y, "PERSONNE DISPARUE")

    # Sous-titre
    p.setFillColor(GRAY_MEDIUM)
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, main_title_y - 1*cm, "MISSING PERSON")

    # Lignes décoratives
    p.setStrokeColor(RED_PRIMARY)
    p.setLineWidth(3)
    p.line(3*cm, main_title_y - 1.5*cm, width - 3*cm, main_title_y - 1.5*cm) # Ligne rouge épaisse

    p.setStrokeColor(ACCENT_GOLD)
    p.setLineWidth(1)
    p.line(5*cm, main_title_y - 1.7*cm, width - 5*cm, main_title_y - 1.7*cm) # Ligne or fine

    # --- 3. Corps (Photo gauche / Infos droite) ---
    content_y = main_title_y - 3*cm
    photo_x = 2*cm
    photo_w = 7*cm
    photo_h = 8*cm

    # PAS de cadre rouge autour de la photo (modifié sur demande)
    # draw_rounded_rect(p, photo_x - 2*mm, content_y - photo_h - 2*mm, photo_w + 4*mm, photo_h + 4*mm, 5*mm, stroke_color=RED_PRIMARY, stroke_width=2)

    # Photo
    photo_loaded = False
    if disparu.photo_url:
        photo_path = disparu.photo_url.replace('/statics/', 'statics/')
        if os.path.exists(photo_path):
            try:
                photo = ImageReader(photo_path)
                # On dessine l'image
                p.drawImage(photo, photo_x, content_y - photo_h, width=photo_w, height=photo_h, preserveAspectRatio=True, mask='auto')
                photo_loaded = True
            except Exception:
                pass

    if not photo_loaded:
         # Placeholder si pas d'image
         draw_rounded_rect(p, photo_x, content_y - photo_h, photo_w, photo_h, 3*mm, fill_color=GRAY_LIGHT)
         p.setFillColor(GRAY_MEDIUM)
         p.setFont("Helvetica", 10)
         p.drawCentredString(photo_x + photo_w/2, content_y - photo_h/2, "Photo non disponible")

    # Infos à droite - TAILLE POLICE AUGMENTÉE
    info_x = photo_x + photo_w + 1*cm
    # On descend le nom un tout petit peu vers le bas (0.8cm plus bas que la photo top)
    info_y_cursor = content_y - 0.8*cm 

    # Nom
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica-Bold", 30) # Augmenté de 26 à 30
    name = f"{disparu.first_name} {disparu.last_name}"
    p.drawString(info_x, info_y_cursor, name)
    info_y_cursor -= 1.8*cm # Espacement augmenté

    # Date et Heure formatée (Séparées)
    date_val = "Non specifie"
    heure_val = ""
    if disparu.disappearance_date:
        date_val = disparu.disappearance_date.strftime('%d/%m/%Y')
        t_str = disparu.disappearance_date.strftime('%H:%M')
        if t_str and t_str != "00:00":
             heure_val = t_str

    details = [
        ("Age:", f"{disparu.age} ans / years old"),
        ("Sexe / Gender:", "Homme" if disparu.sex and disparu.sex.lower() in ['m', 'male', 'homme'] else "Femme"),
        ("Lieu / Location:", f"{disparu.city}, {disparu.country}"),
        ("Date:", date_val), 
    ]

    # Affichage des détails standard
    for label, value in details:
        p.setFillColor(RED_DARK)
        p.setFont("Helvetica-Bold", 14) 
        p.drawString(info_x, info_y_cursor, label)

        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica", 14) 
        label_w = p.stringWidth(label, "Helvetica-Bold", 14)
        p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, value)
        info_y_cursor -= 1.0*cm 

    # Ajout Heure sur la ligne suivante si elle existe
    if heure_val:
        p.setFillColor(RED_DARK)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(info_x, info_y_cursor, "Heure / Time:")

        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica", 14)
        label_w = p.stringWidth("Heure / Time:", "Helvetica-Bold", 14)
        p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, heure_val)
        info_y_cursor -= 1.0*cm

    # Ajout ID sur la ligne suivante encore
    p.setFillColor(RED_DARK)
    p.setFont("Helvetica-Bold", 14)
    label_id = "ID sur Disparus.org:"
    p.drawString(info_x, info_y_cursor, label_id)

    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica", 14)
    label_w = p.stringWidth(label_id, "Helvetica-Bold", 14)
    p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, str(disparu.public_id))
    # info_y_cursor -= 1.0*cm # Pas nécessaire pour le dernier élément

    # --- 4. Description & Circonstances ---
    section_y = content_y - photo_h - 1.5*cm

    def draw_section_block(title, content, y_pos):
        # Petit rectangle rouge puce
        p.setFillColor(RED_PRIMARY)
        p.rect(2*cm, y_pos, 0.4*cm, 0.4*cm, fill=1, stroke=0)

        # Titre
        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2.6*cm, y_pos, title)

        # Ligne grise séparation
        p.setStrokeColor(GRAY_LIGHT)
        p.setLineWidth(1)
        p.line(2*cm, y_pos - 0.2*cm, width - 2*cm, y_pos - 0.2*cm)

        # Contenu
        text_y = y_pos - 0.8*cm
        p.setFillColor(BLACK)
        p.setFont("Helvetica", 11)

        max_width = width - 4*cm
        words = content.split()
        line = ""
        for word in words:
            if p.stringWidth(line + " " + word, "Helvetica", 11) < max_width:
                line += " " + word if line else word
            else:
                p.drawString(2*cm, text_y, line)
                text_y -= 0.5*cm
                line = word
        if line:
            p.drawString(2*cm, text_y, line)
            text_y -= 0.5*cm

        return text_y - 0.5*cm

    desc = disparu.physical_description or "Non disponible."
    section_y = draw_section_block("DESCRIPTION PHYSIQUE / PHYSICAL DESCRIPTION", desc, section_y)

    circ = disparu.circumstances or "Non disponible."
    section_y = draw_section_block("CIRCONSTANCES / CIRCUMSTANCES", circ, section_y)

    # --- 5. Contacts (Bloc dédié) ---
    if section_y < 8*cm: # Si on est trop bas
        pass

    # Titre "CONTACTS"
    p.setFillColor(RED_PRIMARY)
    p.rect(2*cm, section_y, 0.4*cm, 0.4*cm, fill=1, stroke=0)
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2.6*cm, section_y, "CONTACTS")
    p.setStrokeColor(GRAY_LIGHT)
    p.line(2*cm, section_y - 0.2*cm, width - 6*cm, section_y - 0.2*cm) # Ligne plus courte

    contact_y = section_y - 1.2*cm # Espacement un peu plus grand avant le premier contact
    contacts = getattr(disparu, 'contacts', [])

    for contact in contacts[:3]:
        name = contact.get('name', '') if isinstance(contact, dict) else getattr(contact, 'name', '')
        phone = contact.get('phone', '') if isinstance(contact, dict) else getattr(contact, 'phone', '')

        if name or phone:
            p.setFillColor(BLACK)
            p.setFont("Helvetica-Bold", 18) # Augmenté de 12 à 18 (beaucoup plus grand)
            p.drawString(2*cm, contact_y, f"{name}: {phone}")
            contact_y -= 1.0*cm # Espacement vertical augmenté

    # --- 6. Footer (QR Code + Bandes couleur) ---

    # QR Code (en bas à droite, au dessus des bandes)
    qr_size = 3.5*cm
    qr_x = width - 5*cm
    qr_y = 3.5*cm 

    # PAS de cadre autour du QR Code (modifié sur demande)
    # draw_rounded_rect(p, qr_x - 0.2*cm, qr_y - 0.2*cm, qr_size + 0.4*cm, qr_size + 0.6*cm, 0.2*cm, stroke_color=RED_PRIMARY, stroke_width=1)

    url_text = f"{base_url}/disparu/{disparu.public_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(url_text)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#7F1D1D", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        p.drawImage(qr_reader, qr_x, qr_y + 0.2*cm, width=qr_size, height=qr_size)
    except:
        pass

    p.setFillColor(RED_DARK)
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(qr_x + qr_size/2, qr_y, "SCANNEZ / SCAN")

    # Bandes de bas de page
    # Bande Or fine
    p.setFillColor(ACCENT_GOLD)
    p.rect(0, 2*cm, width, 0.2*cm, fill=1, stroke=0)

    # Bande Rouge épaisse en bas
    p.setFillColor(RED_PRIMARY)
    p.rect(0, 0, width, 2*cm, fill=1, stroke=0)

    # Bande Rouge Foncé très fine tout en bas (optionnel, pour le style)
    p.setFillColor(RED_DARK)
    p.rect(0, 0, width, 0.3*cm, fill=1, stroke=0)

    # Texte dans la bande rouge
    p.setFillColor(WHITE)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, 1.2*cm, base_url)

    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, 0.6*cm, "Si vous avez des informations, contactez-nous ! / If you have information, contact us!")

    # Timestamp discret au dessus du footer
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
    avec un layout ajusté pour que tout soit visible.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    settings = get_site_settings()
    site_name = settings.get('site_name', 'DISPARUS.ORG')

    # Dimensions (Format Portrait Social Media)
    width, height = 1080, 1350

    # --- Palette de couleurs exacte du HTML ---
    COLOR_RED = '#9F1C1C'       
    COLOR_NAVY = '#1E2538'      
    COLOR_CONTACT = '#8B1818'   
    COLOR_WHITE = '#FFFFFF'
    COLOR_BG = '#FFFFFF'        
    COLOR_BLACK = '#000000'
    COLOR_TEXT_GRAY = '#4A4A4A' 

    img = Image.new('RGB', (width, height), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    def get_font(variant, size):
        font_candidates = {
            "Bold": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
                "arialbd.ttf", "Arial Bold.ttf",
            ],
            "Regular": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
                "arial.ttf", "Arial.ttf",
            ]
        }
        selected_path = None
        for path in font_candidates.get(variant, []):
            try:
                if os.path.isabs(path) and not os.path.exists(path):
                    continue
                ImageFont.truetype(path, size)
                selected_path = path
                break
            except OSError:
                continue

        if selected_path:
            return ImageFont.truetype(selected_path, size)
        else:
            return ImageFont.load_default()

    # Définition des tailles (Légèrement réduites pour l'espace)
    font_header_title = get_font("Bold", 32)
    font_header_meta = get_font("Bold", 22)
    font_subheader = get_font("Bold", 50)
    font_subheader_small = get_font("Regular", 26)
    font_name = get_font("Bold", 55)   # Réduit de 70
    font_details = get_font("Bold", 32) # Réduit de 38
    font_date = get_font("Bold", 34)    # Réduit de 40
    font_contact_instr = get_font("Bold", 24)
    font_contact_name = get_font("Bold", 36)
    font_contact_phone = get_font("Bold", 55)
    font_footer = get_font("Bold", 24)  # Réduit de 28
    font_url = get_font("Regular", 22)

    # --- 1. En-tête Rouge (Top Header) ---
    header_h = 100
    draw.rectangle([0, 0, width, header_h], fill=COLOR_RED)

    draw.text((width//2, 40), "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!", fill=COLOR_WHITE, font=font_header_title, anchor='mm')
    draw.text((40, 75), site_name, fill=COLOR_WHITE, font=font_header_meta, anchor='lm')
    draw.text((width - 40, 75), f"ID : {disparu.public_id}", fill=COLOR_WHITE, font=font_header_meta, anchor='rm')

    # --- 2. Sous-titre Bleu (Sub-Header) ---
    sub_header_y = header_h
    sub_header_h = 120
    draw.rectangle([0, sub_header_y, width, sub_header_y + sub_header_h], fill=COLOR_NAVY)

    draw.text((width//2, sub_header_y + 45), "PERSONNE DISPARUE", fill=COLOR_WHITE, font=font_subheader, anchor='mm')
    draw.text((width//2, sub_header_y + 90), "MISSING PERSON", fill='#CCCCCC', font=font_subheader_small, anchor='mm') 

    # --- 3. Section Photo (REDUITE) ---
    # Réduit de 520 à 480 pour gagner 40px
    photo_size = 480 
    photo_y = sub_header_y + sub_header_h + 30
    photo_x = (width - photo_size) // 2

    border = 2
    draw.rounded_rectangle(
        [photo_x - border, photo_y - border, photo_x + photo_size + border, photo_y + photo_size + border], 
        radius=40, fill='#E5E7EB'
    )

    photo_img = None
    if disparu.photo_url:
        path = disparu.photo_url.replace('/statics/', 'statics/')
        if not os.path.exists(path) and os.path.exists(path.lstrip('/')):
             path = path.lstrip('/')
        if os.path.exists(path):
            try:
                photo_img = Image.open(path).convert('RGBA')
            except:
                pass

    if not photo_img:
        sex = getattr(disparu, 'sex', 'unknown') or 'unknown'
        key = 'placeholder_male' if sex.lower() in ['m', 'male', 'homme', 'masculin'] else 'placeholder_female'
        p_path = settings.get(key, '')
        if p_path:
             full_p = p_path.replace('/statics/', 'statics/')
             if not os.path.exists(full_p) and os.path.exists(full_p.lstrip('/')):
                 full_p = full_p.lstrip('/')
             if os.path.exists(full_p):
                 try:
                    photo_img = Image.open(full_p).convert('RGBA')
                 except:
                    pass

    if photo_img:
        min_dim = min(photo_img.width, photo_img.height)
        left = (photo_img.width - min_dim) // 2
        top = (photo_img.height - min_dim) // 2
        photo_img = photo_img.crop((left, top, left + min_dim, top + min_dim))
        photo_img = photo_img.resize((photo_size, photo_size), Image.Resampling.LANCZOS)

        mask = Image.new("L", (photo_size, photo_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle((0, 0, photo_size, photo_size), radius=40, fill=255)

        img.paste(photo_img, (photo_x, photo_y), mask=mask)
    else:
        draw.rounded_rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], radius=40, fill='#DDDDDD')
        draw.text((width//2, photo_y + photo_size//2), "Photo non disponible", fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    # --- 4. Informations (Compactée) ---
    info_y = photo_y + photo_size + 40

    name = f"{disparu.first_name} {disparu.last_name}"
    draw.text((width//2, info_y), name.upper(), fill=COLOR_BLACK, font=font_name, anchor='mm')

    info_y += 60 # Reduced spacing

    age_str = f"{disparu.age} ANS" if disparu.age else ""
    sex_input = getattr(disparu, 'sex', '') or ''
    sex_str = "HOMME" if sex_input.lower() in ['m', 'male', 'homme'] else "FEMME" if sex_input else ""

    details_line = " - ".join(filter(None, [age_str, sex_str]))
    draw.text((width//2, info_y), details_line, fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    info_y += 50
    loc_str = f"{disparu.city}, {disparu.country}".upper()
    draw.text((width//2, info_y), loc_str, fill=COLOR_TEXT_GRAY, font=font_details, anchor='mm')

    info_y += 60
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
    contact_box_top = info_y + 40
    contact_box_width = int(width * 0.90) 
    contact_box_x = (width - contact_box_width) // 2
    contact_box_height = 200 # Réduit de 220 à 200

    draw.rounded_rectangle([contact_box_x, contact_box_top, contact_box_x + contact_box_width, contact_box_top + contact_box_height], radius=40, fill=COLOR_CONTACT)

    c_y = contact_box_top + 40
    draw.text((width//2, c_y), "CONTACTEZ NOUS SI VOUS AVEZ UNE INFORMATION", fill=COLOR_WHITE, font=font_contact_instr, anchor='mm')

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

    c_y += 50
    draw.text((width//2, c_y), contact_name_str.upper(), fill=COLOR_WHITE, font=font_contact_name, anchor='mm')

    if contact_phone_str:
        c_y += 60
        draw.text((width//2, c_y), contact_phone_str, fill=COLOR_WHITE, font=font_contact_phone, anchor='mm')

    # --- 6. Texte de pied de page (VISIBILITÉ CRITIQUE) ---
    # Placé juste en dessous de la boite de contact
    footer_text_y = contact_box_top + contact_box_height + 30 

    draw.text((width//2, footer_text_y), "TOUTE INFORMATION PEUT PERMETTRE DE RETROUVER CETTE PERSONNE,", fill=COLOR_RED, font=font_footer, anchor='mm')
    draw.text((width//2, footer_text_y + 35), "UN PARTAGE DE CETTE IMAGE PEUT AIDER A LA RECHERCHE AUSSI", fill=COLOR_RED, font=font_footer, anchor='mm')

    # --- 7. Barre URL en bas ---
    bottom_bar_h = 60
    # La barre URL est à 1290 (1350 - 60). Le texte footer est vers 1200-1250, donc ça passe.
    draw.rectangle([0, height - bottom_bar_h, width, height], fill=COLOR_RED)

    url_text = f"{base_url}/disparu/{disparu.public_id}".upper()
    url_display = f"HTTP://{url_text.replace('HTTPS://', '').replace('HTTP://', '')}"

    draw.text((width//2, height - bottom_bar_h/2), url_display, fill=COLOR_WHITE, font=font_url, anchor='mm')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    return buffer