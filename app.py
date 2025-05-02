import streamlit as st
from web3 import Web3
import os
from dotenv import load_dotenv
from ipfs import generate_certificate, generate_certificate_id

# Load environment variables
load_dotenv()

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract_address = os.getenv("CONTRACT_ADDRESS")
contract_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "initialOwner",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "certificateId",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "cid",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "issuer",
                "type": "address"
            }
        ],
        "name": "CertificateIssued",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "certificateId",
                "type": "string"
            }
        ],
        "name": "CertificateRevoked",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "certificateId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "cid",
                "type": "string"
            }
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "certificateId",
                "type": "string"
            }
        ],
        "name": "revokeCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "certificateId",
                "type": "string"
            }
        ],
        "name": "verifyCertificate",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            },
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            },
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "name": "certificates",
        "outputs": [
            {
                "internalType": "string",
                "name": "cid",
                "type": "string"
            },
            {
                "internalType": "address",
                "name": "issuer",
                "type": "address"
            },
            {
                "internalType": "bool",
                "name": "revoked",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Streamlit UI
st.title("Certificate Verification System")

option = st.selectbox("Choose an action", ["Generate Certificate", "Verify Certificate"])

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
            st.error(f"Error generating certificate: {e}")
            pdf_path = None

        if pdf_path and os.path.exists(pdf_path):
            filename = f"{cert_id}.pdf"
            try:
                tx_hash = contract.functions.issueCertificate(cert_id, filename).transact({"from": w3.eth.accounts[0]})
                st.success(f"Certificate generated successfully! Transaction Hash: {tx_hash.hex()}")
                st.write(f"Certificate ID: {cert_id}")
                st.write(f"Local File: {pdf_path}")
            except Exception as e:
                st.error(f"Blockchain transaction failed: {e}")
        else:
            st.error("Failed to generate certificate PDF")

elif option == "Verify Certificate":
    cert_id = st.text_input("Certificate ID")
    if st.button("Verify"):
        try:
            exists, issuer, revoked = contract.functions.verifyCertificate(cert_id).call()
            if exists:
                st.write(f"Issuer: {issuer}")
                st.write(f"Revoked: {revoked}")
                if not revoked:
                    filename = contract.functions.certificates(cert_id).call()[0]
                    full_path = os.path.join("certificates", filename)
                    if os.path.exists(full_path):
                        with open(full_path, "rb") as f:
                            st.download_button("Download Certificate", f.read(), file_name=filename)
                    else:
                        st.error("Certificate file not found locally")
            else:
                st.error("Certificate does not exist")
        except Exception as e:
            st.error(f"Error: {e}")