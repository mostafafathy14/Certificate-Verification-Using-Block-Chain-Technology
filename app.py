import streamlit as st
from web3 import Web3, HTTPProvider
import os
import json
from dotenv import load_dotenv
from ipfs import generate_certificate, generate_certificate_id, upload_to_pinata

# Load environment variables
load_dotenv()

# Connect to Ganache with extended timeout
provider = HTTPProvider("http://127.0.0.1:8545", request_kwargs={"timeout": 60})
w3 = Web3(provider)
contract_address = os.getenv("CONTRACT_ADDRESS")

# Load ABI from build/contracts/CertificateRegistry.json
try:
    with open('build/contracts/CertificateRegistry.json') as f:
        contract_data = json.load(f)
        contract_abi = contract_data['abi']
except FileNotFoundError:
    st.error("Error: build/contracts/CertificateRegistry.json not found. Run 'truffle compile' first.")
    st.stop()

contract_address = os.getenv("CONTRACT_ADDRESS").strip()
contract_address = Web3.to_checksum_address(contract_address)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Streamlit UI
st.title("🎓 Certificate Verification System")

option = st.selectbox("Choose an action", ["Generate Certificate", "Verify Certificate"])

# ---------------------------------------------------------------
# GENERATE CERTIFICATE
# ---------------------------------------------------------------
if option == "Generate Certificate":
    with st.form("Generate-Certificate"):
        uid = st.text_input("UID")
        candidate_name = st.text_input("Name")
        course_name = st.text_input("Course Name")
        org_name = st.text_input("Organization Name")
        submitted = st.form_submit_button("Submit")

    if submitted:
        cert_id = generate_certificate_id(uid, candidate_name, course_name, org_name)
        os.makedirs("certificates", exist_ok=True)
        pdf_path = f"certificates/{cert_id}.pdf"
        logo_path = "Cairo_University.png"  # Ensure this file exists

        try:
            generate_certificate(pdf_path, uid, candidate_name, course_name, logo_path)
        except Exception as e:
            st.error(f"❌ Error generating certificate: {e}")
            st.stop()

        if not os.path.exists(pdf_path):
            st.error("❌ PDF generation failed.")
            st.stop()

        try:
            cid = upload_to_pinata(pdf_path)
        except Exception as e:
            st.error(f"❌ IPFS upload failed: {e}")
            cid = "Unavailable"

        # ✅ Display output before blockchain
        st.success("📄 Certificate generated successfully!")
        st.write(f"🆔 Certificate ID: `{cert_id}`")
        st.write(f"👤 Candidate: `{candidate_name}`")
        st.write(f"📚 Course: `{course_name}`")
        st.write(f"🏢 Organization: `{org_name}`")
        st.write(f"🔖 UID: `{uid}`")
        st.write(f"🧾 IPFS CID: `{cid}`")
        if cid != "Unavailable":
            st.markdown(f"🔗 [View on IPFS](https://gateway.pinata.cloud/ipfs/{cid})")

        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Download Certificate PDF", f, file_name=f"{cert_id}.pdf")

        # Try blockchain interaction separately
        try:
            tx_hash = contract.functions.issueCertificate(
                cert_id, cid, uid, candidate_name, course_name, org_name
            ).transact({"from": w3.eth.accounts[0]})
            st.success("✅ Certificate issued on blockchain")
            st.write(f"📦 Transaction Hash: `{tx_hash.hex()}`")
        except Exception as e:
            st.warning(f"⚠️ Blockchain operation failed or skipped: {e}")
# ---------------------------------------------------------------
# VERIFY CERTIFICATE
# ---------------------------------------------------------------
elif option == "Verify Certificate":
    cert_id = st.text_input("Enter Certificate ID").strip()  # Remove spaces

    if st.button("Verify"):
        # Show some debug info to confirm values
        st.write("🔍 Verifying Certificate...")
        st.write("✅ Certificate ID:", cert_id)
        st.write("✅ Contract Address:", contract_address)

        # Make sure connected to blockchain
        if not w3.is_connected():
            st.error("❌ Not connected to blockchain")
            st.stop()

        try:
            # Optional: force the call to use account[0] for context
            result = contract.functions.verifyCertificate(cert_id).call({'from': w3.eth.accounts[0]})
            exists = result[0]


            if not exists:
                st.error("❌ Certificate does not exist")
            else:
                uid = result[1]
                name = result[2]
                course = result[3]
                org = result[4]
                cid = result[5]
                issuer = result[6]
                revoked = result[7]
                issued_at = result[8]

                from datetime import datetime
                formatted_date = datetime.utcfromtimestamp(issued_at).strftime('%Y-%m-%d %H:%M:%S')

                st.success("✅ Certificate found!")
                st.write(f"👤 Name: `{name}`")
                st.write(f"🆔 UID: `{uid}`")
                st.write(f"📚 Course: `{course}`")
                st.write(f"🏢 Organization: `{org}`")
                st.write(f"📅 Issued At: `{formatted_date}`")
                st.write(f"👮 Issuer: `{issuer}`")
                st.write(f"❌ Revoked: `{revoked}`")
                st.write(f"🧾 IPFS CID: `{cid}`")

                ipfs_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
                st.markdown(f"[Download Certificate from IPFS]({ipfs_url})")
                google_viewer = f"https://docs.google.com/gview?embedded=true&url={ipfs_url}"

                # Embed the certificate in the browser
                st.components.v1.iframe(google_viewer, height=600, width=800)
                st.components.v1.iframe(ipfs_url, height=600)

        except Exception as e:
            import traceback
            st.error("❌ Error verifying certificate")
            st.text(traceback.format_exc())
