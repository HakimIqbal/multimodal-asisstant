import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data-rag/faiss_index")
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "data-rag/documents")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LITERALAI_API_KEY = os.getenv("LITERALAI_API_KEY")
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
if not LITERALAI_API_KEY:
    print("System: LITERALAI_API_KEY tidak ditemukan, evaluasi LiteralAI tidak akan aktif.")
else:
    print("System: LiteralAI diaktifkan untuk evaluasi kualitas output LLM.")

if LANGSMITH_TRACING:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    print("LangSmith tracing diaktifkan.")
else:
    print("LangSmith tracing tidak diaktifkan.")