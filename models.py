import os
import mysql.connector
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from src.vector_db import process_and_store_text
from src.db import get_db_connection
from config import GROQ_API_KEY, LANGSMITH_TRACING, MYSQL_CONFIG, PINECONE_API_KEY

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "mps" if torch.backends.mps.is_available() else "cpu"}
)

INDEX_NAME = "rag-index"
try:
    vector_store = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embedding_model,
        pinecone_api_key=PINECONE_API_KEY
    )
    print("System: Berhasil memuat Pinecone vector store.")
except Exception as e:
    print(f"System: Gagal memuat Pinecone vector store: {str(e)}. Membuat indeks baru.")
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,  
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"  
        )
    )
    vector_store = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embedding_model,
        pinecone_api_key=PINECONE_API_KEY
    )

SUPPORTED_GROQ_MODELS = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

def get_groq_model(model_name: str = "llama3-70b-8192"):
    if model_name not in SUPPORTED_GROQ_MODELS:
        print(f"System: Model '{model_name}' tidak didukung. Menggunakan default 'llama3-70b-8192'.")
        model_name = "llama3-70b-8192"
    try:
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=model_name,
            temperature=0.0,
            max_tokens=4096
        )
    except Exception as e:
        print(f"System: Gagal memuat model '{model_name}': {str(e)}. Menggunakan default 'llama3-70b-8192'.")
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama3-70b-8192",
            temperature=0.0,
            max_tokens=4096
        )

llm = get_groq_model()

def load_from_mysql():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, text_content FROM documents")
        docs = cursor.fetchall()
        print(f"System: Memuat {len(docs)} dokumen dari MySQL.")
        for filename, text_content in docs:
            print(f"System: Mengindeks dokumen: {filename}, ukuran teks: {len(text_content)} karakter")
            process_and_store_text(text_content, embedding_model, vector_store, metadata={"filename": filename})
        print("System: Selesai memuat ulang dokumen dari MySQL ke Pinecone.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"System: Gagal memuat dari MySQL: {str(e)}")

load_from_mysql()

if LANGSMITH_TRACING:
    from langsmith import Client
    langsmith_client = Client()
    print(f"System: Terhubung ke LangSmith project: {os.environ['LANGSMITH_PROJECT']}")