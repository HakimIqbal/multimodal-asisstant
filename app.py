import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multimodal Assistant", layout="wide")
st.title("🤖 Multimodal Assistant")
st.write("Chat, upload dokumen, atau tanyakan sesuatu!")

# Chat Section
st.header("💬 Chat")
query = st.text_input("Masukkan pertanyaan:")
if st.button("Tanya"):
    response = requests.post(f"{API_URL}/rag/query/", json={"question": query})
    if response.status_code == 200:
        st.write("**Jawaban:**", response.json()["answer"])
    else:
        st.error(f"Gagal mendapatkan jawaban: {response.status_code} - {response.text}")

# Upload Section
st.header("📂 Upload Dokumen")
uploaded_files = st.file_uploader("Pilih file", type=["pdf", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True)
if st.button("Upload"):
    for uploaded_file in uploaded_files:
        files = [("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))]
        response = requests.post(f"{API_URL}/ocr/upload/", files=files)
        if response.status_code == 200:
            st.success(f"✅ Berhasil mengupload: {uploaded_file.name}")
            st.write("**System Message:**", response.json()["system_message"])
        else:
            st.error(f"❌ Gagal upload: {uploaded_file.name} - {response.status_code} - {response.text}")