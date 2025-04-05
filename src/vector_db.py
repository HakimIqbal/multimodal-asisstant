import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from groq import Groq
from config import Config

# Inisialisasi Groq Client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

# Gunakan model embedding dari HuggingFace (bisa diganti dengan Groq jika tersedia)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_vector_store():
    if os.path.exists(Config.VECTOR_DB_PATH):
        return FAISS.load_local(Config.VECTOR_DB_PATH, embedding_model)
    else:
        return FAISS.from_texts([""], embedding_model)

vector_store = load_vector_store()

def add_text_to_vector_store(text: str, source: str):
    if not text.strip():
        return "Teks kosong tidak ditambahkan."
    vector_store.add_texts([text], metadatas=[{"source": source}])
    vector_store.save_local(Config.VECTOR_DB_PATH)
    return f"Teks dari {source} ditambahkan ke Vector DB."

def search_vector_store(query: str, top_k: int = 3):
    results = vector_store.similarity_search(query, k=top_k)
    return [(doc.page_content, doc.metadata) for doc in results]