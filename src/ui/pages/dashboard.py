import streamlit as st
import requests
import pandas as pd
import os

# Check auth
if "auth_token" not in st.session_state:
    st.switch_page("pages/login.py")

st.set_page_config(page_title="Dashboard", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

# Sidebar logout
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.full_name}")
    st.markdown(f"**Role:** {st.session_state.user_role.upper()}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

st.title("📊 Dashboard")
st.markdown("Welcome to RAG System v1.5")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Team", "API Keys", "Audit Logs"])

with tab1:
    st.subheader("System Overview")

    try:
        response = requests.get(f"{API_URL}/api/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Documents", stats["total_documents"])
            with col2:
                st.metric("Queries Today", stats["queries_today"])
            with col3:
                st.metric("Team Members", stats["team_members"])
            with col4:
                st.metric("Accuracy", f"{stats['accuracy']:.1f}%")
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")

with tab2:
    st.subheader("👥 Team Members")

    try:
        response = requests.get(f"{API_URL}/api/team/members", headers=headers)
        if response.status_code == 200:
            members = response.json()
            df = pd.DataFrame(members)
            st.dataframe(df, use_container_width=True)
        elif response.status_code == 403:
            st.info("Only admins can view team members")
    except Exception as e:
        st.error(f"Error: {str(e)}")

    # Add team member (admin only)
    if st.session_state.user_role == "admin":
        st.divider()
        st.subheader("Add Team Member")

        with st.form("add_member"):
            email = st.text_input("Email")
            role = st.selectbox("Role", ["viewer", "editor", "admin"])
            submitted = st.form_submit_button("Add Member")

            if submitted:
                try:
                    response = requests.post(
                        f"{API_URL}/api/team/members",
                        json={"email": email, "role": role},
                        headers=headers
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Team member added!")
                        st.info(f"Temporary password: `{data['temporary_password']}`")
                    else:
                        st.error(response.json()["detail"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab3:
    st.subheader("🔑 API Keys")

    try:
        response = requests.get(f"{API_URL}/api/api-keys", headers=headers)
        if response.status_code == 200:
            keys = response.json()
            if keys:
                df = pd.DataFrame(keys)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No API keys created yet")
    except Exception as e:
        st.error(f"Error: {str(e)}")

    st.divider()
    st.subheader("Create New API Key")

    with st.form("create_api_key"):
        key_name = st.text_input("Key Name")
        expires_in = st.selectbox(
            "Expires In",
            ["never", "7 days", "30 days", "90 days"]
        )
        submitted = st.form_submit_button("Create Key")

        if submitted:
            try:
                response = requests.post(
                    f"{API_URL}/api/api-keys",
                    json={"name": key_name, "expires_in": expires_in},
                    headers=headers
                )
                if response.status_code == 200:
                    new_key = response.json()
                    st.success("API Key created!")
                    st.code(new_key["key"], language="text")
                    st.warning("⚠️ Save this key somewhere safe. You won't see it again!")
                else:
                    st.error(response.json()["detail"])
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab4:
    st.subheader("📋 Audit Logs")

    if st.session_state.user_role == "admin":
        try:
            response = requests.get(f"{API_URL}/api/audit-logs", headers=headers)
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    df = pd.DataFrame(logs)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No audit logs yet")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("🔒 Only admins can view audit logs")