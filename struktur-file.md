/multimodal-assistant/
├── main.py               # Entry point utama (Menjalankan API & UI)
├── models.py             # Modul untuk inisialisasi model dan koneksi ke Groq
├── app.py                # UI dengan Streamlit
├── config.py             # Konfigurasi global (path, API keys dari .env)
├── requirements.txt      # Dependencies
├── data-rag/
│   ├── documents/        # Folder untuk menyimpan dokumen mentah
│   │   ├── contoh-docs/  # Sub-folder untuk dokumen teks
│   │   ├── contoh-gambar/ # Sub-folder untuk gambar
│   │   │   ├── contoh_gambar.png
│   │   ├── contoh-pdf/   # Sub-folder untuk PDF
│   │   │   ├── contoh_dokumen.pdf
│   ├── embeddings/       # Folder untuk menyimpan vektor embedding
│   ├── faiss_index/      # Folder penyimpanan FAISS Index
├── src/
│   ├── ocr.py            # Modul OCR (Tesseract)
│   ├── vector_db.py      # Modul FAISS (Vector DB)
│   ├── rag.py            # Modul RAG (Query & Retrieval)
│   ├── chat.py           # Modul Chatbot (Groq API)
├── api/
│   ├── server.py         # API menggunakan FastAPI
│   ├── endpoints/        # Folder untuk endpoint API
│   │   ├── chat.py       # Endpoint untuk chat
│   │   ├── rag.py        # Endpoint untuk retrieval
│   │   ├── ocr.py        # Endpoint untuk OCR
├── .env                  # Variabel lingkungan (API keys, path, dll.)