import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi global
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH")
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LITERALAI_API_KEY = os.getenv("LITERALAI_API_KEY")

# Pastikan API key tersedia
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY tidak ditemukan di .env")