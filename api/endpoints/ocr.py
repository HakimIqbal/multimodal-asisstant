from fastapi import APIRouter, File, UploadFile
import os
import json
import shutil
import requests
from src.ocr import extract_text
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store
from config import SUBFOLDERS, SUPABASE_URL, SUPABASE_KEY, DOCUMENTS_PATH, LITERALAI_API_KEY
from datetime import datetime

router = APIRouter()

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...), skip_duplicates: bool = False):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    responses = []
    system_message = (
        "System: Fitur RAG System + OCR aktif. Saya akan memproses file yang Anda unggah (PDF, DOCX, PNG, JPG, JPEG) "
        "untuk mengekstrak teks dan menyimpannya ke basis pengetahuan (FAISS). "
        "Data akan disimpan di cloud (Supabase) jika tersedia, atau lokal (JSON) jika tidak. "
        "File disimpan ke subfolder sesuai formatnya. "
        "Batasan: Hanya format tersebut yang didukung saat ini (maksimal 10 MB per file). "
        f"{'Evaluasi kualitas jawaban akan dicatat di LiteralAI.' if LITERALAI_API_KEY else ''}"
    )
    print(system_message)

    json_path = os.path.join(os.path.dirname(DOCUMENTS_PATH), "uploaded_docs.json")
    local_docs = [] if not os.path.exists(json_path) else json.load(open(json_path, "r"))
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"} if SUPABASE_KEY else None

    for file in files:
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            print(f"System: File '{file.filename}' ({file_size} bytes) melebihi batas {MAX_FILE_SIZE} bytes.")
            responses.append({"filename": file.filename, "text": f"❌ Error: File '{file.filename}' melebihi batas ukuran 10 MB."})
            continue
        file.seek(0)  # Reset pointer

        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in SUBFOLDERS:
            responses.append({"filename": file.filename, "text": f"❌ Error: Format '{ext}' tidak didukung."})
            continue

        file_path = os.path.join(SUBFOLDERS[ext], file.filename)
        final_filename = file.filename

        if os.path.exists(file_path):
            if skip_duplicates:
                responses.append({"filename": file.filename, "text": f"⚠️ File '{file.filename}' dilewati karena sudah ada."})
                continue
            base, ext = os.path.splitext(file.filename)
            file_path = os.path.join(SUBFOLDERS[ext], f"{base}-copy{ext}")
            final_filename = f"{base}-copy{ext}"
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(SUBFOLDERS[ext], f"{base}-copy-{counter}{ext}")
                final_filename = f"{base}-copy-{counter}{ext}"
                counter += 1

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        extracted_text = extract_text(file_path)
        if "Error" not in extracted_text:
            local_docs.append({
                "filename": final_filename,
                "file_format": ext,
                "uploaded_at": datetime.utcnow().isoformat()
            })
            with open(json_path, "w") as f:
                json.dump(local_docs, f, indent=2)

            if SUPABASE_URL and SUPABASE_KEY:
                data = {
                    "filename": final_filename,
                    "file_format": ext,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "text_content": extracted_text
                }
                supabase_response = requests.post(f"{SUPABASE_URL}/rest/v1/uploaded_documents", json=data, headers=headers)
                if supabase_response.status_code == 201:
                    local_docs = [doc for doc in local_docs if doc["filename"] != final_filename]
                    with open(json_path, "w") as f:
                        json.dump(local_docs, f, indent=2)
                    print(f"System: {final_filename} tersinkronisasi ke Supabase, dihapus dari JSON lokal.")
                else:
                    responses.append({"filename": final_filename, "text": f"⚠️ Gagal menyimpan ke Supabase: {supabase_response.text}"})
                    print(f"System: Gagal menyimpan {final_filename} ke Supabase: {supabase_response.text}")

            process_and_store_text(extracted_text, embedding_model, vector_store)

        responses.append({"filename": final_filename, "text": extracted_text})

    return {"status": "success", "results": responses, "system_message": system_message}