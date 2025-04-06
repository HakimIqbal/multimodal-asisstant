import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from src.vector_db import load_vector_store, process_and_store_text
from config import GROQ_API_KEY, VECTOR_DB_PATH, DOCUMENTS_PATH, SUBFOLDERS
from src.ocr import extract_text

# Inisialisasi model embedding untuk FAISS
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Inisialisasi LLM dari Groq
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-70b-8192",
    temperature=0.7,
    max_tokens=4096
)

# Fungsi untuk menginisialisasi atau memuat vector store
def initialize_vector_store():
    # Cek apakah indeks FAISS sudah ada
    faiss_index_path = os.path.join(VECTOR_DB_PATH, "index.faiss")
    if os.path.exists(faiss_index_path):
        try:
            print(f"System: Memuat indeks FAISS yang ada dari {VECTOR_DB_PATH}")
            return load_vector_store(VECTOR_DB_PATH, embedding_model)
        except Exception as e:
            print(f"System: Gagal memuat indeks FAISS: {e}. Memulai ulang dengan dokumen yang ada.")

    # Jika indeks tidak ada atau gagal dimuat, buat baru dan proses ulang dokumen
    print("System: Indeks FAISS tidak ditemukan atau rusak. Membuat indeks baru dan memproses ulang dokumen.")
    vector_store = FAISS.from_texts([""], embedding_model)  # Inisialisasi kosong sementara

    # Proses ulang semua dokumen yang ada di subfolder
    processed_files = 0
    for ext, folder in SUBFOLDERS.items():
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    print(f"System: Memproses ulang {file_path}")
                    extracted_text = extract_text(file_path)
                    if "Error" not in extracted_text and extracted_text.strip():
                        process_and_store_text(extracted_text, embedding_model, vector_store)
                        processed_files += 1
    
    if processed_files > 0:
        print(f"System: Berhasil memproses ulang {processed_files} dokumen ke FAISS.")
    else:
        print("System: Tidak ada dokumen yang ditemukan untuk diproses ulang.")

    vector_store.save_local(VECTOR_DB_PATH)
    return vector_store

# Inisialisasi vector store
vector_store = initialize_vector_store()

# Jika LangSmith tracing aktif
if LANGSMITH_TRACING:
    from langsmith import Client
    langsmith_client = Client(api_key=os.environ["LANGSMITH_API_KEY"])
    print(f"Terhubung ke LangSmith project: {os.environ['LANGSMITH_PROJECT']}")