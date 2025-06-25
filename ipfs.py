import os
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests

def upload_to_pinata(filepath: str) -> str:
    """Uploads the file to Pinata and returns the CID (IPFS hash)."""
    api_key = os.getenv("PINATA_API_KEY")
    api_secret = os.getenv("PINATA_API_SECRET")

    if not api_key or not api_secret:
        raise EnvironmentError("Pinata API credentials are missing in .env")

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }

    with open(filepath, "rb") as file:
        files = {
            "file": (os.path.basename(filepath), file),
        }
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        cid = response.json()["IpfsHash"]
        print(f"Uploaded to IPFS: {cid}")
        return cid
    else:
        print(f"Failed to upload to IPFS: {response.status_code}, {response.text}")
        raise Exception("IPFS upload failed")


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