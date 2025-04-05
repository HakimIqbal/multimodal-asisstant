import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(page_title="Chatbot RAG + OCR", layout="wide")

st.title("🤖 Chatbot RAG + OCR")
st.write("Masukkan pertanyaan atau upload dokumen untuk ditambahkan ke knowledge base.")

# **Chatbot Section**
st.header("💬 Chat dengan AI")
query = st.text_input("Masukkan pertanyaan:")

if st.button("Tanya Chatbot"):
    response = requests.post(f"{API_URL}/ask/", json={"query": query})
    
    if response.status_code == 200:
        st.write("**Jawaban:**")
        st.write(response.json()["answer"])
    else:
        st.error("Gagal mendapatkan jawaban dari chatbot.")

# **Upload Dokumen Section**
st.header("📂 Upload Dokumen")
uploaded_files = st.file_uploader("Pilih file PDF, DOCX, atau Gambar", 
                                  type=["pdf", "docx", "png", "jpg"], 
                                  accept_multiple_files=True)

if st.button("Upload"):
    for uploaded_file in uploaded_files:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(f"{API_URL}/upload-document/", files=files)

        if response.status_code == 200:
            st.success(f"✅ Berhasil mengupload: {uploaded_file.name}")
        else:
            st.error(f"❌ Gagal upload: {uploaded_file.name}")

