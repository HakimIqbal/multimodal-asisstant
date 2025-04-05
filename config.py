# Konfigurasi global (path model, API keys, dsb.)
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi global
class Config:
    MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q3_K_M.gguf"
    VECTOR_DB_PATH = "data-rag/embeddings/faiss_index"
    DOCUMENTS_PATH = "data-rag/documents/"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # API Key dari Groq Cloud
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")  # API Key untuk LangSmith