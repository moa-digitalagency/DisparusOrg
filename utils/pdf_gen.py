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

    # Tentative chargement favicon.png (prioritaire)
    favicon_path = 'statics/img/favicon.png'
    # Gestion du chemin relatif si nécessaire
    if not os.path.exists(favicon_path) and os.path.exists('/' + favicon_path):
        favicon_path = '/' + favicon_path

    if os.path.exists(favicon_path):
        try:
            logo = ImageReader(favicon_path)
            p.drawImage(logo, logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
            logo_drawn = True
        except Exception:
            pass

    # Si favicon non trouvé, on tente le logo du site via settings
    if not logo_drawn:
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

    # Si toujours pas de logo, on met un cercle rouge par défaut
    if not logo_drawn:
        # Cercle rouge avec 'D'
        p.setFillColor(WHITE) 
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0) 
        p.setFillColor(RED_PRIMARY)
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0)
        p.setFillColor(WHITE)
        p.setFont("Helvetica-Bold", 40)
        p.drawCentredString(logo_x + logo_size/2, logo_y + logo_size/2 - 10, "D")

    # Titre du site à droite du logo
    title_x = logo_x + logo_size + 0.5*cm
    title_y = height - 2.5*cm
    p.setFillColor(RED_DARK) 
    p.setFont("Helvetica-Bold", 28)
    p.drawString(title_x, title_y, site_name)

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