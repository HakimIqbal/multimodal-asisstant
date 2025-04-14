import json
import os
import uuid
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langsmith import Client
from models import llm, vector_store
from config import LANGSMITH_TRACING

prompt_template = """System: Anda adalah Assistant yang HANYA menjawab berdasarkan dokumen yang diunggah melalui RAG System + OCR. 
Anda DILARANG menggunakan pengetahuan eksternal atau memberikan jawaban spekulatif di luar dokumen. 
Jika tidak ada dokumen yang relevan atau informasi tidak tersedia, Anda HARUS menjawab: 
"Assistant: Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
Context: {context}
Question: {question}
Answer:"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Inisialisasi callback LangSmith jika tracing aktif
callback_manager = CallbackManager([]) if LANGSMITH_TRACING else None
if LANGSMITH_TRACING:
    langsmith_client = Client()
    print(f"System: LangSmith tracing diaktifkan untuk project: {os.environ.get('LANGSMITH_PROJECT', 'default')}")

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": PROMPT},
    callback_manager=callback_manager
)

def query_rag(question: str):
    if LANGSMITH_TRACING:
        print(f"System: Melacak query '{question}' di LangSmith.")
    
    docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
    if not docs or all(doc.page_content.strip() == "" for doc in docs):
        answer = "Assistant: Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
    else:
        result = rag_chain.invoke({"query": question})
        answer = result["result"]

    # Logging manual untuk Generation
    log_dir = Path("data-rag/logs")
    log_file = log_dir / "generations.json"
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        # Inisialisasi log_data
        log_data = {"generations": []}
        if log_file.exists():
            with log_file.open("r", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:
                    try:
                        log_data = json.loads(file_content)
                        if not isinstance(log_data.get("generations"), list):
                            print(f"System: Struktur {log_file} tidak valid, menginisialisasi ulang.")
                            log_data = {"generations": []}
                    except JSONDecodeError:
                        print(f"System: File {log_file} tidak valid, menginisialisasi ulang.")
                        log_data = {"generations": []}
        
        # Tambahkan entri baru
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "input": question,
            "output": answer,
            "metadata": {
                "source": "RAG System + OCR",
                "model": "llama3-70b-8192",
                "context_docs": len(docs)
            }
        }
        log_data["generations"].append(log_entry)
        
        # Simpan kembali ke file
        with log_file.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        print(f"System: Generation untuk query '{question}' dicatat di {log_file}.")
    except Exception as e:
        print(f"System: Gagal mencatat generation: {str(e)}.")
    
    return answer