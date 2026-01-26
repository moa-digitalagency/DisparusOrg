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

    # Logo
    logo_size = 2.5*cm
    logo_x = 1.5*cm
    logo_y = height - 4*cm

    logo_drawn = False

    # Priorite 1: Favicon configure dans les parametres
    favicon_setting = settings.get('favicon')
    if favicon_setting and not logo_drawn:
        if favicon_setting.startswith('/'):
            favicon_setting = favicon_setting[1:]
        if not favicon_setting.startswith('statics/'):
            favicon_setting = f'statics/{favicon_setting}'
        if os.path.exists(favicon_setting):
            try:
                logo = ImageReader(favicon_setting)
                p.drawImage(logo, logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
                logo_drawn = True
            except Exception:
                pass

    # Priorite 2: Logo texte "DISPARUS.ORG" (cercle D) - jamais site_logo ni favicon par defaut
    if not logo_drawn:
        p.setFillColor(WHITE) 
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0) 
        p.setFillColor(RED_PRIMARY)
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0)
        p.setFillColor(WHITE)
        p.setFont("Helvetica-Bold", 40)
        p.drawCentredString(logo_x + logo_size/2, logo_y + logo_size/2 - 10, "D")

    # Titre du site à droite du logo - toujours "DISPARUS.ORG"
    title_x = logo_x + logo_size + 0.5*cm
    title_y = height - 2.5*cm
    p.setFillColor(RED_DARK) 
    p.setFont("Helvetica-Bold", 28)
    p.drawString(title_x, title_y, "DISPARUS.ORG")

    # Slogan
    p.setFont("Helvetica", 10)
    p.setFillColor(GRAY_MEDIUM)
    p.drawString(title_x, title_y - 0.6*cm, "Plateforme citoyenne pour personnes disparues")
    p.drawString(title_x, title_y - 1.0*cm, "Citizen platform for missing persons")

    # ID à droite
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(BLACK)
    p.drawRightString(width - 1.5*cm, title_y, f"ID: {disparu.public_id}")

    # --- 2. Titre Principal "PERSONNE DISPARUE" ---
    # On remonte tout le bloc de 0.5 cm vers le haut (avant height - 6*cm)
    main_title_y = height - 5.5*cm 

    # Fond rouge léger (10% opacité) derrière tout le bloc
    p.saveState()
    # Création couleur rouge avec alpha 0.1
    bg_color = Color(RED_PRIMARY.red, RED_PRIMARY.green, RED_PRIMARY.blue, alpha=0.1)
    p.setFillColor(bg_color)
    # Rectangle couvrant le titre, sous-titre et les lignes
    # Calcul approximatif pour couvrir la zone
    rect_bottom = main_title_y - 2.2*cm # Juste en dessous de la ligne or
    rect_height = 3.5*cm # Assez haut pour couvrir le texte PERSONNE DISPARUE
    p.rect(0, rect_bottom, width, rect_height, fill=1, stroke=0)
    p.restoreState()

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
    # Remonté de 0.5cm (était 3*cm) pour rapprocher du titre
    content_y = main_title_y - 2.5*cm 

    # Photo décalée de 0.5cm vers la gauche (était 2*cm)
    photo_x = 1.5*cm
    photo_w = 7*cm
    photo_h = 8*cm

    # PAS de cadre rouge autour de la photo (modifié sur demande)

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
    # Infos décalées de 1cm vers la gauche par rapport à l'original (2+7+1 = 10cm).
    # Nouveau calcul : photo_x (1.5) + photo_w (7) + marge (0.5) = 9cm.
    info_x = photo_x + photo_w + 0.5*cm

    # On descend le nom de 0.5 cm supplémentaires vers le bas (était 0.8cm, devient 1.3cm)
    info_y_cursor = content_y - 1.3*cm 

    # Nom
    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica-Bold", 25) # Réduit de 26 à 25 comme demandé
    name = f"{disparu.first_name} {disparu.last_name}"
    p.drawString(info_x, info_y_cursor, name)
    info_y_cursor -= 1.3*cm # Espacement réduit de 1.8 à 1.3 pour faire monter les détails de 0.5cm

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
    label_id = "ID Disparus.org:"
    p.drawString(info_x, info_y_cursor, label_id)

    p.setFillColor(GRAY_DARK)
    p.setFont("Helvetica", 14)
    label_w = p.stringWidth(label_id, "Helvetica-Bold", 14)
    p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, str(disparu.public_id))
    # info_y_cursor -= 1.0*cm # Pas nécessaire pour le dernier élément

    # --- 4. Description & Circonstances ---
    # REMONTÉ de 0.5cm (était -1.5*cm, maintenant -1.0*cm)
    section_y = content_y - photo_h - 1.0*cm

    def draw_section_block(title, content, y_pos):
        # Petit rectangle rouge puce
        p.setFillColor(RED_PRIMARY)
        p.rect(2*cm, y_pos, 0.4*cm, 0.4*cm, fill=1, stroke=0)

        # Titre - COULEUR CHANGÉE en RED_DARK
        p.setFillColor(RED_DARK)
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

    clothing = disparu.clothing or "Non disponible."
    section_y = draw_section_block("VETEMENTS / CLOTHING", clothing, section_y)

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


