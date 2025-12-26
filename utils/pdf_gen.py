import io
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    import qrcode
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_missing_person_pdf(disparu):
    if not HAS_REPORTLAB:
        return None
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 2*cm, "PERSONNE DISPARUE")
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height - 3.5*cm, f"{disparu.first_name} {disparu.last_name}")
    
    p.setFont("Helvetica", 12)
    y = height - 5*cm
    
    details = [
        f"Age: {disparu.age} ans",
        f"Sexe: {disparu.sex}",
        f"Lieu de disparition: {disparu.city}, {disparu.country}",
        f"Date: {disparu.disappearance_date.strftime('%d/%m/%Y') if disparu.disappearance_date else 'N/A'}",
        f"Description: {disparu.physical_description[:200]}..." if len(disparu.physical_description) > 200 else f"Description: {disparu.physical_description}",
    ]
    
    for detail in details:
        p.drawString(2*cm, y, detail)
        y -= 0.7*cm
    
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, 3*cm, f"ID: {disparu.public_id}")
    p.drawCentredString(width/2, 2*cm, "disparus.org")
    
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
