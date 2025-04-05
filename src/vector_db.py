import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# Load model untuk embedding
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Path untuk menyimpan FAISS Index
INDEX_PATH = "data-rag/embeddings/faiss_index.bin"
METADATA_PATH = "data-rag/embeddings/metadata.pkl"

# Cek apakah FAISS Index sudah ada
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
else:
    index = faiss.IndexFlatL2(384)  # 384 dimensi untuk model MiniLM
    metadata = []

def add_text_to_faiss(text: str, source: str):
    """
    Menambahkan teks hasil OCR ke FAISS Index.
    
    Args:
        text (str): Teks yang diekstrak dari file.
        source (str): Sumber dokumen (misalnya: nama file).
    """
    if not text.strip():
        return "Teks kosong tidak akan ditambahkan ke FAISS."

    # Generate embedding
    embedding = embedding_model.encode([text])[0]
    index.add(embedding.reshape(1, -1))
    
    # Simpan metadata
    metadata.append({"source": source, "text": text})

    # Save FAISS index & metadata
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    return f"Teks dari {source} berhasil ditambahkan ke FAISS."

def search_faiss(query: str, top_k: int = 3) -> List[Tuple[str, str]]:
    """
    Melakukan pencarian teks serupa di FAISS berdasarkan query.
    
    Args:
        query (str): Input pencarian.
        top_k (int): Jumlah hasil yang ingin dikembalikan.
    
    Returns:
        List[Tuple[str, str]]: Daftar hasil (sumber, teks).
    """
    if len(metadata) == 0:
        return [("Tidak ada data dalam FAISS.", "")]

    # Generate embedding untuk query
    query_embedding = embedding_model.encode([query])
    
    # Cari di FAISS
    D, I = index.search(query_embedding, top_k)
    
    results = [(metadata[i]["source"], metadata[i]["text"]) for i in I[0] if i < len(metadata)]
    return results if results else [("Tidak ditemukan hasil yang relevan.", "")]
