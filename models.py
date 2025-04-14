import os
import json
import requests
import glob
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Nonaktifkan paralelisme HuggingFace
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from src.vector_db import load_vector_store, process_and_store_text
from src.ocr import extract_text
from config import GROQ_API_KEY, VECTOR_DB_PATH, LANGSMITH_TRACING, SUPABASE_URL, SUPABASE_KEY, DOCUMENTS_PATH

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-70b-8192", temperature=0.0, max_tokens=4096)

try:
    vector_store = load_vector_store(VECTOR_DB_PATH, embedding_model)
except:
    vector_store = FAISS.from_texts([""], embedding_model)
    vector_store.save_local(VECTOR_DB_PATH)

JSON_LOG_PATH = os.path.join(os.path.dirname(DOCUMENTS_PATH), "uploaded_docs.json")

def load_from_supabase():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    response = requests.get(f"{SUPABASE_URL}/rest/v1/uploaded_documents", headers=headers)
    if response.status_code == 200:
        docs = response.json()
        for doc in docs:
            process_and_store_text(doc["text_content"], embedding_model, vector_store)
        print("System: Memuat ulang dokumen dari Supabase ke FAISS.")
    else:
        print(f"System: Gagal memuat dari Supabase: {response.text}")

def load_from_json():
    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r") as f:
            docs = json.load(f)
            for doc in docs:
                file_path = os.path.join(DOCUMENTS_PATH, doc["file_format"][1:], doc["filename"])
                if os.path.exists(file_path):
                    text = extract_text(file_path)
                    process_and_store_text(text, embedding_model, vector_store)
            print("System: Memuat ulang dokumen dari JSON lokal ke FAISS.")
    else:
        print("System: File JSON lokal tidak ditemukan, mencoba pindai folder dokumen.")

def load_from_documents_folder():
    supported_extensions = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]
    for ext in supported_extensions:
        folder = os.path.join(DOCUMENTS_PATH, ext[1:])
        if os.path.exists(folder):
            for file_path in glob.glob(os.path.join(folder, f"*{ext}")):
                text = extract_text(file_path)
                if "Error" not in text:
                    process_and_store_text(text, embedding_model, vector_store)
                    print(f"System: Memuat ulang {os.path.basename(file_path)} dari folder dokumen.")
    print("System: Selesai memindai folder dokumen.")

if len(vector_store.index.reconstruct_n(0, vector_store.index.ntotal)) <= 1:
    if SUPABASE_URL and SUPABASE_KEY:
        load_from_supabase()
    else:
        load_from_json()
        if os.path.exists(JSON_LOG_PATH) and not json.load(open(JSON_LOG_PATH, "r")):
            load_from_documents_folder()

if LANGSMITH_TRACING:
    from langsmith import Client
    langsmith_client = Client()
    print(f"System: Terhubung ke LangSmith project: {os.environ['LANGSMITH_PROJECT']}")