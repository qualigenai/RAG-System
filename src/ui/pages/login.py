import streamlit as st
import requests
import os

st.set_page_config(page_title="RAG System - Login", layout="centered")

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Check if already logged in
if "auth_token" in st.session_state and st.session_state.auth_token:
    st.switch_page("pages/dashboard.py")

# Simple layout
st.title("🔐 RAG System")
st.markdown("### Enterprise Document Search Platform")
st.divider()

# Tabs
tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("Login to Your Account")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if not email or not password:
            st.error("Please enter email and password")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.auth_token = data["access_token"]
                    st.session_state.user_email = email

                    headers = {"Authorization": f"Bearer {data['access_token']}"}
                    user_response = requests.get(
                        f"{API_URL}/api/auth/me",
                        headers=headers
                    )

                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        st.session_state.user_role = user_data["role"]
                        st.session_state.full_name = user_data["full_name"]

                    st.success("Login successful!")
                    st.switch_page("pages/dashboard.py")

                else:
                    st.error("Invalid credentials")

            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Create New Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address", key="register_email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account", use_container_width=True):
        if not all([full_name, email, username, password, confirm_password]):
            st.error("Please fill in all fields")
        elif password != confirm_password:
            st.error("Passwords don't match")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/register",
                    json={
                        "full_name": full_name,
                        "email": email,
                        "username": username,
                        "password": password
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        st.success("✅ Account created! Please login.")
                    except:
                        st.success("✅ Account created! Please login.")

                elif response.status_code == 400:
                    try:
                        error_msg = response.json().get("detail", "Registration failed")
                    except:
                        error_msg = "Email or username already exists"
                    st.error(f"❌ {error_msg}")
                else:
                    st.error(f"❌ Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Is FastAPI running on port 8000?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")