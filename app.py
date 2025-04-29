import streamlit as st
import requests
import os
import tempfile
from models import SUPPORTED_GROQ_MODELS
from gtts import gTTS
import io
import pyttsx3
from src.db import save_ocr_note

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multimodal Assistant", layout="wide")
st.title("🤖 Multimodal Assistant")
st.write("Pilih fitur di bawah untuk berinteraksi dengan asisten!")

if "general_chat_history" not in st.session_state:
    st.session_state["general_chat_history"] = []
if "coder_chat_history" not in st.session_state:
    st.session_state["coder_chat_history"] = []
if "rag_chat_history" not in st.session_state:
    st.session_state["rag_chat_history"] = []
if "ocr_uploaded_file" not in st.session_state:
    st.session_state["ocr_uploaded_file"] = None
if "ocr_extracted_text" not in st.session_state:
    st.session_state["ocr_extracted_text"] = None
if "ocr_filename" not in st.session_state:
    st.session_state["ocr_filename"] = None
if "ocr_temp_path" not in st.session_state:
    st.session_state["ocr_temp_path"] = None
if "navigate_to_chat" not in st.session_state:
    st.session_state["navigate_to_chat"] = False
if "chat_with_ocr_text" not in st.session_state:
    st.session_state["chat_with_ocr_text"] = None

tab1, tab2, tab3, tab4 = st.tabs(["General Chat", "Coder Chat", "RAG System", "OCR"])

with tab1:
    st.header("💬 General Chat")
    st.write("Tanyakan pertanyaan umum (misalnya, definisi atau fakta sederhana). Untuk coding, gunakan Coder Chat.")
    model_general = st.selectbox("Pilih Model (General Chat):", SUPPORTED_GROQ_MODELS, index=0, key="model_general")
    initial_query = st.session_state["chat_with_ocr_text"] if st.session_state["navigate_to_chat"] else ""
    query_general = st.text_input("Masukkan pertanyaan (General):", value=initial_query, key="query_general")
    if st.button("Tanya (General)"):
        response = requests.post(f"{API_URL}/chat/general/", json={"query": query_general, "model_name": model_general})
        if response.status_code == 200:
            st.markdown("**Jawaban:**")
            st.markdown(response.json()["response"])
            st.write(f"**Model Digunakan:** {response.json()['model']}")
            st.session_state["general_chat_history"].append({"user": query_general, "assistant": response.json()["response"]})
        else:
            st.error(f"Gagal mendapatkan jawaban: {response.status_code} - {response.text}")
        st.session_state["navigate_to_chat"] = False
        st.session_state["chat_with_ocr_text"] = None
    
    if st.session_state["general_chat_history"]:
        st.subheader("Riwayat Percakapan")
        for chat in st.session_state["general_chat_history"]:
            st.markdown(f"**User:** {chat['user']}")
            st.markdown(f"**Assistant:** {chat['assistant']}")
            st.markdown("---")

with tab2:
    st.header("💻 Coder Chat")
    st.write("Tanyakan hal terkait coding (misalnya, membuat kode, debugging, atau penjelasan konsep pemrograman)!")
    model_coder = st.selectbox("Pilih Model (Coder Chat):", SUPPORTED_GROQ_MODELS, index=0, key="model_coder")
    query_coder = st.text_input("Masukkan pertanyaan coding:", key="query_coder")
    if st.button("Tanya (Coder)"):
        response = requests.post(f"{API_URL}/coder/coder/", json={"query": query_coder, "model_name": model_coder})
        if response.status_code == 200:
            st.markdown("**Jawaban:**")
            st.markdown(response.json()["response"])
            st.write(f"**Model Digunakan:** {response.json()['model']}")
            st.session_state["coder_chat_history"].append({"user": query_coder, "assistant": response.json()["response"]})
        else:
            st.error(f"Gagal mendapatkan jawaban: {response.status_code} - {response.text}")
    
    if st.session_state["coder_chat_history"]:
        st.subheader("Riwayat Percakapan")
        for chat in st.session_state["coder_chat_history"]:
            st.markdown(f"**User:** {chat['user']}")
            st.markdown(f"**Assistant:** {chat['assistant']}")
            st.markdown("---")

