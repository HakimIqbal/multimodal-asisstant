/multimodal-assistant/
├── main.py               # Entry point utama (Menjalankan API & UI)
├── models.py             # Modul untuk memuat semua model (Chat, RAG, OCR, dll.)
├── app.py                # UI dengan Streamlit
├── config.py             # Konfigurasi global (path model, API keys, dsb.)
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
├── models/
│   ├── mistral-7b-instruct-v0.1.Q3_K_M.gguf  # Model LLM lokal
│   ├── tesseract/        # Model OCR Tesseract
│   ├── whisper/          # Model Whisper (opsional)
├── src/
│   ├── ocr.py            # Modul OCR (Tesseract)
│   ├── vector_db.py      # Modul FAISS (Vector DB)
│   ├── rag.py            # Modul RAG (Query & Retrieval)
│   ├── chat.py           # Modul Chatbot (LLM)
├── api/
│   ├── server.py         # API menggunakan FastAPI
│   ├── endpoints/        # Folder untuk endpoint API
│   │   ├── chat.py       # Endpoint untuk chat
│   │   ├── rag.py        # Endpoint untuk retrieval
│   │   ├── ocr.py        # Endpoint untuk OCR
├── .env                  # Variabel lingkungan (API keys, path, dll.)