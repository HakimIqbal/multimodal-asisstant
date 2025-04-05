import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from src.ocr import extract_text
from src.vector_db import load_vector_store

# Path model LLM lokal
MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q3_K_M.gguf"

# Inisialisasi LLM (Mistral 7B menggunakan CTransformers)
llm = CTransformers(
    model=MODEL_PATH,
    model_type="mistral",
    config={
        "gpu_layers": 0,  # Set ke 0 karena MacBook M1 Pro pakai CPU
        "context_length": 4096  # Panjang maksimum input model
    }
)

# Inisialisasi model embedding untuk FAISS
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Path FAISS
VECTOR_DB_PATH = "data-rag/embeddings/faiss_index"

# Load FAISS atau buat baru jika tidak ada
try:
    vector_store = load_vector_store(VECTOR_DB_PATH, embedding_model)
except:
    vector_store = FAISS.from_texts([""], embedding_model)  # Inisialisasi FAISS kosong
    vector_store.save_local(VECTOR_DB_PATH)

def process_document(file_path: str):
    """
    Proses dokumen (PDF, DOCX, atau gambar) untuk ekstraksi teks dan penyimpanan ke FAISS.
    """
    text = extract_text(file_path)

    if not text.strip():
        return "Error: Tidak ada teks yang dapat diekstrak dari dokumen."

    # Tambahkan teks hasil OCR ke FAISS
    vector_store.add_texts([text])
    vector_store.save_local(VECTOR_DB_PATH)

    return f"Teks dari dokumen telah ditambahkan ke FAISS: {file_path}"
