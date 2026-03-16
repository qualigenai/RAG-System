import streamlit as st
import requests
import os

# Check auth
if "auth_token" not in st.session_state:
    st.switch_page("pages/login.py")

st.set_page_config(page_title="Settings", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

# Sidebar logout
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.full_name}")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

st.title("⚙️ Settings")

# User Settings
st.subheader("👤 Your Profile")

col1, col2 = st.columns(2)
with col1:
    st.text_input("Full Name", value=st.session_state.full_name, disabled=True)
with col2:
    st.text_input("Email", value=st.session_state.user_email, disabled=True)

st.text_input("Role", value=st.session_state.user_role.upper(), disabled=True)

st.divider()

# About
st.subheader("ℹ️ About RAG System v1.5")
st.markdown("""
**RAG System v1.5** - Enterprise Document Search Platform

**Features:**
- ✅ Multi-user authentication with JWT
- ✅ Role-based access control (Admin, Editor, Viewer)
- ✅ Document upload and indexing
- ✅ Intelligent document search
- ✅ Team management
- ✅ API key authentication
- ✅ Audit logging
- ✅ Enterprise-grade security

**Version:** 1.5.0  
**Status:** Production Ready ✅
""")

st.divider()

st.markdown("""
<div style='text-align: center; color: gray; margin-top: 50px;'>
RAG System v1.5 | Enterprise Document Search | www.ragsystem.io
</div>
""", unsafe_allow_html=True)