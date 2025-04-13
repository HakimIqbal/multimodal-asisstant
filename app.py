import streamlit as st
import requests
from config import SUPABASE_URL, SUPABASE_KEY 

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multimodal Assistant", layout="wide")
st.title("🤖 Multimodal Assistant")
st.write("Chat, upload dokumen, atau tanyakan sesuatu!")

st.header("💬 Chat")
query = st.text_input("Masukkan pertanyaan:")
if st.button("Tanya"):
    response = requests.post(f"{API_URL}/rag/query/", json={"question": query})
    if response.status_code == 200:
        st.write("**Jawaban:**", response.json()["answer"])
    else:
        st.error(f"Gagal mendapatkan jawaban: {response.status_code} - {response.text}")

st.header("📂 Upload Dokumen")
uploaded_files = st.file_uploader("Pilih file", type=["pdf", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True)
skip_duplicates = st.checkbox("Lewati file duplikat (jika nama sudah ada)")
if st.button("Upload"):
    for uploaded_file in uploaded_files:
        files = [("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))]
        response = requests.post(f"{API_URL}/ocr/upload/", files=files, data={"skip_duplicates": skip_duplicates})
        if response.status_code == 200:
            st.success(f"✅ Berhasil mengupload: {uploaded_file.name}")
            st.write("**System Message:**", response.json()["system_message"])
            for result in response.json()["results"]:
                if "Error" in result["text"]:
                    st.error(f"❌ Gagal memproses {result['filename']}: {result['text']}")
                elif "dilewati karena sudah ada" in result["text"]:
                    st.warning(f"⚠️ {result['text']}")
                elif "Tidak ada teks yang terdeteksi" in result["text"]:
                    st.warning(f"⚠️ Untuk {result['filename']}: Coba unggah file dengan kualitas lebih tinggi atau teks yang lebih jelas.")
                else:
                    st.info(f"📄 File disimpan sebagai: {result['filename']}")
                # Pengecekan kegagalan Supabase
                if SUPABASE_URL and SUPABASE_KEY and any("Gagal menyimpan" in r["text"] for r in response.json()["results"]):
                    st.warning("⚠️ Gagal menyimpan ke cloud, data disimpan secara lokal.")
        else:
            st.error(f"❌ Gagal upload: {uploaded_file.name} - {response.status_code} - {response.text}")