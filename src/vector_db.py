from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import torch

def process_and_store_text(text: str, embedding_model, vector_store, metadata: dict = None):
    if not text or not text.strip():
        print("System: Tidak ada teks untuk diproses.")
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True
    )
    chunks = text_splitter.split_text(text)
    
    # Pastikan metadata adalah dict, jika None gunakan default
    if metadata is None:
        metadata = {"filename": "unknown"}
    elif not isinstance(metadata, dict):
        print(f"System: Metadata tidak valid: {metadata}. Menggunakan default.")
        metadata = {"filename": "unknown"}
    
    documents = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]
    
    if not documents:
        print("System: Tidak ada chunk yang dihasilkan dari teks.")
        return
    
    batch_size = 16  # Optimalkan untuk M1 Pro
    total_chunks = len(documents)
    filename = metadata.get('filename', 'unknown')
    print(f"System: Total {total_chunks} chunk akan disimpan untuk dokumen {filename} ke Pinecone.")
    
    for i in range(0, total_chunks, batch_size):
        batch_docs = documents[i:i + batch_size]
        try:
            with torch.no_grad():  # Hemat memori
                vector_store.add_documents(batch_docs)
            print(f"System: Berhasil menyimpan {len(batch_docs)} chunk ke Pinecone (batch {i//batch_size + 1}/{total_chunks//batch_size + 1}).")
        except Exception as e:
            print(f"System: Gagal menyimpan batch ke Pinecone: {str(e)}")
            raise e