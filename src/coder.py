import json
import os
import uuid
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
import requests
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from models import get_groq_model
from config import LANGSMITH_TRACING, SUPABASE_URL, SUPABASE_KEY

# Inisialisasi ChatMessageHistory secara langsung
coder_chat_history = ChatMessageHistory()

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "System: Anda adalah asisten coding yang memberikan jawaban singkat, langsung ke inti, dan terstruktur. Gunakan Markdown untuk formatting (misalnya, **bold**, *italic*, atau ``` untuk blok kode). Jangan ulangi pertanyaan atau berikan informasi yang tidak relevan. Jawab dengan bahasa yang sama seperti input pengguna (misalnya, jika input dalam bahasa Indonesia, jawab dalam bahasa Indonesia; jika dalam bahasa Inggris, jawab dalam bahasa Inggris). Sertakan contoh kode dalam blok kode Markdown jika diperlukan. Jika jawaban panjang, gunakan poin-poin untuk memudahkan pembacaan."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{query}")
])

def detect_language(query: str) -> str:
    indonesian_words = {"apa", "bagaimana", "siapa", "dimana", "kapan", "mengapa", "adalah"}
    query_lower = query.lower()
    if any(word in query_lower for word in indonesian_words):
        return "id"
    return "en"

def chat_coder(query: str, model_name: str = "llama3-70b-8192"):
    if LANGSMITH_TRACING:
        print(f"System: Melacak coder query '{query}' di LangSmith.")
    
    # Tahap 1: Pemahaman Pertanyaan
    print(f"System: Memahami pertanyaan coding: {query}")
    language = detect_language(query)
    print(f"System: Bahasa terdeteksi: {language}")

    # Tahap 2: Pencarian Informasi (opsional)

    # Tahap 3: Pengolahan dan Penalaran
    print(f"System: Memproses dan menalar jawaban coding untuk: {query}")
    llm = get_groq_model(model_name)
    
    # Ambil riwayat percakapan
    chat_history = coder_chat_history.messages
    
    # Gabungkan prompt dengan riwayat dan query
    prompt = prompt_template.format_messages(query=query, chat_history=chat_history)
    
    # Tahap 4: Penyusunan Jawaban
    response = llm.invoke(prompt)
    answer = response.content.strip()

    # Tahap 5: Post-Processing (opsional)
    if len(answer.split()) > 50 and "\n" not in answer:
        answer = "\n".join([answer[i:i+100] for i in range(0, len(answer), 100)])

    # Simpan ke riwayat
    coder_chat_history.add_user_message(query)
    coder_chat_history.add_ai_message(answer)

    # Tahap 6: Pemeriksaan Konteks
    print(f"System: Memeriksa konteks jawaban coding untuk: {query}")

    # Tahap 7: Penyampaian
    log_dir = Path("data-rag/logs")
    archive_dir = log_dir / "archive"
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = log_dir / f"coder_chat-{today}.json"
    
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
            "input": query,
            "output": answer,
            "metadata": {
                "source": "Coder Chatbot",
                "model": model_name,
                "context": "Coding",
                "language": language
            }
        }
        log_data["generations"].append(log_entry)
        
        with log_file.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        print(f"System: Chat coding untuk query '{query}' dicatat di {log_file}.")
        
        if log_file.stat().st_size > 10 * 1024 * 1024:
            archive_path = archive_dir / f"coder_chat-{today}.json"
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
                response = requests.post(f"{SUPABASE_URL}/rest/v1/coder_chat_logs", json=log_entry, headers=headers)
                if response.status_code == 201:
                    print(f"System: Chat coding untuk query '{query}' tersinkronisasi ke Supabase (coder_chat_logs).")
                else:
                    print(f"System: Gagal menyimpan chat coding ke Supabase: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"System: Error saat menyimpan chat coding ke Supabase: {str(e)}")
                
    except Exception as e:
        print(f"System: Gagal mencatat chat coding: {str(e)}.")
    
    return answer