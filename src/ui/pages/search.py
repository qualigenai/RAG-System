import streamlit as st
import requests
import os

if "auth_token" not in st.session_state:
    st.switch_page("pages/login.py")

st.set_page_config(page_title="Document Search", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.full_name}")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

st.title("🔍 Document Search")

# Upload
with st.expander("📤 Upload Document", expanded=False):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md"])
    if uploaded_file and st.button("Upload"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file)}
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers)
            if response.status_code == 200:
                st.success(f"✅ Uploaded: {response.json()['filename']}")
            else:
                st.error(f"Upload failed")

# Search
st.divider()
st.subheader("💬 Ask Your Documents")

question = st.text_input("Enter your question:")

if question:
    if st.button("🔍 Search"):
        with st.spinner("Searching..."):
            response = requests.post(
                f"{API_URL}/query",
                data={"query_text": question},
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                st.markdown("---")
                st.subheader("📝 Answer")
                st.write(result.get("answer", "No answer"))

                if result.get("sources"):
                    st.subheader("📎 Sources")
                    for s in result["sources"]:
                        st.write(f"• {s}")

                st.success("✅ Done!")
            else:
                st.error(f"Error from API")