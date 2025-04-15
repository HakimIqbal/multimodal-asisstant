from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_vector_store(vector_db_path: str, embedding_model):
    return FAISS.load_local(vector_db_path, embedding_model, allow_dangerous_deserialization=True)

def process_and_store_text(text: str, embedding_model, vector_store):
    if not text.strip():
        print("System: Tidak ada teks untuk diproses.")
        return
    
    # Gunakan RecursiveCharacterTextSplitter untuk chunking berbasis semantik
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        print("System: Tidak ada chunk yang dihasilkan dari teks.")
        return
    
    # Vectorize dan simpan
    embeddings = embedding_model.embed_documents(chunks)
    vector_store.add_texts(texts=chunks, embeddings=embeddings)
    print(f"System: Menyimpan {len(chunks)} chunk ke vector store.")