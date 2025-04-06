import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi global
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH")
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LITERALAI_API_KEY = os.getenv("LITERALAI_API_KEY")

# Pastikan API key tersedia
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY tidak ditemukan di .env")
if not LANGSMITH_API_KEY and LANGSMITH_TRACING:
    raise ValueError("LANGSMITH_API_KEY tidak ditemukan di .env meskipun tracing diaktifkan")
if not LITERALAI_API_KEY:
    print("LITERALAI_API_KEY tidak ditemukan, evaluasi LiteralAI tidak akan aktif.")

# Konfigurasi LangSmith tracing
if LANGSMITH_TRACING:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGCHAIN_TRACING_V2"] = "true"  # Aktifkan tracing v2 untuk LangChain
    print("LangSmith tracing diaktifkan.")
else:
    print("LangSmith tracing tidak diaktifkan.")