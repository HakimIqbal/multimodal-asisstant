import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from src.vector_db import load_vector_store, process_and_store_text
from config import GROQ_API_KEY, VECTOR_DB_PATH, DOCUMENTS_PATH, SUBFOLDERS, LANGSMITH_TRACING
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

# Fungsi untuk memeriksa apakah ada dokumen di subfolder
def has_documents():
    for folder in SUBFOLDERS.values():
        if os.path.exists(folder) and any(os.path.isfile(os.path.join(folder, f)) for f in os.listdir(folder)):
            return True
    return False

# Fungsi untuk menginisialisasi atau memuat vector store
def initialize_vector_store():
    faiss_index_path = os.path.join(VECTOR_DB_PATH, "index.faiss")
    has_docs = has_documents()

    if os.path.exists(faiss_index_path):
        try:
            print(f"System: Memuat indeks FAISS yang ada dari {VECTOR_DB_PATH}")
            vector_store = load_vector_store(VECTOR_DB_PATH, embedding_model, allow_dangerous_deserialization=True)
            if not has_docs:
                print("System: Peringatan: Tidak ada dokumen ditemukan di subfolder, tetapi indeks FAISS masih ada. "
                      "Indeks mungkin tidak sesuai dengan dokumen saat ini.")
            return vector_store
        except Exception as e:
            print(f"System: Gagal memuat indeks FAISS: {e}. Memulai ulang dengan dokumen yang ada.")

    # Jika indeks tidak ada atau gagal dimuat, buat baru
    print("System: Indeks FAISS tidak ditemukan atau rusak. Membuat indeks baru.")
    vector_store = FAISS.from_texts([""], embedding_model)

    # Proses ulang dokumen jika ada
    processed_files = 0
    if has_docs:
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
            print("System: Tidak ada dokumen valid yang ditemukan untuk diproses ulang.")
    else:
        print("System: Tidak ada dokumen di subfolder untuk diproses. Indeks FAISS akan kosong sampai dokumen baru diunggah.")

    vector_store.save_local(VECTOR_DB_PATH)
    return vector_store

# Inisialisasi vector store
vector_store = initialize_vector_store()

# Jika LangSmith tracing aktif
if LANGSMITH_TRACING:
    from langsmith import Client
    langsmith_client = Client(api_key=os.environ["LANGSMITH_API_KEY"])
    print(f"Terhubung ke LangSmith project: {os.environ['LANGSMITH_PROJECT']}")