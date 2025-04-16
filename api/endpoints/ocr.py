from fastapi import APIRouter, File, UploadFile
import os
import json
import requests
from src.ocr import extract_text
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store
from config import SUBFOLDERS, SUPABASE_URL, SUPABASE_KEY, DOCUMENTS_PATH
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
        "Batasan: Hanya format tersebut yang didukung saat ini (maksimal 10 MB per file)."
    )
    print(system_message)
    print(f"System: Parameter skip_duplicates diterima sebagai: {skip_duplicates}")

    json_path = os.path.join(os.path.dirname(DOCUMENTS_PATH), "uploaded_docs.json")
    local_docs = [] if not os.path.exists(json_path) else json.load(open(json_path, "r"))
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"} if SUPABASE_KEY else None

    for file in files:
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            responses.append({"filename": file.filename, "text": f"❌ Error: File '{file.filename}' melebihi batas ukuran 10 MB.", "status": "error"})
            continue

        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in SUBFOLDERS:
            responses.append({"filename": file.filename, "text": f"❌ Error: Format '{ext}' tidak didukung.", "status": "error"})
            continue

        final_filename = file.filename
        file_path = os.path.normpath(os.path.join(SUBFOLDERS[ext], final_filename))
        print(f"System: Memeriksa duplikat untuk file: {final_filename}")

        # Cek duplikat di lokal (file dan JSON) dan Supabase
        is_duplicate = False
        if skip_duplicates:
            # Cek di sistem file lokal
            print(f"System: Cek sistem file: {file_path}")
            if os.path.exists(file_path):
                print(f"System: Duplikat ditemukan di sistem file: {file_path}")
                is_duplicate = True
            # Cek di uploaded_docs.json
            print(f"System: Cek uploaded_docs.json untuk: {final_filename}")
            if any(doc["filename"] == final_filename for doc in local_docs):
                print(f"System: Duplikat ditemukan di uploaded_docs.json: {final_filename}")
                is_duplicate = True
            # Cek di Supabase
            if SUPABASE_URL and SUPABASE_KEY:
                try:
                    print(f"System: Cek Supabase untuk: {final_filename}")
                    response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/uploaded_documents?filename=eq.{final_filename}",
                        headers=headers
                    )
                    if response.status_code == 200 and response.json():
                        print(f"System: Duplikat ditemukan di Supabase: {final_filename}")
                        is_duplicate = True
                except Exception as e:
                    print(f"System: Gagal memeriksa duplikat di Supabase: {str(e)}")
                    is_duplicate = True  # Anggap duplikat untuk amannya

            if is_duplicate:
                print(f"System: File {final_filename} dilewati karena duplikat.")
                responses.append({
                    "filename": final_filename,
                    "text": f"⚠️ File '{final_filename}' dilewati karena sudah ada.",
                    "status": "skipped"
                })
                continue

        # Tangani duplikat dengan sufiks jika skip_duplicates=False
        if not skip_duplicates:
            base_filename, _ = os.path.splitext(file.filename)
            counter = 1
            while True:
                file_exists = os.path.exists(file_path)
                json_exists = any(doc["filename"] == final_filename for doc in local_docs)
                supabase_exists = False
                if SUPABASE_URL and SUPABASE_KEY:
                    try:
                        response = requests.get(
                            f"{SUPABASE_URL}/rest/v1/uploaded_documents?filename=eq.{final_filename}",
                            headers=headers
                        )
                        if response.status_code == 200 and response.json():
                            supabase_exists = True
                    except Exception as e:
                        print(f"System: Gagal memeriksa duplikat di Supabase: {str(e)}")
                        supabase_exists = True  # Anggap ada untuk amannya

                if file_exists or json_exists or supabase_exists:
                    final_filename = f"{base_filename}-{counter}{ext}"
                    file_path = os.path.normpath(os.path.join(SUBFOLDERS[ext], final_filename))
                    counter += 1
                    continue
                break
            print(f"System: Nama file akhir setelah cek sufiks: {final_filename}")

        # Simpan file ke subfolder lokal
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # Ekstrak teks
        extracted_text = extract_text(file_path)
        if extracted_text.startswith("❌ Error"):
            responses.append({"filename": final_filename, "text": extracted_text, "status": "error"})
            continue

        # Simpan metadata lokal
        local_docs.append({
            "filename": final_filename,
            "file_format": ext,
            "uploaded_at": datetime.utcnow().isoformat()
        })
        with open(json_path, "w") as f:
            json.dump(local_docs, f, indent=2)

        # Simpan ke Supabase
        if SUPABASE_URL and SUPABASE_KEY:
            data = {
                "filename": final_filename[:255],
                "file_format": ext[:20],
                "uploaded_at": datetime.utcnow().isoformat(),
                "text_content": extracted_text
            }
            try:
                supabase_response = requests.post(f"{SUPABASE_URL}/rest/v1/uploaded_documents", json=data, headers=headers)
                if supabase_response.status_code == 201:
                    local_docs = [doc for doc in local_docs if doc["filename"] != final_filename]
                    with open(json_path, "w") as f:
                        json.dump(local_docs, f, indent=2)
                    print(f"System: {final_filename} tersinkronisasi ke Supabase, dihapus dari JSON lokal.")
                else:
                    print(f"System: Gagal menyimpan {final_filename} ke Supabase: {supabase_response.status_code} - {supabase_response.text}")
                    responses.append({"filename": final_filename, "text": f"⚠️ Gagal menyimpan ke Supabase: {supabase_response.text}", "status": "warning"})
            except Exception as e:
                print(f"System: Error saat menyimpan {final_filename} ke Supabase: {str(e)}")
                responses.append({"filename": final_filename, "text": f"⚠️ Gagal menyimpan ke Supabase: {str(e)}", "status": "warning"})

        # Simpan teks ke FAISS
        process_and_store_text(extracted_text, embedding_model, vector_store)
        responses.append({
            "filename": final_filename,
            "text": "Teks berhasil diekstrak dan disimpan.",
            "status": "success",
            "preview": extracted_text[:100] + ("..." if len(extracted_text) > 100 else "")
        })

    return {"status": "success", "results": responses, "system_message": system_message}