import os
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_certificate(output_path: str, uid: str, candidate_name: str, course_name: str, logo_path: str) -> None:
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    university_name = "Cairo University"

    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=150, height=150)
        elements.append(logo)

    institute_style = ParagraphStyle(
        "InstituteStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=1,
        spaceAfter=30,
    )
    institute = Paragraph(university_name, institute_style)
    elements.extend([institute, Spacer(1, 12)])

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        alignment=1,
        spaceAfter=20,
    )
    title = Paragraph("Certificate of Completion", title_style)
    elements.extend([title, Spacer(1, 6)])

    recipient_style = ParagraphStyle(
        "RecipientStyle",
        parent=getSampleStyleSheet()["BodyText"],
        fontSize=14,
        leading=18,
        alignment=1,
        spaceAfter=12,
    )
    recipient_text = (
        "This is to certify that<br/><br/>"
        f"<b><font color='red'>{candidate_name}</font></b><br/>"
        "bearing the Unique Identification Number (UID):<br/>"
        f"<b><font color='red'>{uid}</font></b><br/><br/>"
        "has successfully completed the course<br/>"
        f"<b><font color='blue'>{course_name}</font></b>."
    )
    recipient = Paragraph(recipient_text, recipient_style)
    elements.append(recipient)

    doc.build(elements)

    print(f"Certificate generated and saved at: {output_path}")

def generate_certificate_id(uid: str, name: str, course: str, org: str) -> str:
    data = f"{uid}{name}{course}{org}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()