from fastapi import APIRouter, File, UploadFile
import os
import shutil
from src.ocr import extract_text
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store

router = APIRouter()
UPLOAD_DIR = "data-rag/documents/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    responses = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        extracted_text = extract_text(file_path)
        if "Error" not in extracted_text:
            process_and_store_text(extracted_text, embedding_model, vector_store)
        responses.append({"filename": file.filename, "text": extracted_text})
    return {"status": "success", "results": responses}