with tab3:
    st.header("📜 RAG System")
    st.write("Unggah dokumen (DOC, DOCX, PDF, maksimal 10MB) dan tanyakan sesuatu berdasarkan dokumen tersebut!")
    
    st.subheader("Upload Dokumen")
    uploaded_files = st.file_uploader("Pilih file dokumen", type=["doc", "docx", "pdf"], accept_multiple_files=True)
    skip_duplicates = st.checkbox("Lewati file duplikat (jika nama sudah ada)")
    if st.button("Upload"):
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.read()
            if len(file_content) > 10 * 1024 * 1024:
                st.error(f"❌ File '{uploaded_file.name}' melebihi batas ukuran 10MB.")
                continue
            files = [("files", (uploaded_file.name, file_content, uploaded_file.type))]
            response = requests.post(f"{API_URL}/rag/upload/", files=files, data={"skip_duplicates": skip_duplicates})
            if response.status_code == 200:
                st.success(f"✅ Berhasil mengupload: {uploaded_file.name}")
                st.write("**System Message:**", response.json()["system_message"])
                for result in response.json()["results"]:
                    if result["status"] == "error":
                        st.error(f"❌ Gagal memproses {result['filename']}: {result['text']}")
                    elif result["status"] == "skipped":
                        st.warning(f"⚠️ {result['text']}")
                    else:
                        st.info(f"📄 File {result['filename']}: {result['text']}")
                        if "preview" in result:
                            st.write(f"**Pratinjau Teks (100 karakter pertama):** {result['preview']}")
            else:
                st.error(f"❌ Gagal upload: {uploaded_file.name} - {response.status_code} - {response.text}")
    
    st.subheader("Tanya Berdasarkan Dokumen")
    model_rag = st.selectbox("Pilih Model (RAG System):", SUPPORTED_GROQ_MODELS, index=0, key="model_rag")
    query_rag = st.text_input("Masukkan pertanyaan (RAG):", key="query_rag")
    if st.button("Tanya (RAG)"):
        response = requests.post(f"{API_URL}/rag/query/", json={
            "question": query_rag,
            "chat_history": st.session_state["rag_chat_history"]
        })
        if response.status_code == 200:
            st.markdown("**Jawaban:**")
            st.markdown(response.json()["answer"])
            st.write(f"**Model Digunakan:** {model_rag}")
            st.session_state["rag_chat_history"] = response.json()["chat_history"]
        else:
            st.error(f"Gagal mendapatkan jawaban: {response.status_code} - {response.text}")
    
    if st.session_state["rag_chat_history"]:
        st.subheader("Riwayat Percakapan")
        for i in range(0, len(st.session_state["rag_chat_history"]), 2):
            user_msg = st.session_state["rag_chat_history"][i]
            assistant_msg = st.session_state["rag_chat_history"][i + 1]
            st.markdown(f"**User:** {user_msg['content']}")
            st.markdown(f"**Assistant:** {assistant_msg['content']}")
            st.markdown("---")

