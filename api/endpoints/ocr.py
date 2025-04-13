from fastapi import APIRouter, File, UploadFile
import os
import json
import shutil
import requests
from src.ocr import extract_text
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store
from config import SUBFOLDERS, SUPABASE_URL, SUPABASE_KEY, DOCUMENTS_PATH
from datetime import datetime

router = APIRouter()

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    responses = []
    system_message = (
        "System: Fitur RAG System + OCR aktif. Saya akan memproses file yang Anda unggah (PDF, DOCX, PNG, JPG, JPEG) "
        "untuk mengekstrak teks dan menyimpannya ke basis pengetahuan (FAISS). "
        "Data akan disimpan di cloud (Supabase) jika tersedia, atau lokal (JSON) jika tidak. "
        "File disimpan ke subfolder sesuai formatnya. "
        "Batasan: Hanya format tersebut yang didukung saat ini. "
        f"{'Evaluasi kualitas jawaban akan dicatat di LiteralAI.' if LITERALAI_API_KEY else ''}"
    )
    print(system_message)

    # Path untuk JSON lokal
    json_path = os.path.join(os.path.dirname(DOCUMENTS_PATH), "uploaded_docs.json")
    local_docs = [] if not os.path.exists(json_path) else json.load(open(json_path, "r"))

    # Headers untuk Supabase
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"} if SUPABASE_KEY else None

    for file in files:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in SUBFOLDERS:
            responses.append({"filename": file.filename, "text": f"❌ Error: Format '{ext}' tidak didukung."})
            continue

        # Simpan file ke subfolder
        file_path = os.path.join(SUBFOLDERS[ext], file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ekstrak teks
        extracted_text = extract_text(file_path)
        if "Error" not in extracted_text:
            # Simpan ke Supabase jika tersedia
            if SUPABASE_URL and SUPABASE_KEY:
                data = {
                    "filename": file.filename,
                    "file_format": ext,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "text_content": extracted_text
                }
                supabase_response = requests.post(f"{SUPABASE_URL}/rest/v1/uploaded_documents", json=data, headers=headers)
                if supabase_response.status_code != 201:
                    print(f"System: Gagal menyimpan {file.filename} ke Supabase: {supabase_response.text}")

            # Simpan ke JSON lokal
            local_docs.append({
                "filename": file.filename,
                "file_format": ext,
                "uploaded_at": datetime.utcnow().isoformat()
            })
            with open(json_path, "w") as f:
                json.dump(local_docs, f, indent=2)

            # Indeks ke FAISS
            process_and_store_text(extracted_text, embedding_model, vector_store)

        responses.append({"filename": file.filename, "text": extracted_text})

    return {"status": "success", "results": responses, "system_message": system_message}