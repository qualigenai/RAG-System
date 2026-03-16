import streamlit as st

st.set_page_config(page_title="RAG System", layout="centered")

# Check if logged in
if "auth_token" not in st.session_state or not st.session_state.auth_token:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/dashboard.py")