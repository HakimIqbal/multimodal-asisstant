from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import VECTOR_DB_PATH
import torch

def load_vector_store(vector_db_path: str, embedding_model):
    try:
        return FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"System: Gagal memuat vector store: {str(e)}. Membuat vector store baru.")
        return FAISS.from_texts([""], embedding_model)

def process_and_store_text(text: str, embedding_model, vector_store):
    if not text.strip():
        print("System: Tidak ada teks untuk diproses.")
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        print("System: Tidak ada chunk yang dihasilkan dari teks.")
        return
    
    batch_size = 32  
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        try:
            with torch.no_grad():  
                embeddings = embedding_model.embed_documents(batch_chunks)
            vector_store.add_texts(texts=batch_chunks, embeddings=embeddings)
            print(f"System: Menyimpan {len(batch_chunks)} chunk ke vector store.")
        except Exception as e:
            print(f"System: Gagal menyimpan batch ke vector store: {str(e)}")
    
    try:
        vector_store.save_local(VECTOR_DB_PATH)
        print("System: Vector store disimpan.")
    except Exception as e:
        print(f"System: Gagal menyimpan vector store: {str(e)}")