with tab4:
    st.header("🔍 OCR")
    st.write("Unggah file gambar (JPG, JPEG, PNG, HEIC, SVG, maksimal 5MB) untuk mengekstrak teks.")
    
    uploaded_file = st.file_uploader("Pilih file gambar", type=["jpg", "jpeg", "png", "heic", "svg"], accept_multiple_files=False, key="ocr_uploader")
    
    if uploaded_file:
        st.session_state["ocr_uploaded_file"] = uploaded_file
        st.session_state["ocr_filename"] = uploaded_file.name
        file_content = uploaded_file.read()
        if len(file_content) > 5 * 1024 * 1024:
            st.error("❌ File melebihi batas ukuran 5MB.")
            st.session_state["ocr_uploaded_file"] = None
            st.session_state["ocr_filename"] = None
            st.session_state["ocr_temp_path"] = None
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(file_content)
                st.session_state["ocr_temp_path"] = tmp.name
            
            st.image(file_content, caption="Preview Gambar", use_container_width=True)
            
            files = [("file", (uploaded_file.name, file_content, uploaded_file.type))]
            response = requests.post(f"{API_URL}/ocr/extract/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state["ocr_extracted_text"] = result["text"]
                st.markdown("**Hasil:**")
                st.text_area("Teks Hasil Ekstraksi", result["text"], height=200)
            else:
                st.error(f"❌ Gagal mengekstrak teks: {response.status_code} - {response.text}")
                st.session_state["ocr_extracted_text"] = None
    
    if st.session_state["ocr_extracted_text"]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Simpan Catatan"):
                save_ocr_note(st.session_state["ocr_filename"], st.session_state["ocr_extracted_text"])
                st.success("✅ Catatan disimpan ke database.")
        
        with col2:
            if st.button("Scan Ulang"):
                if st.session_state["ocr_temp_path"]:
                    with open(st.session_state["ocr_temp_path"], "rb") as f:
                        file_content = f.read()
                    files = [("file", (st.session_state["ocr_filename"], file_content, st.session_state["ocr_uploaded_file"].type))]
                    response = requests.post(f"{API_URL}/ocr/extract/", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["ocr_extracted_text"] = result["text"]
                        st.markdown("**Hasil (Setelah Scan Ulang):**")
                        st.text_area("Teks Hasil Ekstraksi (Setelah Scan Ulang)", result["text"], height=200)
                    else:
                        st.error(f"❌ Gagal mengekstrak ulang teks: {response.status_code} - {response.text}")
                else:
                    st.error("❌ File sementara tidak ditemukan.")
        
        with col3:
            voice_options = {"Bahasa Inggris": "en", "Bahasa Indonesia": "id"}
            selected_voice = st.selectbox("Pilih Suara:", list(voice_options.keys()), key="voice_select")
            if st.button("Baca"):
                if not st.session_state["ocr_extracted_text"] or st.session_state["ocr_extracted_text"].strip() == "":
                    st.error("❌ Tidak ada teks untuk dibaca.")
                else:
                    st.write(f"System: Teks yang akan dibaca: {st.session_state['ocr_extracted_text'][:100]}...")
                    try:
                        tts = gTTS(text=st.session_state["ocr_extracted_text"], lang=voice_options[selected_voice])
                        audio_file = io.BytesIO()
                        tts.write_to_fp(audio_file)
                        audio_file.seek(0)
                        st.audio(audio_file, format="audio/mp3")
                    except Exception as e:
                        st.error(f"❌ Gagal menghasilkan audio dengan gTTS: {str(e)}")
                        st.write("System: Mencoba menggunakan pyttsx3 (offline)...")
                        try:
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)
                            engine.setProperty('volume', 0.9)
                            voices = engine.getProperty('voices')
                            for voice in voices:
                                if voice_options[selected_voice] == "en" and "en" in voice.id.lower():
                                    engine.setProperty('voice', voice.id)
                                    break
                                elif voice_options[selected_voice] == "id" and "id" in voice.id.lower():
                                    engine.setProperty('voice', voice.id)
                                    break
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                engine.save_to_file(st.session_state["ocr_extracted_text"], tmp.name)
                                engine.runAndWait()
                                tmp_path = tmp.name
                            with open(tmp_path, "rb") as f:
                                audio_file = io.BytesIO(f.read())
                            audio_file.seek(0)
                            st.audio(audio_file, format="audio/mp3")
                            os.unlink(tmp_path)
                        except Exception as e:
                            st.error(f"❌ Gagal menghasilkan audio dengan pyttsx3: {str(e)}")
        
        with col4:
            if st.button("Mengobrol"):
                st.session_state["navigate_to_chat"] = True
                st.session_state["chat_with_ocr_text"] = st.session_state["ocr_extracted_text"]
                st.info("Silakan beralih ke tab General Chat untuk melanjutkan percakapan dengan teks OCR.")
    
    if st.session_state["ocr_uploaded_file"] and st.button("Hapus File"):
        if st.session_state["ocr_temp_path"] and os.path.exists(st.session_state["ocr_temp_path"]):
            os.unlink(st.session_state["ocr_temp_path"])
        st.session_state["ocr_uploaded_file"] = None
        st.session_state["ocr_extracted_text"] = None
        st.session_state["ocr_filename"] = None
        st.session_state["ocr_temp_path"] = None
        st.success("✅ File dihapus.")