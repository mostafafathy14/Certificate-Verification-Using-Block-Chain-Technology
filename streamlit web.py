import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(page_title="Blockchain Certificate Verification", layout="wide")

# Load logo
logo = Image.open("Cairo_University.png")

# --- Top Bar with Two Logos and Title ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image(logo, width=70)
with col2:
    st.markdown("<h1 style='text-align: center; color: #1a237e;'>🎓 Certificate Verification System</h1>", unsafe_allow_html=True)
with col3:
    st.image(logo, width=70)

# Initialize navigation state
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Navigation Buttons on Home Page ---
def go_to_page(page_name):
    st.session_state.page = page_name

# Sidebar Navigation
st.sidebar.title("Navigate")
if st.sidebar.button("🏠 Home"):
    go_to_page("Home")
if st.sidebar.button("📝 Issue Certificate"):
    go_to_page("Issue Certificate")
if st.sidebar.button("🔍 Verify Certificate"):
    go_to_page("Verify Certificate")
if st.sidebar.button("🛠 Admin"):
    go_to_page("Admin")

# --- PAGE ROUTING LOGIC ---
if st.session_state.page == "Home":
    # Add some vertical space to push buttons lower
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    
    # Center the buttons horizontally and place them side by side
    col1, col2, col3 = st.columns([1, 2, 1])  # Wider center column for buttons
    with col2:
        # Create two columns within the centered column for side-by-side buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("📝 Issue Certificate", key="issue_btn", use_container_width=True):
                go_to_page("Issue Certificate")
        with btn_col2:
            if st.button("🔍 Verify Certificate", key="verify_btn", use_container_width=True):
                go_to_page("Verify Certificate")

elif st.session_state.page == "Issue Certificate":
    st.header("📝 Issue Certificate")
    name = st.text_input("Recipient Name")
    course = st.text_input("Course Name")
    date = st.date_input("Issue Date")
    issuer = st.text_input("Issuer (University/Organization)")
    submit = st.button("Generate & Upload to Blockchain")
    if submit:
        st.success("Certificate issued and recorded on blockchain.")

elif st.session_state.page == "Verify Certificate":
    st.header("🔍 Verify Certificate")
    cert_id = st.text_input("Enter Certificate ID / Hash")
    if st.button("Verify"):
        # Replace this block with actual verification logic
        st.success("✅ Certificate Verified!")
        st.markdown("**Name:** Jane Doe  \n**Course:** Blockchain 101  \n**Issued by:** XYZ University")

elif st.session_state.page == "Admin":
    st.header("🛠 Admin Dashboard")
    st.markdown("Manage certificate entries and monitor verification logs.")