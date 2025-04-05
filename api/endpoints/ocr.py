from fastapi import APIRouter, File, UploadFile
import os
import shutil
from src.ocr import extract_text  # Import fungsi OCR dari src

router = APIRouter()

UPLOAD_DIR = "data-rag/documents/"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Buat folder jika belum ada

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    """Menerima banyak file (PNG, JPG, JPEG, PDF, DOCX), menyimpannya, lalu mengekstrak teks"""
    responses = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Simpan file yang diunggah
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ekstrak teks dari file
        extracted_text = extract_text(file_path)
        responses.append({"filename": file.filename, "text": extracted_text})
    
    return {"status": "success", "results": responses}
