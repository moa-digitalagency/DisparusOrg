"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Generation de PDF et images
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from utils.i18n import get_translation


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

# Stats backgrounds
BG_TOTAL_LIGHT = HexColor('#F8FAFC')     # Slate-50
BG_FOUND_LIGHT = HexColor('#F0FDF4')     # Green-50
BG_DECEASED_LIGHT = HexColor('#F3F4F6')  # Gray-100
BG_VIEWS_LIGHT = HexColor('#F5F3FF')     # Violet-50
BG_DOWNLOADS_LIGHT = HexColor('#EFF6FF') # Blue-50
BG_COUNTRIES_LIGHT = HexColor('#FAF5FF') # Purple-50


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


def generate_missing_person_pdf(disparu, base_url='https://disparus.org', t=None, locale='fr'):
    """
    Génère un PDF A4 reproduisant le design original du site (horizontal).
    Robustified to handle missing data and errors gracefully.
    """
    if not HAS_REPORTLAB:
        return None

    # Ensure locale is valid
    if not locale or locale not in ['fr', 'en']:
        locale = 'fr'

    # Use global get_translation if available
    if t is None:
        def t(key, **kwargs):
            text = get_translation(key, locale)
            if kwargs:
                try:
                    return text.format(**kwargs)
                except:
                    return text
            return text

    def bl(key):
        """Bilingual label helper"""
        try:
            fr = get_translation(key, 'fr')
            en = get_translation(key, 'en')
            if fr == en: return fr
            return f"{fr} / {en}"
        except Exception:
            return key

    try:
        settings = get_site_settings()
        site_name = settings.get('site_name', 'DISPARUS.ORG')
    except Exception:
        settings = {}
        site_name = 'DISPARUS.ORG'

    try:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4 # approx 21cm x 29.7cm

        # --- 1. En-tête (Logo + Titre Site) ---
        logo_size = 2.5*cm
        logo_x = 1.5*cm
        logo_y = height - 4*cm
        logo_drawn = False

        favicon_setting = settings.get('favicon')
        if favicon_setting:
            try:
                if favicon_setting.startswith('/'):
                    favicon_setting = favicon_setting[1:]
                if not favicon_setting.startswith('statics/'):
                    favicon_setting = f'statics/{favicon_setting}'
                if os.path.exists(favicon_setting):
                    logo = ImageReader(favicon_setting)
                    p.drawImage(logo, logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
                    logo_drawn = True
            except Exception:
                pass

        if not logo_drawn:
            p.setFillColor(WHITE)
            p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0)
            p.setFillColor(RED_PRIMARY)
            p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2, fill=1, stroke=0)
            p.setFillColor(WHITE)
            p.setFont("Helvetica-Bold", 40)
            p.drawCentredString(logo_x + logo_size/2, logo_y + logo_size/2 - 10, "D")

        title_x = logo_x + logo_size + 0.5*cm
        title_y = height - 2.5*cm
        p.setFillColor(RED_DARK)
        p.setFont("Helvetica-Bold", 28)
        p.drawString(title_x, title_y, "DISPARUS.ORG")

        p.setFont("Helvetica", 10)
        p.setFillColor(GRAY_MEDIUM)
        p.drawString(title_x, title_y - 0.6*cm, t('site.description'))
        p.drawString(title_x, title_y - 1.0*cm, get_translation('site.description', 'en'))

        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(BLACK)
        p.drawRightString(width - 1.5*cm, title_y, f"ID: {disparu.public_id}")

        # --- 2. Titre Principal ---
        main_title_y = height - 5.5*cm

        p.saveState()
        bg_color = Color(RED_PRIMARY.red, RED_PRIMARY.green, RED_PRIMARY.blue, alpha=0.1)
        p.setFillColor(bg_color)
        rect_bottom = main_title_y - 2.2*cm
        rect_height = 3.5*cm
        p.rect(0, rect_bottom, width, rect_height, fill=1, stroke=0)
        p.restoreState()

        p.setFillColor(RED_DARK)
        p.setFont("Helvetica-Bold", 36)
        p.drawCentredString(width/2, main_title_y, t('pdf.missing_person'))

        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width/2, main_title_y - 1*cm, get_translation('pdf.missing_person', 'en').upper())

        p.setStrokeColor(RED_PRIMARY)
        p.setLineWidth(3)
        p.line(3*cm, main_title_y - 1.5*cm, width - 3*cm, main_title_y - 1.5*cm)

        p.setStrokeColor(ACCENT_GOLD)
        p.setLineWidth(1)
        p.line(5*cm, main_title_y - 1.7*cm, width - 5*cm, main_title_y - 1.7*cm)

        # --- 3. Corps ---
        content_y = main_title_y - 2.5*cm
        photo_x = 1.5*cm
        photo_w = 7*cm
        photo_h = 8*cm

        photo_loaded = False
        try:
            if getattr(disparu, 'photo_url', None):
                p_url = str(disparu.photo_url)
                if '/statics/' in p_url:
                    photo_path = p_url.replace('/statics/', 'statics/')
                elif p_url.startswith('statics/'):
                    photo_path = p_url
                else:
                    photo_path = p_url.lstrip('/')

                if os.path.exists(photo_path):
                    photo = ImageReader(photo_path)
                    p.drawImage(photo, photo_x, content_y - photo_h, width=photo_w, height=photo_h, preserveAspectRatio=True, mask='auto')
                    photo_loaded = True
        except Exception:
            pass

        if not photo_loaded:
             draw_rounded_rect(p, photo_x, content_y - photo_h, photo_w, photo_h, 3*mm, fill_color=GRAY_LIGHT)
             p.setFillColor(GRAY_MEDIUM)
             p.setFont("Helvetica", 10)
             p.drawCentredString(photo_x + photo_w/2, content_y - photo_h/2, t('pdf.photo_unavailable'))

        info_x = photo_x + photo_w + 0.5*cm
        info_y_cursor = content_y - 1.3*cm

        # Safe name
        first_name = str(getattr(disparu, 'first_name', '') or '')
        last_name = str(getattr(disparu, 'last_name', '') or '')
        name = f"{first_name} {last_name}".strip() or "Inconnu"

        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(info_x, info_y_cursor, name)
        info_y_cursor -= 1.3*cm

        # Safe date
        date_val = t('common.not_available')
        heure_val = ""
        d_date = getattr(disparu, 'disappearance_date', None)

        # Check if date string is literally "invalid-date" or "invalid"
        if isinstance(d_date, str) and "invalid" in d_date.lower():
             date_val = t('common.invalid_date')
        elif d_date:
            if isinstance(d_date, datetime):
                date_val = d_date.strftime('%d/%m/%Y')
                t_str = d_date.strftime('%H:%M')
                if t_str and t_str != "00:00":
                     heure_val = t_str
            elif isinstance(d_date, str):
                try:
                    dt = datetime.fromisoformat(d_date.replace('Z', '+00:00'))
                    date_val = dt.strftime('%d/%m/%Y')
                    t_str = dt.strftime('%H:%M')
                    if t_str and t_str != "00:00":
                         heure_val = t_str
                except ValueError:
                    date_val = str(d_date)

        # Logic for Animal vs Person details
        is_animal = (getattr(disparu, 'person_type', 'adult') == 'animal')

        sex_fr = t('pdf.gender.female')
        sex_en = get_translation('pdf.gender.female', 'en')

        is_male = False
        sex_val = getattr(disparu, 'sex', None)
        if sex_val:
            s = str(sex_val).lower()
            if s in ['m', 'male', 'homme', '1', 'true']:
                is_male = True

        if is_male:
            sex_fr = t('pdf.gender.male')
            sex_en = get_translation('pdf.gender.male', 'en')

        if is_animal:
            if is_male:
                sex_fr = t('pdf.gender.male_animal')
                sex_en = get_translation('pdf.gender.male_animal', 'en')
            else:
                sex_fr = t('pdf.gender.female_animal')
                sex_en = get_translation('pdf.gender.female_animal', 'en')

        sex_label = f"{sex_fr} / {sex_en}"

        details = []

        age = getattr(disparu, 'age', -1)
        if age is not None and str(age) != '-1':
            details.append((bl('pdf.label.age') + ":", f"{age} {t('detail.age_years')}"))

        details.append((bl('pdf.label.sex') + ":", sex_label))

        city = str(getattr(disparu, 'city', '') or '')
        country = str(getattr(disparu, 'country', '') or '')
        loc_str = f"{city}, {country}".strip(', ')
        details.append((bl('pdf.label.location') + ":", loc_str))

        details.append((bl('pdf.label.date') + ":", date_val))

        for label, value in details:
            p.setFillColor(RED_DARK)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(info_x, info_y_cursor, str(label))

            p.setFillColor(GRAY_DARK)
            p.setFont("Helvetica", 14)
            label_w = p.stringWidth(str(label), "Helvetica-Bold", 14)
            p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, str(value))
            info_y_cursor -= 1.0*cm

        if heure_val:
            time_label = bl('pdf.label.time') + ":"
            p.setFillColor(RED_DARK)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(info_x, info_y_cursor, str(time_label))

            p.setFillColor(GRAY_DARK)
            p.setFont("Helvetica", 14)
            label_w = p.stringWidth(str(time_label), "Helvetica-Bold", 14)
            p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, str(heure_val))
            info_y_cursor -= 1.0*cm

        p.setFillColor(RED_DARK)
        p.setFont("Helvetica-Bold", 14)
        label_id = bl('pdf.label.id') + ":"
        p.drawString(info_x, info_y_cursor, str(label_id))

        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica", 14)
        label_w = p.stringWidth(str(label_id), "Helvetica-Bold", 14)
        p.drawString(info_x + label_w + 0.3*cm, info_y_cursor, str(disparu.public_id))

        # --- 4. Description & Circonstances ---
        section_y = content_y - photo_h - 1.0*cm

        def draw_section_block(title, content, y_pos):
            try:
                p.setFillColor(RED_PRIMARY)
                p.rect(2*cm, y_pos, 0.4*cm, 0.4*cm, fill=1, stroke=0)

                p.setFillColor(RED_DARK)
                p.setFont("Helvetica-Bold", 14)
                p.drawString(2.6*cm, y_pos, str(title))

                p.setStrokeColor(GRAY_LIGHT)
                p.setLineWidth(1)
                p.line(2*cm, y_pos - 0.2*cm, width - 2*cm, y_pos - 0.2*cm)

                text_y = y_pos - 0.8*cm
                p.setFillColor(BLACK)
                p.setFont("Helvetica", 11)

                max_width = width - 4*cm
                words = str(content).split()
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
            except Exception:
                return y_pos - 1.0*cm

        desc = str(getattr(disparu, 'physical_description', '') or t('common.not_available'))
        section_y = draw_section_block(bl('pdf.label.description'), desc, section_y)

        clothing = str(getattr(disparu, 'clothing', '') or t('common.not_available'))
        clothing_label = bl('pdf.label.clothing_animal') if is_animal else bl('pdf.label.clothing')
        section_y = draw_section_block(clothing_label, clothing, section_y)

        if not is_animal:
            circ = str(getattr(disparu, 'circumstances', '') or t('common.not_available'))
            section_y = draw_section_block(bl('pdf.label.circumstances'), circ, section_y)

        # --- 5. Contacts (Bloc dédié) ---
        if section_y < 8*cm:
            pass

        p.setFillColor(RED_PRIMARY)
        p.rect(2*cm, section_y, 0.4*cm, 0.4*cm, fill=1, stroke=0)
        p.setFillColor(GRAY_DARK)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2.6*cm, section_y, bl('pdf.label.contacts'))
        p.setStrokeColor(GRAY_LIGHT)
        p.line(2*cm, section_y - 0.2*cm, width - 6*cm, section_y - 0.2*cm)

        contact_y = section_y - 1.2*cm
        contacts = getattr(disparu, 'contacts', []) or []
        # Handle dict case (invalid json)
        if isinstance(contacts, dict):
            contacts = [contacts]
        elif not isinstance(contacts, list):
            contacts = []

        for contact in contacts[:3]:
            try:
                name = ""
                phone = ""
                if isinstance(contact, dict):
                    name = contact.get('name', '')
                    phone = contact.get('phone', '')
                else:
                    name = getattr(contact, 'name', '')
                    phone = getattr(contact, 'phone', '')

                if name or phone:
                    p.setFillColor(BLACK)
                    p.setFont("Helvetica-Bold", 18)
                    p.drawString(2*cm, contact_y, f"{name}: {phone}")
                    contact_y -= 1.0*cm
            except Exception:
                pass

        # --- 6. Footer (QR Code + Bandes couleur) ---
        qr_size = 3.5*cm
        qr_x = width - 5*cm
        qr_y = 3.5*cm

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
        p.setFont("Helvetica-Bold", 6)
        p.drawCentredString(qr_x + qr_size/2, qr_y, "Scannez pour voir & contribuer")
        p.drawCentredString(qr_x + qr_size/2, qr_y - 0.25*cm, "Scan to view & contribute")

        p.setFillColor(ACCENT_GOLD)
        p.rect(0, 2*cm, width, 0.2*cm, fill=1, stroke=0)

        p.setFillColor(RED_PRIMARY)
        p.rect(0, 0, width, 2*cm, fill=1, stroke=0)

        p.setFillColor(RED_DARK)
        p.rect(0, 0, width, 0.3*cm, fill=1, stroke=0)

        p.setFillColor(WHITE)
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width/2, 1.2*cm, str(base_url))

        p.setFont("Helvetica", 10)
        p.drawCentredString(width/2, 0.6*cm, "Toute information peut être utile / Any information can be useful")

        p.setFillColor(GRAY_MEDIUM)
        p.setFont("Helvetica", 8)
        p.drawString(2*cm, 2.5*cm, f"{t('pdf.footer.generated_on')} {datetime.now().strftime('%d/%m/%Y')} {t('pdf.label.time')} {datetime.now().strftime('%H:%M')}")

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    except Exception as e:
        import logging
        logging.error(f"Critical error generating PDF: {e}")
        return None # Graceful failure


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


