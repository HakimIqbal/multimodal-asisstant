import json
import os
import uuid
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
import requests
from langchain.chains import LLMChain, StuffDocumentsChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langsmith import Client
from models import llm, vector_store
from config import LANGSMITH_TRACING, SUPABASE_URL, SUPABASE_KEY

# Prompt template untuk LLMChain
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "System: Anda adalah Assistant yang HANYA menjawab berdasarkan dokumen yang diunggah melalui RAG System + OCR. Anda DILARANG menggunakan pengetahuan eksternal atau memberikan jawaban spekulatif di luar dokumen. Jika tidak ada dokumen yang relevan atau informasi tidak tersedia, Anda HARUS menjawab: 'Assistant: Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini.' Jawab dengan bahasa yang sama seperti input pengguna (misalnya, jika input dalam bahasa Indonesia, jawab dalam bahasa Indonesia; jika dalam bahasa Inggris, jawab dalam bahasa Inggris). Gunakan Markdown untuk formatting (misalnya, **bold**, *italic*, atau ``` untuk blok kode). Berikan jawaban yang singkat, terstruktur, dan langsung ke inti. Jika jawaban panjang, gunakan poin-poin untuk memudahkan pembacaan."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Context dari dokumen: {context}\nPertanyaan: {question}")
])

# Buat LLMChain secara manual
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    verbose=True
)

# Buat StuffDocumentsChain
stuff_chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_variable_name="context",
    verbose=True
)

def detect_language(query: str) -> str:
    indonesian_words = {"apa", "bagaimana", "siapa", "dimana", "kapan", "mengapa", "adalah"}
    query_lower = query.lower()
    if any(word in query_lower for word in indonesian_words):
        return "id"
    return "en"

def query_rag(question: str, chat_history=None):
    if LANGSMITH_TRACING:
        print(f"System: Melacak query '{question}' di LangSmith.")
    
    # Deteksi bahasa
    language = detect_language(question)
    print(f"System: Bahasa terdeteksi: {language}")
    
    # Gunakan riwayat percakapan (jika ada), jika tidak inisialisasi kosong
    chat_history = chat_history or []
    
    # Tahap 1: Pemahaman Pertanyaan
    print(f"System: Memahami pertanyaan RAG: {question}")

    # Tahap 2: Pencarian Informasi (dari dokumen)
    docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)
    if not docs or all(doc.page_content.strip() == "" for doc in docs):
        answer = "Assistant: Saya tidak memiliki informasi cukup dari dokumen yang diunggah untuk menjawab ini."
    else:
        # Tahap 3: Pengolahan dan Penalaran
        print(f"System: Memproses dan menalar jawaban RAG untuk: {question}")
        # Siapkan input untuk StuffDocumentsChain
        inputs = {
            "question": question,
            "chat_history": chat_history,
            "input_documents": docs
        }
        result = stuff_chain.invoke(inputs)
        answer = result["output_text"].strip()

        # Tahap 4: Post-Processing (opsional)
        if len(answer.split()) > 50 and "\n" not in answer:
            answer = "\n".join([answer[i:i+100] for i in range(0, len(answer), 100)])

    # Tahap 5: Pemeriksaan Konteks
    print(f"System: Memeriksa konteks jawaban RAG untuk: {question}")

    # Tahap 6: Penyampaian
    log_dir = Path("data-rag/logs")
    archive_dir = log_dir / "archive"
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = log_dir / f"generations-{today}.json"
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "input": question,
            "output": answer,
            "metadata": {
                "source": "RAG System + OCR",
                "model": "llama3-70b-8192",
                "context_docs": len(docs),
                "language": language
            }
        }
        log_data["generations"].append(log_entry)
        
        with log_file.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        print(f"System: Generation untuk query '{question}' dicatat di {log_file}.")
        
        if log_file.stat().st_size > 10 * 1024 * 1024:
            archive_path = archive_dir / f"generations-{today}.json"
            log_file.rename(archive_path)
            print(f"System: File {log_file} diarsipkan ke {archive_path} karena melebihi 10 MB.")
            log_data = {"generations": []}
            with log_file.open("w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
        
        if SUPABASE_URL and SUPABASE_KEY:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(f"{SUPABASE_URL}/rest/v1/generations", json=log_entry, headers=headers)
                if response.status_code == 201:
                    print(f"System: Generation untuk query '{question}' tersinkronisasi ke Supabase.")
                else:
                    print(f"System: Gagal menyimpan generation ke Supabase: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"System: Error saat menyimpan generation ke Supabase: {str(e)}")
                
    except Exception as e:
        print(f"System: Gagal mencatat generation: {str(e)}.")
    
    # Simpan riwayat percakapan
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))
    
    return answer, chat_history