def generate_qr_code(url, size=10):
    """Generate a QR code for a URL and return as PNG buffer"""
    try:
        import qrcode
        from io import BytesIO

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    except Exception as e:
        import logging
        logging.error(f"Error generating QR code: {e}")
        return None


def generate_social_media_image(disparu, base_url='https://disparus.org'):
    """Generate a 1080x1350px portrait image for social media sharing matching the reference design."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        import os
        import requests

        # Dimensions et Couleurs
        width, height = 1080, 1350

        # Palette basée sur l'image de référence
        RED_HEADER = (153, 27, 27)    # Rouge sombre en haut
        DARK_BAR = (17, 24, 39)       # Bande bleu/noir 'Personne Disparue'
        BG_WHITE = (255, 255, 255)
        RED_ACCENT = (185, 28, 28)    # Rouge vif texte date
        CONTACT_BG = (127, 29, 29)    # Fond rouge bloc contact
        FOOTER_BAR = (88, 28, 28)     # Fond barre URL en bas
        TEXT_BLACK = (0, 0, 0)
        TEXT_GRAY = (80, 80, 80)
        TEXT_WHITE = (255, 255, 255)

        img = Image.new('RGB', (width, height), BG_WHITE)
        draw = ImageDraw.Draw(img)

        # --- Chargement des Polices (Tailles Réduites) ---
        try:
            # Chemins Linux communs
            font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

            font_heavy = ImageFont.truetype(font_path_bold, 48) # Contact Phone
            font_bold_large = ImageFont.truetype(font_path_bold, 36) # Titres principaux
            font_bold_med = ImageFont.truetype(font_path_bold, 28) # Footer text
            font_reg = ImageFont.truetype(font_path_reg, 24) # Textes normaux
            font_small = ImageFont.truetype(font_path_reg, 20) # Petits textes
            font_name = ImageFont.truetype(font_path_bold, 55) # Nom Prénom
        except:
            font_heavy = ImageFont.load_default()
            font_bold_large = font_heavy
            font_bold_med = font_heavy
            font_reg = font_heavy
            font_small = font_heavy
            font_name = font_heavy

        # --- 1. Header Rouge (Top) ---
        header_height = 120 # Reduit de 140
        draw.rectangle([0, 0, width, header_height], fill=RED_HEADER)

        # Texte Header
        header_text = "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!"
        bbox = draw.textbbox((0, 0), header_text, font=font_bold_large)
        draw.text(((width - (bbox[2]-bbox[0])) // 2, 40), header_text, fill=TEXT_WHITE, font=font_bold_large)

        # Sous-textes header (gauche/droite)
        draw.text((30, 85), "DISPARUS.ORG", fill=TEXT_WHITE, font=font_small)
        id_text = f"ID : {disparu.public_id}"
        bbox_id = draw.textbbox((0, 0), id_text, font=font_small)
        draw.text((width - (bbox_id[2]-bbox_id[0]) - 30, 85), id_text, fill=TEXT_WHITE, font=font_small)

        # --- 2. Bande Sombre 'Personne Disparue' ---
        bar_y = header_height
        bar_height = 90 # Reduit de 110
        draw.rectangle([0, bar_y, width, bar_y + bar_height], fill=DARK_BAR)

        main_title = "PERSONNE DISPARUE"
        bbox_mt = draw.textbbox((0, 0), main_title, font=font_bold_large)
        draw.text(((width - (bbox_mt[2]-bbox_mt[0])) // 2, bar_y + 15), main_title, fill=TEXT_WHITE, font=font_bold_large)

        sub_title = "MISSING PERSON"
        bbox_st = draw.textbbox((0, 0), sub_title, font=font_small)
        draw.text(((width - (bbox_st[2]-bbox_st[0])) // 2, bar_y + 60), sub_title, fill=(200, 200, 200), font=font_small)

        # --- 3. Photo Centrale (Arrondie) ---
        photo_area_y = bar_y + bar_height + 40 # Marge reduite
        photo_size = 420 # Reduit de 500
        photo_x = (width - photo_size) // 2

        # Récupération image
        person_photo = None
        if disparu.photo_url:
            try:
                photo_path = disparu.photo_url
                if photo_path.startswith('/'):
                    photo_path = photo_path[1:]

                if os.path.exists(photo_path):
                    person_photo = Image.open(photo_path)
                else:
                    response = requests.get(disparu.photo_url, timeout=5)
                    person_photo = Image.open(BytesIO(response.content))
            except:
                pass

        if person_photo:
            # Redimensionner et couper en carré
            img_w, img_h = person_photo.size
            min_dim = min(img_w, img_h)
            left = (img_w - min_dim) / 2
            top = (img_h - min_dim) / 2
            right = (img_w + min_dim) / 2
            bottom = (img_h + min_dim) / 2
            person_photo = person_photo.crop((left, top, right, bottom))
            person_photo = person_photo.resize((photo_size, photo_size), Image.LANCZOS)

            # Créer masque arrondi
            mask = Image.new('L', (photo_size, photo_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle([(0,0), (photo_size, photo_size)], radius=30, fill=255)

            img.paste(person_photo, (photo_x, photo_area_y), mask)
        else:
            # Placeholder gris
            draw.rounded_rectangle([photo_x, photo_area_y, photo_x+photo_size, photo_area_y+photo_size], radius=30, fill=(230, 230, 230))
            draw.text((photo_x + 100, photo_area_y + 200), "Photo non disponible", fill=TEXT_GRAY, font=font_reg)

        # --- 4. Informations Principales ---
        text_y_cursor = photo_area_y + photo_size + 30 # Marge reduite

        # NOM PRENOM
        name_str = f"{disparu.first_name} {disparu.last_name}".upper()
        # Tronquer si trop long
        if len(name_str) > 30:
            name_str = name_str[:27] + "..."
        bbox_name = draw.textbbox((0, 0), name_str, font=font_name)
        draw.text(((width - (bbox_name[2]-bbox_name[0])) // 2, text_y_cursor), name_str, fill=TEXT_BLACK, font=font_name)
        text_y_cursor += 70 # Espacement reduit

        # Age - Sexe
        age_sex = f"{disparu.age} ans - " + ("Homme" if disparu.sex == 'male' else "Femme")
        bbox_as = draw.textbbox((0, 0), age_sex, font=font_bold_large)
        draw.text(((width - (bbox_as[2]-bbox_as[0])) // 2, text_y_cursor), age_sex, fill=TEXT_GRAY, font=font_bold_large)
        text_y_cursor += 50

        # Ville, Pays
        loc = f"{disparu.city}, {disparu.country}"
        bbox_loc = draw.textbbox((0, 0), loc, font=font_bold_large)
        draw.text(((width - (bbox_loc[2]-bbox_loc[0])) // 2, text_y_cursor), loc, fill=TEXT_GRAY, font=font_bold_large)
        text_y_cursor += 50

        # Date disparition
        date_str = ""
        if disparu.disappearance_date:
            d = disparu.disappearance_date.strftime("%d/%m/%Y")
            h = disparu.disappearance_date.strftime("%H:%M")
            date_str = f"Disparu(e) le {d} a {h}"

        bbox_date = draw.textbbox((0, 0), date_str, font=font_bold_large)
        draw.text(((width - (bbox_date[2]-bbox_date[0])) // 2, text_y_cursor), date_str, fill=RED_ACCENT, font=font_bold_large)
        text_y_cursor += 50

        # --- 5. Description (Ajouté selon demande, entre date et contact) ---
        if disparu.physical_description:
            desc_text = disparu.physical_description
            # Simple wrapping logic
            margin = 80
            max_desc_width = width - (2 * margin)

            # Decoupage simple en lignes
            words = desc_text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox_test = draw.textbbox((0, 0), test_line, font=font_reg)
                if (bbox_test[2] - bbox_test[0]) <= max_desc_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            # Limiter à 3 lignes max
            lines = lines[:3] 

            for line in lines:
                bbox_l = draw.textbbox((0, 0), line, font=font_reg)
                draw.text(((width - (bbox_l[2]-bbox_l[0])) // 2, text_y_cursor), line, fill=TEXT_BLACK, font=font_reg)
                text_y_cursor += 30

            text_y_cursor += 15 # Marge après description

        # --- 6. Bloc Contact ---
        # Fond rouge sombre
        box_margin = 120
        box_height = 160
        box_y = text_y_cursor + 10

        draw.rectangle([box_margin, box_y, width - box_margin, box_y + box_height], fill=CONTACT_BG)

        # Texte titre box
        c_title = "CONTACTEZ NOUS SI VOUS AVEZ UNE INFORMATION"
        bbox_ct = draw.textbbox((0, 0), c_title, font=font_small) # Font plus petite pour etre sur que ca rentre
        draw.text(((width - (bbox_ct[2]-bbox_ct[0])) // 2, box_y + 20), c_title, fill=TEXT_WHITE, font=font_small)

        # Info Contact
        contacts = getattr(disparu, 'contacts', [])
        if contacts:
            c = contacts[0] # Premier contact
            c_name = c.get('name', '').upper()
            c_phone = c.get('phone', '')

            bbox_cn = draw.textbbox((0, 0), c_name, font=font_bold_med)
            draw.text(((width - (bbox_cn[2]-bbox_cn[0])) // 2, box_y + 60), c_name, fill=TEXT_WHITE, font=font_bold_med)

            bbox_cp = draw.textbbox((0, 0), c_phone, font=font_heavy) # Gros pour le tel
            draw.text(((width - (bbox_cp[2]-bbox_cp[0])) // 2, box_y + 100), c_phone, fill=TEXT_WHITE, font=font_heavy)

        # --- 7. Footer Texte Rouge ---
        # Calculer l'espace restant avant le footer du bas
        footer_bar_y = height - 60
        remaining_space = footer_bar_y - (box_y + box_height)

        # On centre le texte d'avertissement dans l'espace restant, s'il y a de la place
        if remaining_space > 60:
            footer_warn_y = (box_y + box_height) + (remaining_space // 2) - 40

            line1 = "Toute information peut permettre de retrouver cette personne,"
            line2 = "un partage de cette image peut aider a la recherche aussi"

            bbox_f1 = draw.textbbox((0, 0), line1, font=font_reg)
            draw.text(((width - (bbox_f1[2]-bbox_f1[0])) // 2, footer_warn_y), line1, fill=RED_ACCENT, font=font_reg)

            bbox_f2 = draw.textbbox((0, 0), line2, font=font_reg)
            draw.text(((width - (bbox_f2[2]-bbox_f2[0])) // 2, footer_warn_y + 35), line2, fill=RED_ACCENT, font=font_reg)

        # --- 8. Barre URL Bas ---
        url_text = f"{base_url}/disparu/{disparu.public_id}".upper()

        draw.rectangle([0, footer_bar_y, width, height], fill=FOOTER_BAR)
        bbox_url = draw.textbbox((0, 0), url_text, font=font_small)
        draw.text(((width - (bbox_url[2]-bbox_url[0])) // 2, footer_bar_y + 15), url_text, fill=TEXT_WHITE, font=font_small)

        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer

    except Exception as e:
        import logging
        logging.error(f"Error generating social media image: {e}")
        return None