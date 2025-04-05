from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_groq import ChatGroq
from src.vector_db import load_vector_store
from config import GROQ_API_KEY, VECTOR_DB_PATH, LANGSMITH_TRACING

# Inisialisasi model embedding untuk FAISS
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Inisialisasi LLM dari Groq
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="mixtral-8x7b-32768",  # Model Groq yang tersedia
    temperature=0.7,
    max_tokens=4096
)

# Load atau buat FAISS Vector Store
try:
    vector_store = load_vector_store(VECTOR_DB_PATH, embedding_model)
except:
    vector_store = FAISS.from_texts([""], embedding_model)
    vector_store.save_local(VECTOR_DB_PATH)

# Jika LangSmith tracing aktif, pastikan semua operasi LLM dan vector store akan dilacak otomatis oleh LangChain
if LANGSMITH_TRACING:
    from langsmith import Client
    langsmith_client = Client(api_key=os.environ["LANGSMITH_API_KEY"], endpoint=os.environ["LANGSMITH_ENDPOINT"])
    print(f"Terhubung ke LangSmith project: {os.environ['LANGSMITH_PROJECT']}")