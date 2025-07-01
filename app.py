import streamlit as st
from web3 import Web3, HTTPProvider
import os
import json
from dotenv import load_dotenv
from ipfs import generate_certificate, generate_certificate_id, upload_to_pinata
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Connect to Ganache with extended timeout
provider = HTTPProvider("http://127.0.0.1:8545", request_kwargs={"timeout": 60})
w3 = Web3(provider)

# Load ABI from build/contracts/CertificateRegistry.json
try:
    with open('build/contracts/CertificateRegistry.json') as f:
        contract_data = json.load(f)
        contract_abi = contract_data['abi']
except FileNotFoundError:
    st.error("Error: build/contracts/CertificateRegistry.json not found. Run 'truffle compile' first.")
    st.stop()

# Get contract address
contract_address = os.getenv("CONTRACT_ADDRESS")
if not contract_address:
    st.error("❌ CONTRACT_ADDRESS not found in .env")
    st.stop()

contract_address = Web3.to_checksum_address(contract_address.strip())
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Streamlit UI
st.title("🎓 Certificate Verification System")

option = st.selectbox("Choose an action", ["Generate Certificate", "Verify Certificate"])

# Optional Sidebar: Show balances
with st.sidebar:
    st.subheader("💰 Ganache Accounts")
    for acc in w3.eth.accounts:
        bal = Web3.from_wei(w3.eth.get_balance(acc), 'ether')
        st.text(f"{acc[:10]}...: {bal:.4f} ETH")

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

        pdf_url = f"/{pdf_path}"
        if os.path.exists(pdf_path):
            st.markdown(
        f'<a href="{pdf_url}" download target="_blank">'
        f'🟢 <button style="padding: 10px 20px; font-size: 16px;">⬇️ Download Certificate PDF</button>'
        f'</a>',
        unsafe_allow_html=True
    )

        # Try blockchain interaction separately
        try:
            sender = w3.eth.accounts[0]
            min_required = Web3.to_wei(0.01, 'ether')
            sender_balance = w3.eth.get_balance(sender)

            # Auto-fund the account if low
            if sender_balance < min_required:
                st.warning("⚠️ Low balance detected. Attempting to auto-fund...")
                funded = False
                for donor in w3.eth.accounts[1:]:
                    donor_balance = w3.eth.get_balance(donor)
                    if donor_balance > Web3.to_wei(1, 'ether'):
                        tx = {
                            'from': donor,
                            'to': sender,
                            'value': Web3.to_wei(10, 'ether'),
                            'gas': 21000,
                            'gasPrice': w3.to_wei('1', 'gwei')
                        }
                        tx_hash = w3.eth.send_transaction(tx)
                        w3.eth.wait_for_transaction_receipt(tx_hash)
                        st.success(f"💸 Auto-funded `{sender}` with 10 ETH from `{donor}`")
                        funded = True
                        break
                if not funded:
                    st.error("❌ No donor account with enough ETH to fund the sender.")
                    st.stop()

            # Now send the blockchain transaction
            tx_hash = contract.functions.issueCertificate(
                cert_id, cid, uid, candidate_name, course_name, org_name
            ).transact({"from": sender})
            st.success("✅ Certificate issued on blockchain")
            st.write(f"📦 Transaction Hash: `{tx_hash.hex()}`")

        except Exception as e:
            st.warning(f"⚠️ Blockchain operation failed or skipped: {e}")
    

# ---------------------------------------------------------------
# VERIFY CERTIFICATE
# ---------------------------------------------------------------
elif option == "Verify Certificate":
    cert_id = st.text_input("Enter Certificate ID").strip()

    if st.button("Verify"):
        st.write("🔍 Verifying Certificate...")
        st.write("✅ Certificate ID:", cert_id)
        st.write("✅ Contract Address:", contract_address)

        if not w3.is_connected():
            st.error("❌ Not connected to blockchain")
            st.stop()

        try:
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

                formatted_date = datetime.fromtimestamp(issued_at, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

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
                st.components.v1.iframe(google_viewer, height=600, width=800)

        except Exception as e:
            import traceback
            st.error("❌ Error verifying certificate")
            st.text(traceback.format_exc())
