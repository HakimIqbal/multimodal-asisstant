import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "multimodal-assistant")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "multimodal_assistant")
}

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY tidak ditemukan di .env")

if LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    print("System: LangSmith tracing diaktifkan.")
else:
    print("System: LangSmith tracing tidak diaktifkan.")