async def generate_social_media_image(disparu, base_url='https://disparus.org', t=None, locale='fr'):
    """Generate a 1080x1350px portrait image for social media sharing matching the reference design."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        import os
        import aiohttp
        from urllib.parse import urlparse

        if t is None:
            from utils.i18n import get_translation
            def t(key, **kwargs):
                text = get_translation(key, locale)
                if kwargs:
                    try:
                        return text.format(**kwargs)
                    except:
                        return text
                return text

        # Dimensions
        width, height = 1080, 1350

        # --- Theme Logic based on Status ---
        status = getattr(disparu, 'status', 'missing')
        person_type = getattr(disparu, 'person_type', 'adult')
        is_animal = (person_type == 'animal')

        # Default Theme (Missing)
        theme = {
            'header_color': (153, 27, 27),     # RED_HEADER
            'bar_color': (17, 24, 39),         # DARK_BAR
            'block_bg': (127, 29, 29),         # CONTACT_BG (Red)
            'accent_color': (185, 28, 28),     # RED_ACCENT
            'footer_bar': (88, 28, 28),        # FOOTER_BAR
            'header_text': t('pdf.help_find'),
            'main_title': t('pdf.missing_person'),
            'sub_title': None,
            'block_type': 'contact',
            'header_font_size': 36,
            'footer_lines': [t('pdf.social.footer_line1'), t('pdf.social.footer_line2')]
        }

        # Override for Found / Found Alive (Green)
        if status in ['found', 'found_alive']:
            theme['header_color'] = (4, 120, 87)    # Emerald 700
            theme['bar_color'] = (6, 78, 59)        # Emerald 900
            theme['block_bg'] = (4, 120, 87)        # Emerald 700
            theme['accent_color'] = (4, 120, 87)
            theme['footer_bar'] = (6, 78, 59)

            theme['header_text'] = "MERCI DE TOUT COEUR !"
            theme['header_font_size'] = 36

            noun = "ANIMAL" if is_animal else "PERSONNE"
            # Personne is always feminine in French grammar for agreement here?
            # actually "Personne retrouvée saine et sauve"
            # "Animal retrouvé sain et sauf"

            if is_animal:
                theme['main_title'] = f"{noun} RETROUVÉ"
                theme['sub_title'] = "SAIN ET SAUF"
            else:
                theme['main_title'] = f"{noun} RETROUVÉE"
                theme['sub_title'] = "SAINE ET SAUVE"

            theme['block_type'] = 'date'
            theme['footer_lines'] = [
                "Toutes vos informations et mobilisations ont permis",
                "de retrouver cette personne, nous vous remercions"
            ]

        # Override for Deceased / Found Deceased (Gray)
        elif status in ['deceased', 'found_deceased']:
            theme['header_color'] = (31, 41, 55)    # Gray 800
            theme['bar_color'] = (17, 24, 39)       # Gray 900
            theme['block_bg'] = (55, 65, 81)        # Gray 700
            theme['accent_color'] = (31, 41, 55)
            theme['footer_bar'] = (17, 24, 39)

            theme['header_text'] = "MERCI POUR VOTRE MOBILISATION, MALHEURESEMENT..."
            theme['header_font_size'] = 28

            noun = "ANIMAL" if is_animal else "PERSONNE"
            if is_animal:
                theme['main_title'] = f"{noun} RETROUVÉ"
                theme['sub_title'] = "DÉCÉDÉ"
            else:
                theme['main_title'] = f"{noun} RETROUVÉE"
                theme['sub_title'] = "DÉCÉDÉE"

            theme['block_type'] = 'date'
            theme['footer_lines'] = [
                "Toutes vos informations et mobilisations ont permis",
                "de retrouver cette personne, nous vous remercions"
            ]

        # Override for Injured (Orange - if supported or manually set)
        elif status in ['injured', 'found_injured', 'blesse']:
            theme['header_color'] = (194, 65, 12)   # Orange 700
            theme['bar_color'] = (124, 45, 18)      # Orange 900
            theme['block_bg'] = (194, 65, 12)       # Orange 700
            theme['accent_color'] = (194, 65, 12)
            theme['footer_bar'] = (124, 45, 18)

            theme['header_text'] = "MERCI POUR VOTRE MOBILISATION"
            theme['header_font_size'] = 36

            noun = "ANIMAL" if is_animal else "PERSONNE"
            if is_animal:
                theme['main_title'] = f"{noun} RETROUVÉ"
                theme['sub_title'] = "BLESSÉ"
            else:
                theme['main_title'] = f"{noun} RETROUVÉE"
                theme['sub_title'] = "BLESSÉE"

            theme['block_type'] = 'date'
            theme['footer_lines'] = [
                "Toutes vos informations et mobilisations ont permis",
                "de retrouver cette personne, nous vous remercions"
            ]

        # Common Colors
        BG_WHITE = (255, 255, 255)
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

            font_heavy = ImageFont.truetype(font_path_bold, 48) # Contact Phone / Big Date
            font_bold_large = ImageFont.truetype(font_path_bold, theme.get('header_font_size', 36)) # Titres principaux (variable)
            font_bold_med = ImageFont.truetype(font_path_bold, 28) # Footer text
            font_reg = ImageFont.truetype(font_path_reg, 24) # Textes normaux
            font_small = ImageFont.truetype(font_path_reg, 20) # Petits textes
            font_name = ImageFont.truetype(font_path_bold, 40) # Nom Prénom
        except:
            font_heavy = ImageFont.load_default()
            font_bold_large = font_heavy
            font_bold_med = font_heavy
            font_reg = font_heavy
            font_small = font_heavy
            font_name = font_heavy

        # --- 1. Header (Top) ---
        header_height = 120
        draw.rectangle([0, 0, width, header_height], fill=theme['header_color'])

        # Texte Header
        bbox = draw.textbbox((0, 0), theme['header_text'], font=font_bold_large)
        draw.text(((width - (bbox[2]-bbox[0])) // 2, 40), theme['header_text'], fill=TEXT_WHITE, font=font_bold_large)

        # Sous-textes header (gauche/droite)
        draw.text((30, 85), t('site.name'), fill=TEXT_WHITE, font=font_small)
        id_text = f"{t('admin.id')} : {disparu.public_id}"
        bbox_id = draw.textbbox((0, 0), id_text, font=font_small)
        draw.text((width - (bbox_id[2]-bbox_id[0]) - 30, 85), id_text, fill=TEXT_WHITE, font=font_small)

        # --- 2. Bande Sombre 'Personne Disparue' ---
        bar_y = header_height
        bar_height = 90
        draw.rectangle([0, bar_y, width, bar_y + bar_height], fill=theme['bar_color'])

        main_title = theme['main_title']
        sub_title = theme['sub_title']

        # Determine positions based on if subtitle exists
        if sub_title:
             # Two lines
             bbox_mt = draw.textbbox((0, 0), main_title, font=font_bold_med)
             draw.text(((width - (bbox_mt[2]-bbox_mt[0])) // 2, bar_y + 15), main_title, fill=TEXT_WHITE, font=font_bold_med)

             bbox_st = draw.textbbox((0, 0), sub_title, font=font_bold_med)
             draw.text(((width - (bbox_st[2]-bbox_st[0])) // 2, bar_y + 50), sub_title, fill=TEXT_WHITE, font=font_bold_med)
        else:
             # One line centered
             bbox_mt = draw.textbbox((0, 0), main_title, font=font_bold_large)
             draw.text(((width - (bbox_mt[2]-bbox_mt[0])) // 2, bar_y + 25), main_title, fill=TEXT_WHITE, font=font_bold_large)


        # --- 3. Photo Centrale (Arrondie) ---
        photo_area_y = bar_y + bar_height + 40 # Marge reduite
        photo_size = 420 # Reduit de 500
        photo_x = (width - photo_size) // 2

        # Récupération image
        person_photo = None
        if disparu.photo_url:
            try:
                photo_path = disparu.photo_url
                local_path = None

                # Check if it's a URL or path
                parsed = urlparse(photo_path)
                if parsed.scheme in ('http', 'https'):
                    # Check if it's our own domain or local dev
                    # We can try to extract path if it looks like a static file
                    path = parsed.path
                    if path.startswith('/'):
                        path = path[1:]

                    if os.path.exists(path):
                        local_path = path
                else:
                    # It's a relative path
                    if photo_path.startswith('/'):
                        photo_path = photo_path[1:]
                    if os.path.exists(photo_path):
                        local_path = photo_path

                if local_path:
                    person_photo = Image.open(local_path)
                else:
                    timeout = aiohttp.ClientTimeout(total=5)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(disparu.photo_url) as response:
                            if response.status == 200:
                                content = await response.read()
                                person_photo = Image.open(BytesIO(content))
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
            draw.text((photo_x + 100, photo_area_y + 200), t('pdf.photo_unavailable'), fill=TEXT_GRAY, font=font_reg)

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
        sex_str = t('pdf.gender.male') if disparu.sex == 'male' else t('pdf.gender.female')
        if disparu.person_type == 'animal':
             sex_str = t('pdf.gender.male_animal') if disparu.sex == 'male' else t('pdf.gender.female_animal')

        if disparu.age != -1:
            age_sex = f"{disparu.age} {t('detail.age_years')} - {sex_str}"
        else:
            age_sex = sex_str

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
            date_str = t('pdf.social.missing_since', date=d, time=h)

        bbox_date = draw.textbbox((0, 0), date_str, font=font_bold_large)
        draw.text(((width - (bbox_date[2]-bbox_date[0])) // 2, text_y_cursor), date_str, fill=theme['accent_color'], font=font_bold_large)
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

        # --- 6. Bloc Contact OU Date ---
        box_margin = 120
        box_height = 160
        box_y = text_y_cursor + 10

        draw.rectangle([box_margin, box_y, width - box_margin, box_y + box_height], fill=theme['block_bg'])

        if theme['block_type'] == 'contact':
            # Texte titre box
            c_title = t('pdf.social.contact_title')
            bbox_ct = draw.textbbox((0, 0), c_title, font=font_small)
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

        else: # 'date'
            line1 = "DÉCLARÉ RETROUVÉ LE" # Hardcoded as per request (or approximate)
            # Actually user asked for "Declarer retouver" (sic)
            line1 = "DÉCLARÉ(E) RETROUVÉ(E)"

            # Date (Big)
            # Use updated_at or today
            found_date = getattr(disparu, 'updated_at', datetime.now())
            if not found_date: found_date = datetime.now()
            line2 = found_date.strftime("%d/%m/%Y")

            line3 = "sur la plateforme disparus.org"

            bbox_l1 = draw.textbbox((0, 0), line1, font=font_bold_med)
            draw.text(((width - (bbox_l1[2]-bbox_l1[0])) // 2, box_y + 20), line1, fill=TEXT_WHITE, font=font_bold_med)

            bbox_l2 = draw.textbbox((0, 0), line2, font=font_heavy)
            draw.text(((width - (bbox_l2[2]-bbox_l2[0])) // 2, box_y + 60), line2, fill=TEXT_WHITE, font=font_heavy)

            bbox_l3 = draw.textbbox((0, 0), line3, font=font_small)
            draw.text(((width - (bbox_l3[2]-bbox_l3[0])) // 2, box_y + 120), line3, fill=TEXT_WHITE, font=font_small)


        # --- 7. Footer Texte ---
        # Calculer l'espace restant avant le footer du bas
        footer_bar_y = height - 60
        remaining_space = footer_bar_y - (box_y + box_height)

        # On centre le texte d'avertissement dans l'espace restant, s'il y a de la place
        if remaining_space > 60:
            footer_warn_y = (box_y + box_height) + (remaining_space // 2) - 40

            line1 = theme['footer_lines'][0]
            line2 = theme['footer_lines'][1]

            bbox_f1 = draw.textbbox((0, 0), line1, font=font_reg)
            draw.text(((width - (bbox_f1[2]-bbox_f1[0])) // 2, footer_warn_y), line1, fill=theme['accent_color'], font=font_reg)

            bbox_f2 = draw.textbbox((0, 0), line2, font=font_reg)
            draw.text(((width - (bbox_f2[2]-bbox_f2[0])) // 2, footer_warn_y + 35), line2, fill=theme['accent_color'], font=font_reg)

        # --- 8. Barre URL Bas ---
        url_text = f"{base_url}/disparu/{disparu.public_id}".upper()

        draw.rectangle([0, footer_bar_y, width, height], fill=theme['footer_bar'])
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
def generate_statistics_pdf(stats_data, t, locale='fr', generated_by='System'):
    """
    Génère un rapport PDF complet des statistiques de la plateforme.
    """
    if not HAS_REPORTLAB:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=RED_PRIMARY,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=RED_DARK,
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=5,
        backgroundColor=GRAY_LIGHT
    )

    label_style = ParagraphStyle(
        'MetricLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRAY_MEDIUM
    )

    value_style = ParagraphStyle(
        'MetricValue',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=BLACK,
        alignment=TA_CENTER,
        leading=20
    )

    # Centered style for metadata
    centered_style = ParagraphStyle(
        'Centered',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )

    # --- Header ---
    settings = get_site_settings()
    logo_path = settings.get('favicon')
    if logo_path:
        if logo_path.startswith('/'): logo_path = logo_path[1:]
        if not logo_path.startswith('statics/'): logo_path = f'statics/{logo_path}'
        if os.path.exists(logo_path):
            from reportlab.platypus import Image
            try:
                img = Image(logo_path, width=2*cm, height=2*cm)
                img.hAlign = 'CENTER'
                elements.append(img)
            except Exception:
                pass

    elements.append(Paragraph(f"{t('admin.statistics')} - DISPARUS.ORG", title_style))

    period_text = ""
    filters = stats_data.get('filters', {})
    p = filters.get('period', 'all')
    start = filters.get('start_date', '')
    end = filters.get('end_date', '')
    label = t('stats.period')

    if p == '1d': period_text = f"{label}: {t('stats.last_24h')}"
    elif p == '7d': period_text = f"{label}: {t('stats.last_7d')}"
    elif p == '1m': period_text = f"{label}: {t('stats.last_30d')}"
    elif p == 'custom':
        # Format dates for display
        start_fmt, end_fmt = start, end
        try:
            if start: start_fmt = datetime.strptime(start, '%Y-%m-%d').strftime('%d/%m/%Y')
            if end: end_fmt = datetime.strptime(end, '%Y-%m-%d').strftime('%d/%m/%Y')
        except: pass
        period_text = f"{label}: {t('stats.custom_range', start=start_fmt, end=end_fmt)}"
    else: period_text = f"{label}: {t('stats.all_time')}"

    elements.append(Paragraph(period_text, centered_style))

    # Centered generation info with user name
    gen_text = f"{t('stats.generated_on')}: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if generated_by:
        gen_text = f"{t('stats.generated_by')} {generated_by} - {gen_text}"

    elements.append(Paragraph(gen_text, centered_style))
    elements.append(Spacer(1, 20))

    # --- Section 1: Résumé Global ---
    elements.append(Paragraph(t('admin.dashboard'), section_style))

    stats = stats_data.get('stats', {})

    summary_data = [
        [
            Paragraph(f"<font size=12 color='{RED_PRIMARY}'><b>Total</b></font><br/><br/><font size=22 color='#111827'>{stats.get('total', 0)}</font>", value_style),
            Paragraph(f"<font size=12 color='#059669'><b>{t('stats.found')}</b></font><br/><br/><font size=22 color='#111827'>{stats.get('found', 0)}</font>", value_style),
            Paragraph(f"<font size=12 color='#4B5563'><b>{t('deceased')}</b></font><br/><br/><font size=22 color='#111827'>{stats.get('deceased', 0)}</font>", value_style)
        ],
        [
            Paragraph(f"<font size=12 color='#7C3AED'><b>{t('stats.views')}</b></font><br/><br/><font size=22 color='#111827'>{stats.get('total_views', 0)}</font>", value_style),
            Paragraph(f"<font size=12 color='#2563EB'><b>{t('admin.downloads')}</b></font><br/><br/><font size=22 color='#111827'>{stats.get('total_downloads', 0)}</font>", value_style),
            Paragraph(f"<font size=12 color='#D97706'><b>{t('stats.countries')}</b></font><br/><br/><font size=22 color='#111827'>{stats.get('countries', 0)}</font>", value_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[6*cm, 6*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, RED_PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, GRAY_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        # ('BACKGROUND', (0,0), (-1,-1), white), # Removed global background
        # Specific backgrounds
        ('BACKGROUND', (0,0), (0,0), BG_TOTAL_LIGHT),
        ('BACKGROUND', (1,0), (1,0), BG_FOUND_LIGHT),
        ('BACKGROUND', (2,0), (2,0), BG_DECEASED_LIGHT),
        ('BACKGROUND', (0,1), (0,1), BG_VIEWS_LIGHT),
        ('BACKGROUND', (1,1), (1,1), BG_DOWNLOADS_LIGHT),
        ('BACKGROUND', (2,1), (2,1), BG_COUNTRIES_LIGHT),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # Human/Animal Split
    split_data = [
        [t('admin.type'), t('admin.total'), t('stats.found'), t('deceased'), t('stats.views'), t('admin.downloads')],
        [
            t('stats.humans'),
            str(stats.get('total_persons', 0)),
            str(stats.get('found_persons', 0)),
            str(stats.get('deceased_persons', 0)),
            str(stats.get('views_persons', 0)),
            str(stats.get('downloads_persons', 0))
        ],
        [
            t('stats.animals'),
            str(stats.get('total_animals', 0)),
            str(stats.get('found_animals', 0)),
            str(stats.get('deceased_animals', 0)),
            str(stats.get('views_animals', 0)),
            str(stats.get('downloads_animals', 0))
        ]
    ]
    split_table = Table(split_data, colWidths=[4*cm, 2.8*cm, 2.8*cm, 2.8*cm, 2.8*cm, 2.8*cm])
    split_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RED_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, GRAY_MEDIUM),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(split_table)

    # --- Section 2: Répartition par Statut ---
    elements.append(Paragraph(t('admin.status'), section_style))
    status_data = [[t('admin.status'), t('stats.reports')]]
    for status, count in stats_data.get('by_status', []):
        status_label = t(f'detail.status_{status}')
        status_data.append([status_label, str(count)])

    status_table = Table(status_data, colWidths=[10*cm, 8*cm])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_MEDIUM),
    ]))
    elements.append(status_table)

    # --- Section 3: Top 10 Pays ---
    elements.append(Paragraph(f"Top 10 {t('stats.countries')}", section_style))
    country_data = [[t('report_form.country'), t('stats.reports')]]
    for country, count in stats_data.get('by_country', []):
        country_data.append([country, str(count)])

    country_table = Table(country_data, colWidths=[10*cm, 8*cm])
    country_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RED_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_MEDIUM),
    ]))
    elements.append(country_table)

    # --- Section 4: Détails des fiches (Top Views) ---
    elements.append(Paragraph(t('stats.top_100_views'), section_style))
    files_data = [[t('admin.id'), t('admin.name'), t('admin.type'), t('admin.status'), t('stats.views')]]
    for p in stats_data.get('all_files_stats', [])[:100]:
        p_type = t('sections.animal') if p.person_type == 'animal' else (t(f'stats.{p.person_type}') if p.person_type in ['child', 'teenager', 'adult', 'elderly'] else p.person_type)
        files_data.append([
            p.public_id,
            f"{p.first_name} {p.last_name}",
            p_type,
            t(f'detail.status_{p.status}'),
            str(p.view_count)
        ])

    files_table = Table(files_data, colWidths=[3*cm, 6*cm, 3*cm, 3.5*cm, 2.5*cm])
    files_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), GRAY_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, GRAY_LIGHT])
    ]))
    elements.append(files_table)

    # --- Section 5: Fiches les plus téléchargées ---
    elements.append(Paragraph(t('stats.most_downloaded_records'), section_style))
    dl_data = [[t('common.rank'), t('admin.name'), t('admin.location'), t('admin.downloads')]]
    for i, record in enumerate(stats_data.get('most_downloaded', []), 1):
        dl_data.append([
            str(i),
            f"{record.first_name} {record.last_name}",
            f"{record.city}, {record.country}",
            str(record.download_count)
        ])

    dl_table = Table(dl_data, colWidths=[2*cm, 7*cm, 6*cm, 3*cm])
    dl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#1D4ED8')), # Blue
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_MEDIUM),
    ]))
    elements.append(dl_table)

    # --- Section 6: Formats téléchargés ---
    elements.append(Paragraph(t('stats.downloaded_formats'), section_style))
    format_data = [[t('common.format'), t('admin.downloads')]]
    for f_type, count in stats_data.get('downloads_by_type', []):
        format_data.append([f_type.upper(), str(count)])

    format_table = Table(format_data, colWidths=[10*cm, 8*cm])
    format_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#059669')), # Green
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_MEDIUM),
    ]))
    elements.append(format_table)

    # --- Footer ---
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(GRAY_MEDIUM)
        canvas.drawCentredString(A4[0]/2, 1*cm, f"DISPARUS.ORG - {t('site.description')} - Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer
