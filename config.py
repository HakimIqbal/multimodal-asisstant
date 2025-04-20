from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data-rag/faiss_index")
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "data-rag/documents")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "multimodal-assistant")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SUBFOLDERS = {
    ".pdf": os.path.join(DOCUMENTS_PATH, "pdf"),
    ".docx": os.path.join(DOCUMENTS_PATH, "docx"),
    ".png": os.path.join(DOCUMENTS_PATH, "png"),
    ".jpg": os.path.join(DOCUMENTS_PATH, "jpg"),
    ".jpeg": os.path.join(DOCUMENTS_PATH, "jpeg")
}

for folder in SUBFOLDERS.values():
    os.makedirs(folder, exist_ok=True)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY tidak ditemukan di .env")
if not SUPABASE_URL or not SUPABASE_KEY:
    print("System: SUPABASE_URL atau SUPABASE_KEY tidak ditemukan, menggunakan penyimpanan lokal.")

if LANGSMITH_TRACING:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    print("System: LangSmith tracing diaktifkan.")
else:
    print("System: LangSmith tracing tidak diaktifkan.")