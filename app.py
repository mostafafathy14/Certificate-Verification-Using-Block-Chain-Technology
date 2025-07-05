import streamlit as st
from web3 import Web3, HTTPProvider
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from ipfs import generate_certificate, generate_certificate_id, upload_to_pinata
import base64


def back_to_home_button():
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# Load environment variables
load_dotenv()

# Web3 setup
provider = HTTPProvider("http://127.0.0.1:8545", request_kwargs={"timeout": 60})
w3 = Web3(provider)

# Load ABI
try:
    with open('build/contracts/CertificateRegistry.json') as f:
        contract_data = json.load(f)
        contract_abi = contract_data['abi']
except FileNotFoundError:
    st.error("Missing ABI JSON. Run `truffle compile` first.")
    st.stop()

# Load Contract Address
contract_address = os.getenv("CONTRACT_ADDRESS")
if not contract_address:
    st.error("Missing CONTRACT_ADDRESS in .env")
    st.stop()

contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)

# --- Styling ---
st.markdown("""
    <style>
    .home-title {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        color: #104e3e;
        margin-top: 40px;
    }
    .icon-label {
        font-size: 1.2rem;
        font-weight: 600;
        color: #104e3e;
        margin-top: 10px;
    }
    .clickable-icon {
        text-align: center;
        cursor: pointer;
    }
    .clickable-icon img {
        width: 130px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# --- Home Page ---
def show_home():
    st.markdown("""
    <style>
    .home-title {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        color: #104e3e;
        margin-top: 40px;
        margin-bottom: 40px;
    }
    .stButton > button {
        width: 70%;
        margin: 0 auto;
        display: block;
        background-color: #2D6A4F;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button:hover {
        background-color: #1B4332;
    }
    </style>
""", unsafe_allow_html=True)

    st.markdown('<div class="home-title">🎓 Certificate Verification System</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    admin_image_path = "images/admin.png"
    verifier_image_path = "images/verifier.png"

    with col1:
        if os.path.exists(admin_image_path):
            admin_img_base64 = base64.b64encode(open(admin_image_path, "rb").read()).decode()
            st.markdown(f"""
                <div style="text-align:center">
                    <img src="data:image/png;base64,{admin_img_base64}" width="130" />
                    <div style="margin-top: 10px;"></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Admin image not found.")

        # ✅ Button directly under image
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if st.button("Login as Admin", key="admin_btn"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if os.path.exists(verifier_image_path):
            verifier_img_base64 = base64.b64encode(open(verifier_image_path, "rb").read()).decode()
            st.markdown(f"""
                <div style="text-align:center">
                    <img src="data:image/png;base64,{verifier_img_base64}" width="130" />
                    <div style="margin-top: 10px;"></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Verifier image not found.")

        # ✅ Button directly under image
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if st.button("Continue as Verifier", key="verifier_btn"):
            st.session_state.page = "guest_verify"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)



# --- Login ---
def show_login():
    st.set_page_config(page_title="Admin Login", layout="centered")

    # Custom CSS with modern styling
    st.markdown("""
        <style>
        .login-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.8rem;
            font-family: 'Segoe UI', 'Poppins', sans-serif;
            letter-spacing: 1px;
            color: #2D6A4F;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
        }

        .stButton button {
            display: block;
            margin: 1.5em auto 0 auto;
            width: 90%;
            max-width: 150px;
            background-color: #2D6A4F;
            color: #fff;
            font-weight: 700;
            border-radius: 6px;
            padding: 0.1em;
            border: none;
            overflow: hidden;
            text-align: center;
            transition: background-color 0.2s ease;
        }

        .stButton button:hover {
            background-color: #1B4332;
        }

        .username span, .password span {
            display: block;
            text-align: center;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.1em;
            font-size: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">🔐 <span>Admin Login</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="username"><span>Username</span></div>', unsafe_allow_html=True)
    username = st.text_input("", key="login_username")
    
    st.markdown('<div class="password"><span>Password</span></div>', unsafe_allow_html=True)
    password = st.text_input("", type="password", key="login_password")

    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD")

    if st.button("Login"):
        if username == admin_user and password == admin_pass:
            st.session_state.admin_logged_in = True
            st.session_state.page = "admin_dashboard"
            st.success("✅ Login successful")
            st.rerun()
        elif username or password:
            st.error("❌ Invalid credentials")
    
    back_to_home_button()

# --- Admin Dashboard ---
def show_admin_dashboard():
    st.markdown("""
        <style>
        .admin-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            color: #104e3e;
            margin-bottom: 40px;
        }
        .stButton>button {
            background-color: #104e3e;
            color: white;
            padding: 12px 28px;
            font-size: 16px;
            border-radius: 10px;
            margin: 10px auto;
            display: block;
        }
        .stButton>button:hover {
            background-color: #0b3c2e;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="admin-title">👨‍💼 Admin Panel</div>', unsafe_allow_html=True)

    if st.button("🧾 Generate Certificate"):
        st.session_state.page = "admin_generate"
        st.rerun()

    if st.button("🔍 Verify Certificate"):
        st.session_state.page = "admin_verify"
        st.rerun()

    back_to_home_button()

# --- Generate Certificate UI ---
def generate_certificate_ui():
    st.title("🧾 Generate Certificate")

    with st.form("Generate"):
        uid = st.text_input("UID")
        name = st.text_input("Candidate Name")
        course = st.text_input("Course Name")
        org = st.text_input("Organization Name")
        submitted = st.form_submit_button("Generate")

    if submitted:
        os.makedirs("certificates", exist_ok=True)
        temp_pdf_path = "certificates/temp.pdf"
        logo_path = "images/Cairo_University.png"

        try:
            generate_certificate(temp_pdf_path, uid, name, course, logo_path)
            cert_id = generate_certificate_id(temp_pdf_path)
            final_pdf_path = f"certificates/{cert_id}.pdf"
            os.rename(temp_pdf_path, final_pdf_path)
            cid = upload_to_pinata(final_pdf_path)

            st.success("✅ Certificate generated!")
            
            dark_green = "#104e3e"
            st.markdown(f"<b>🆔 ID:</b> <span style='color:{dark_green}'>{cert_id}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>👤 Name:</b> <span style='color:{dark_green}'>{name}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>📚 Course:</b> <span style='color:{dark_green}'>{course}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>🏢 Organization:</b> <span style='color:{dark_green}'>{org}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>🔗 IPFS:</b> <span style='color:{dark_green}'>{cid}</span>", unsafe_allow_html=True)


            if cid != "Unavailable":
                st.markdown(f"[🔗 View on IPFS](https://gateway.pinata.cloud/ipfs/{cid})")

            sender = w3.eth.accounts[0]
            tx_hash = contract.functions.issueCertificate(
                cert_id, cid, uid, name, course, org
            ).transact({"from": sender})
            st.success("📦 Issued on Blockchain!")
            

        except Exception as e:
            st.error(f"❌ Error: {e}")
    back_to_home_button()

# --- Verify Certificate UI ---
def verify_certificate_ui():
    st.markdown("""
        <style>
        .verifier-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            color: #104e3e;
            margin-bottom: 40px;
        }
        .stButton>button {
            background-color: #104e3e;
            color: white;
            padding: 12px 28px;
            font-size: 16px;
            border-radius: 10px;
            margin: 10px auto;
            display: block;
        }
        .stButton>button:hover {
            background-color: #0b3c2e;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="verifier-title">🔍 Verifier Panel</div>', unsafe_allow_html=True)

    if "verify_method" not in st.session_state:
        st.session_state.verify_method = None

    if not st.session_state.verify_method:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Upload Certificate"):
                st.session_state.verify_method = "upload"
                st.rerun()
        with col2:
            if st.button("🔢 Enter Certificate ID"):
                st.session_state.verify_method = "id"
                st.rerun()

    elif st.session_state.verify_method == "upload":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            if st.button("✅ Verify"):
                try:
                    temp_path = os.path.join("temp", uploaded_file.name)
                    os.makedirs("temp", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.read())
                    cert_id = generate_certificate_id(temp_path)
                    verify_on_chain(cert_id)
                except Exception as e:
                    st.error(f"Error verifying certificate: {e}")
        if st.button("🔁 Change Method"):
            st.session_state.verify_method = None
            st.rerun()

    elif st.session_state.verify_method == "id":
        cert_id = st.text_input("Enter Certificate ID")
        if st.button("✅ Verify") and cert_id:
            try:
                verify_on_chain(cert_id.strip())
            except Exception as e:
                st.error(f"Error verifying certificate: {e}")
        if st.button("🔁 Change Method"):
            st.session_state.verify_method = None
            st.rerun()

    back_to_home_button()


# --- On-chain Verification Helper ---
def verify_on_chain(cert_id): 
    try: 
        cert = contract.functions.verifyCertificate(cert_id).call() 
        exists = cert[0] 
        if not exists: 
            st.error("❌ Certificate does not exist") 
        else: 
            st.success("✅ Certificate found!") 

            dark_green = "#104e3e"
            st.markdown(f"<b>🆔 Certificate ID:</b> <span style='color:{dark_green}'>{cert_id}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>👤 Name:</b> <span style='color:{dark_green}'>{cert[2]}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>📚 Course:</b> <span style='color:{dark_green}'>{cert[3]}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>🏢 Organization:</b> <span style='color:{dark_green}'>{cert[4]}</span>", unsafe_allow_html=True)
            st.markdown(f"<b>🔗 IPFS CID:</b> <span style='color:{dark_green}'>{cert[5]}</span>", unsafe_allow_html=True)

            # Optional: direct link to certificate
            st.markdown(f"[🔗 View on IPFS](https://gateway.pinata.cloud/ipfs/{cert[5]})", unsafe_allow_html=True)
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{cert[5]}"
            st.markdown(f"[Download Certificate from IPFS]({ipfs_url})")
            google_viewer = f"https://docs.google.com/gview?embedded=true&url={ipfs_url}"
            st.components.v1.iframe(google_viewer, height=600, width=800)
            
    except Exception as e: 
        st.error(f"❌ Blockchain error: {e}")
    

# --- Routing ---
if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "login":
    show_login()
elif st.session_state.page == "admin_dashboard":
    if st.session_state.admin_logged_in:
        show_admin_dashboard()
    else:
        st.session_state.page = "login"
        st.rerun()
elif st.session_state.page == "admin_generate":
    if st.session_state.admin_logged_in:
        generate_certificate_ui()
    else:
        st.session_state.page = "login"
        st.rerun()
elif st.session_state.page == "admin_verify": 
    if st.session_state.admin_logged_in: 
        verify_certificate_ui()
    else:
        st.session_state.page = "login"
        st.rerun()
elif st.session_state.page == "guest_verify":
    verify_certificate_ui()
