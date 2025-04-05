from fastapi import APIRouter, File, UploadFile
import os
import shutil
from src.ocr import extract_text
from src.vector_db import add_text_to_vector_store
from config import Config

router = APIRouter()

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    responses = []
    for file in files:
        file_path = os.path.join(Config.DOCUMENTS_PATH, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = extract_text(file_path)
        result = add_text_to_vector_store(text, file.filename)
        responses.append({"filename": file.filename, "text": text, "status": result})
    
    return {"status": "success", "results": responses}