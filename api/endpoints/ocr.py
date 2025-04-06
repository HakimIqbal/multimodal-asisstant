from fastapi import APIRouter, File, UploadFile
import os
import shutil
from src.ocr import extract_text
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store
from config import SUBFOLDERS

router = APIRouter()

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    responses = []
    system_message = (
        "System: Fitur RAG System + OCR aktif. Saya akan memproses file yang Anda unggah (PDF, DOCX, PNG, JPG, JPEG) "
        "untuk mengekstrak teks dan menyimpannya ke basis pengetahuan (FAISS). File akan disimpan ke subfolder sesuai formatnya. "
        "Batasan: Hanya file dengan format tersebut yang didukung saat ini. Assistant akan menjawab pertanyaan Anda hanya "
        "berdasarkan dokumen yang diunggah."
    )
    print(system_message)  # System menjelaskan peran dan batasan

    for file in files:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in SUBFOLDERS:
            responses.append({"filename": file.filename, "text": f"❌ Error: Format '{ext}' tidak didukung."})
            continue
        
        # Simpan file ke subfolder sesuai format
        file_path = os.path.join(SUBFOLDERS[ext], file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Proses teks dan simpan ke FAISS
        extracted_text = extract_text(file_path)
        if "Error" not in extracted_text:
            process_and_store_text(extracted_text, embedding_model, vector_store)
        responses.append({"filename": file.filename, "text": extracted_text})
    
    return {"status": "success", "results": responses, "system_message": system_message}