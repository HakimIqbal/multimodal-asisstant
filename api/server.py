import os
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from api.models import llm, vector_store, process_document

app = FastAPI()

# Konfigurasi CORS agar API bisa diakses dari frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain frontend jika sudah ada
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path folder untuk upload dokumen
BASE_UPLOAD_FOLDER = "data-rag/documents"

# Mapping ekstensi file ke folder
FOLDER_MAP = {
    "pdf": "contoh-pdf",
    "docx": "contoh-docx",
    "jpg": "contoh-gambar",
    "jpeg": "contoh-gambar",
    "png": "contoh-gambar",
}

# Pastikan folder utama ada
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "API RAG + OCR is running!"}


@app.post("/upload-document/")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    Upload banyak dokumen (PDF, DOCX, atau Gambar) lalu proses dengan OCR & simpan ke FAISS.
    """
    responses = []
    
    for file in files:
        ext = file.filename.split(".")[-1].lower()  # Ambil ekstensi file
        folder_name = FOLDER_MAP.get(ext, "lainnya")  # Gunakan folder default jika tidak terdaftar
        upload_folder = os.path.join(BASE_UPLOAD_FOLDER, folder_name)

        # Pastikan folder target ada
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, file.filename)

        try:
            # Simpan file
            content = await file.read()  # Gunakan await untuk async
            with open(file_path, "wb") as f:
                f.write(content)

            # Proses dokumen dan simpan ke FAISS
            result = process_document(file_path)
            responses.append({file.filename: result})

        except Exception as e:
            responses.append({file.filename: f"Error: {str(e)}"})

    return {"status": "success", "results": responses}


@app.get("/search/")
async def search(query: str):
    """
    Mencari informasi dalam FAISS berdasarkan query.
    """
    if not vector_store:
        return {"error": "Vector store belum diinisialisasi"}

    docs = vector_store.similarity_search(query, k=3)
    results = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]

    return {"query": query, "results": results}


@app.post("/ask/")
async def ask_chatbot(query: str = Form(...)):
    """
    Query chatbot → Cari jawaban di FAISS + gunakan Mistral 7B untuk menyusun jawaban.
    """
    try:
        # Cari dokumen yang relevan di FAISS
        docs = vector_store.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Gabungkan pertanyaan dengan konteks
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"

        # Dapatkan jawaban dari LLM (Mistral 7B)
        response = llm(prompt)

        return {"query": query, "answer": response}

    except Exception as e:
        return {"error": f"Gagal memproses query: {str(e)}"}
