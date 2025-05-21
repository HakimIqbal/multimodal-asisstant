import io
import os  
import uuid
from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import re
import mysql.connector
import cloudinary.uploader
from src.rag import query_rag
from src.vector_db import process_and_store_text
from models import embedding_model, vector_store
from src.db import save_document_to_mysql
from config import MYSQL_CONFIG  
from pydantic import BaseModel
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    chat_history: list = None

def clean_text(text: str) -> str:
    text = re.sub(r'[^\w\s.,!?()-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_with_ocr(file_content: bytes) -> str:
    try:
        images = convert_from_bytes(file_content)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang='eng+ind') + "\n"
        return text.strip()
    except Exception as e:
        print(f"System: Gagal mengekstrak teks dengan OCR: {str(e)}")
        return ""

@router.post("/upload/")
async def upload_files(files: List[UploadFile], skip_duplicates: bool = False):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    results = []
    system_message = (
        "System: Fitur RAG System aktif. Saya akan memproses file dokumen (PDF) "
        "untuk mengekstrak teks dan menyimpannya ke basis pengetahuan (Pinecone). "
        "File diunggah ke Cloudinary, dan metadata disimpan di MySQL. "
        "Batasan: Maksimal 10 MB per file."
    )
    print(system_message)

    for file in files:
        filename = file.filename
        try:
            file_content = await file.read()
            file_size = len(file_content)
            if file_size > MAX_FILE_SIZE:
                results.append({
                    "status": "error",
                    "filename": filename,
                    "text": f"❌ Error: File '{filename}' melebihi batas ukuran 10MB."
                })
                continue

            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            if ext != ".pdf":
                results.append({
                    "status": "error",
                    "filename": filename,
                    "text": f"❌ Error: Format '{ext}' tidak didukung."
                })
                continue

            try:
                conn = mysql.connector.connect(**MYSQL_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT filename FROM documents WHERE filename = %s", (filename,))
                is_duplicate = cursor.fetchone() is not None
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"System: Gagal memeriksa duplikat di MySQL: {str(e)}")
                results.append({
                    "status": "error",
                    "filename": filename,
                    "text": f"❌ Error: Gagal memeriksa duplikat di database."
                })
                continue

            if skip_duplicates and is_duplicate:
                results.append({
                    "status": "skipped",
                    "filename": filename,
                    "text": f"⚠️ File '{filename}' dilewati karena sudah ada."
                })
                continue

            final_filename = filename
            if is_duplicate and not skip_duplicates:
                base, ext = os.path.splitext(filename)
                counter = 1
                while counter <= 100:
                    final_filename = f"{base}-{counter}{ext}"
                    try:
                        conn = mysql.connector.connect(**MYSQL_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("SELECT filename FROM documents WHERE filename = %s", (final_filename,))
                        is_duplicate = cursor.fetchone() is not None
                        cursor.close()
                        conn.close()
                        if not is_duplicate:
                            break
                    except Exception as e:
                        print(f"System: Gagal memeriksa duplikat untuk {final_filename}: {str(e)}")
                        break
                    counter += 1
                if counter > 100:
                    results.append({
                        "status": "error",
                        "filename": filename,
                        "text": f"❌ Error: Gagal menemukan nama unik setelah 100 percobaan."
                    })
                    continue

            text_content = ""
            try:
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            except Exception as e:
                print(f"System: Gagal mengekstrak teks dari PDF dengan pdfplumber: {str(e)}")

            if not text_content.strip():
                print(f"System: Teks dari pdfplumber kosong, menggunakan OCR untuk {final_filename}.")
                text_content = extract_text_with_ocr(file_content)

            if not text_content.strip():
                results.append({
                    "status": "error",
                    "filename": final_filename,
                    "text": "❌ Error: Tidak ada teks yang dapat diekstrak dari file."
                })
                continue

            try:
                upload_result = cloudinary.uploader.upload(
                    io.BytesIO(file_content),
                    resource_type="raw",
                    public_id=f"documents/{final_filename}",
                    overwrite=True
                )
                file_url = upload_result["secure_url"]
            except Exception as e:
                print(f"System: Gagal mengunggah file {final_filename} ke Cloudinary: {str(e)}")
                results.append({
                    "status": "error",
                    "filename": final_filename,
                    "text": f"❌ Error: Gagal mengunggah file ke Cloudinary."
                })
                continue

            text_content = clean_text(text_content)
            try:
                save_document_to_mysql(final_filename, ext, text_content, file_url=file_url)
            except Exception as e:
                print(f"System: Gagal menyimpan dokumen {final_filename} ke MySQL: {str(e)}")
                results.append({
                    "status": "error",
                    "filename": final_filename,
                    "text": f"❌ Error: Gagal menyimpan dokumen ke database."
                })
                continue

            try:
                process_and_store_text(text_content, embedding_model, vector_store, metadata={"filename": final_filename, "url": file_url})
            except Exception as e:
                print(f"System: Gagal menyimpan teks ke Pinecone untuk {final_filename}: {str(e)}")
                results.append({
                    "status": "error",
                    "filename": final_filename,
                    "text": f"❌ Error: Gagal menyimpan teks ke basis pengetahuan."
                })
                continue

            preview = text_content[:100].replace("\n", " ") + "..." if len(text_content) > 100 else text_content
            results.append({
                "status": "success",
                "filename": final_filename,
                "text": f"Teks berhasil diekstrak dan diunggah ke Cloudinary dari {final_filename}.",
                "preview": preview,
                "url": file_url
            })

        except Exception as e:
            print(f"System: Gagal memproses file {filename}: {str(e)}")
            results.append({
                "status": "error",
                "filename": filename,
                "text": f"❌ Error: Gagal memproses file: {str(e)}"
            })

    return {"system_message": system_message, "results": results}

@router.post("/query/")
async def query(request: QueryRequest):
    try:
        answer, updated_history = query_rag(request.question, request.chat_history)
        return {"question": request.question, "answer": answer, "chat_history": updated_history}
    except Exception as e:
        print(f"System: Gagal memproses query RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal memproses query: {str(e)}")