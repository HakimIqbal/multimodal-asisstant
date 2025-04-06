from langchain_community.vectorstores import FAISS  # Perbarui impor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import VECTOR_DB_PATH

def load_vector_store(path: str, embedding_model):
    return FAISS.load_local(path, embedding_model)

def process_and_store_text(text: str, embedding_model, vector_store):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text)
    vector_store.add_texts(chunks)
    vector_store.save_local(VECTOR_DB_PATH)
    return f"Berhasil memproses dan menyimpan {len(chunks)} chunks ke FAISS."