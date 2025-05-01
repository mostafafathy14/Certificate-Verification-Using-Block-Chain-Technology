import os
import hashlib
import requests
import streamlit as st
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from connection import contract, w3

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

# Helper functions
def generate_certificate(output_path: str, uid: str, candidate_name: str, course_name: str, logo_path: str) -> None:
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    university_name = "Cairo University"

    if logo_path:
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
        f"<strong><span style='color:red'>{candidate_name}</span></strong><br/>"
        "bearing the Unique Identification Number (UID):<br/>"
        f"<strong><span style='color:red'>{uid}</span></strong><br/><br/>"
        "has successfully completed the course<br/>"
        f"<strong><span style='color:blue'>{course_name}</span></strong>."
    )
    recipient = Paragraph(recipient_text, recipient_style)
    elements.append(recipient)

    doc.build(elements)

    print(f"Certificate generated and saved at: {output_path}")

def upload_to_pinata(file_path: str, api_key: str, api_secret: str) -> str | None:
    """Uploads a file to Pinata IPFS and returns its hash."""
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }

    try:
        with open(file_path, "rb") as file:
            files = {"file": (file.name, file)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()

        result = response.json()
        ipfs_hash = result.get("IpfsHash")
        if not ipfs_hash:
            st.error("Failed to get IPFS hash from Pinata response.")
        return ipfs_hash

    except Exception as e:
        st.error(f"Error uploading to Pinata: {e}")
        return None

def generate_certificate_id(uid: str, name: str, course: str, org: str) -> str:
    data = f"{uid}{name}{course}{org}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def view_certificate(certificate_id: str):
    cert = contract.functions.getCertificate(certificate_id).call()
    ipfs_hash = cert[4]

    pinata_gateway_base_url = "http://localhost:8080/ipfs/"
    content_url = f"{pinata_gateway_base_url}/{ipfs_hash}"
    
    response = requests.get(content_url)
    if response.status_code == 200:
        with open("certificate.pdf", "wb") as f:
            f.write(response.content)
        st.success("Certificate retrieved successfully.")
        st.download_button("Download Certificate", data=response.content, file_name="certificate.pdf")
    else:
        st.error("Failed to retrieve certificate.")

# UI Logic
OPTIONS = ("Generate Certificate", "View Certificates")
selected_option = st.selectbox("", OPTIONS, label_visibility="hidden")

if selected_option == "Generate Certificate":
    with st.form("Generate-Certificate"):
        uid = st.text_input("UID")
        candidate_name = st.text_input("Name")
        course_name = st.text_input("Course Name")
        org_name = st.text_input("Organization Name")
        submitted = st.form_submit_button("Submit")

    if submitted:
        pdf_path = "certificate.pdf"
        logo_path = "Cairo_University.png"

        generate_certificate(pdf_path, uid, candidate_name, course_name, org_name, logo_path)

        ipfs_hash = upload_to_pinata(pdf_path, PINATA_API_KEY, PINATA_API_SECRET)
        os.remove(pdf_path)

        if ipfs_hash:
            cert_id = generate_certificate_id(uid, candidate_name, course_name, org_name)
            try:
                contract.functions.generateCertificate(
                    cert_id, uid, candidate_name, course_name, org_name, ipfs_hash
                ).transact({'from': w3.eth.accounts[0]})

                st.success(f"Certificate generated successfully!\n\nCertificate ID: `{cert_id}`")

            except Exception as e:
                st.error(f"Blockchain transaction failed: {e}")
        else:
            st.error("Certificate upload failed. Please try again.")

elif selected_option == "View Certificates":
    with st.form("View-Certificate"):
        cert_id = st.text_input("Enter Certificate ID")
        submitted = st.form_submit_button("Submit")

    if submitted:
        try:
            view_certificate(cert_id)
        except Exception as e:
            st.error(f"Error viewing certificate: {e}")
